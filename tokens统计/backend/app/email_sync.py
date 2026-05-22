from __future__ import annotations
import json
import logging
from datetime import datetime, timedelta, timezone, date

from sqlalchemy.orm import Session

from app.models import EmailAccount, SyncedEmail, SyncLog, TokenUsage
from app.email_auth import decrypt_token
from app.email_fetcher import fetch_messages, PROVIDER_TO_DOMAINS
from app.email_parser import get_parser_for_sender, ParsedUsageData

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("email_sync")


async def run_sync_for_account(account_id: int, db: Session, sync_log_id: int | None = None) -> SyncLog:
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    if not account:
        raise ValueError(f"EmailAccount {account_id} not found")

    if sync_log_id:
        sync_log = db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
        if not sync_log:
            sync_log = SyncLog(
                email_account_id=account.id,
                started_at=datetime.now(timezone.utc),
                status="running",
            )
            db.add(sync_log)
            db.commit()
            db.refresh(sync_log)
    else:
        sync_log = SyncLog(
            email_account_id=account.id,
            started_at=datetime.now(timezone.utc),
            status="running",
        )
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)

    try:
        # Determine time range — first sync goes back 30 days
        since = account.last_synced_at or (datetime.now(timezone.utc) - timedelta(days=30))

        # Get monitored providers
        monitored = None
        if account.monitored_providers:
            try:
                monitored = json.loads(account.monitored_providers)
            except json.JSONDecodeError:
                pass

        logger.info(
            "Sync account %d (%s) since=%s providers=%s",
            account.id, account.email_address,
            since.strftime("%Y-%m-%d") if since else "any",
            monitored or "all",
        )

        # Fetch emails (auto-routes to Gmail API or IMAP based on account.provider_type)
        emails = await fetch_messages(account, since=since, monitored_providers=monitored)
        sync_log.emails_fetched = len(emails)
        logger.info("Fetched %d candidate emails for account %d", len(emails), account.id)

        debug_msgs: list[str] = []
        skipped_dedup = 0
        skipped_no_parser = 0
        skipped_no_tokens = 0
        skipped_provider_filter = 0
        # Track which providers sent emails but had no parser match
        unmatched_senders: dict[str, int] = {}

        for email_data in emails:
            msg_id = email_data["message_id"]
            email_subject = email_data.get("subject", "")[:100]
            email_from = email_data.get("from", "")[:80]

            # Dedup check
            existing = db.query(SyncedEmail).filter(
                SyncedEmail.email_account_id == account.id,
                SyncedEmail.message_id == msg_id,
            ).first()
            if existing:
                skipped_dedup += 1
                continue

            # Match parser by sender
            parser = get_parser_for_sender(email_data.get("from", ""))
            parsed: ParsedUsageData | None = None
            provider = "Unknown"
            parser_name = type(parser).__name__ if parser else "None"

            if parser:
                parsed = parser.parse(email_data)
            if parsed:
                provider = parsed.provider

            # Skip if monitored_providers is set and parsed provider doesn't match
            if monitored and provider != "Unknown":
                matched = any(
                    provider.lower() == mp.lower()
                    or any(d in email_data.get("from", "").lower()
                           for d in PROVIDER_TO_DOMAINS.get(mp, []))
                    for mp in monitored
                )
                if not matched:
                    skipped_provider_filter += 1
                    debug_msgs.append(
                        f"SKIP provider: from={email_from} subject={email_subject} "
                        f"parsed_provider={provider} parser={parser_name}"
                    )
                    continue

            # Log what we found
            if not parsed:
                skipped_no_tokens += 1
                # Extract domain for tracking unmatched senders
                try:
                    domain = email_from.rsplit("@", 1)[-1].rstrip(">")
                    unmatched_senders[domain] = unmatched_senders.get(domain, 0) + 1
                except Exception:
                    pass
                debug_msgs.append(
                    f"NO_MATCH: from={email_from} subject={email_subject} "
                    f"parser={parser_name}"
                )
                # Still save as synced email record (without token data)
                synced = SyncedEmail(
                    email_account_id=account.id,
                    message_id=msg_id,
                    provider=provider,
                    email_date=email_data.get("date", datetime.now(timezone.utc)),
                    subject=email_data.get("subject", ""),
                    parsed_data=None,
                    token_usage_id=None,
                )
                db.add(synced)
                continue

            sync_log.emails_parsed += 1
            logger.info(
                "Parsed: provider=%s model=%s input=%s output=%s from=%s",
                parsed.provider, parsed.model_name,
                parsed.input_tokens, parsed.output_tokens,
                email_from,
            )

            # Create TokenUsage record if we got token data
            token_usage_id = None
            if parsed.input_tokens or parsed.output_tokens:
                try:
                    usage_date = date.fromisoformat(parsed.usage_date)
                except (ValueError, TypeError):
                    usage_date = email_data["date"].date() if email_data.get("date") else date.today()

                # Create a record for the main parsed data
                record = TokenUsage(
                    date=usage_date,
                    model_name=parsed.model_name or "unknown",
                    provider=parsed.provider,
                    input_tokens=parsed.input_tokens or 0,
                    output_tokens=parsed.output_tokens or 0,
                    total_tokens=(parsed.input_tokens or 0) + (parsed.output_tokens or 0),
                    user_id=account.user_id,
                    source="email_sync",
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                token_usage_id = record.id
                sync_log.records_created += 1

                # Also create records for additional models found
                for m in parsed.all_models[1:]:
                    m_total = m.get("total_tokens", 0)
                    m_input = m.get("input_tokens", 0)
                    m_output = m.get("output_tokens", 0)
                    if not m_input and not m_output and m_total:
                        m_input = m_total
                    m_record = TokenUsage(
                        date=usage_date,
                        model_name=m["model_name"],
                        provider=parsed.provider,
                        input_tokens=m_input,
                        output_tokens=m_output,
                        total_tokens=m_total or m_input + m_output,
                        user_id=account.user_id,
                        source="email_sync",
                    )
                    db.add(m_record)
                    db.commit()
                    sync_log.records_created += 1

            # Save synced email record
            synced = SyncedEmail(
                email_account_id=account.id,
                message_id=msg_id,
                provider=provider,
                email_date=email_data.get("date", datetime.now(timezone.utc)),
                subject=email_data.get("subject", ""),
                parsed_data=json.dumps({
                    "model_name": parsed.model_name,
                    "input_tokens": parsed.input_tokens,
                    "output_tokens": parsed.output_tokens,
                    "usage_date": parsed.usage_date,
                    "all_models": parsed.all_models,
                }) if parsed else None,
                token_usage_id=token_usage_id,
            )
            db.add(synced)

        # Update account
        account.last_synced_at = datetime.now(timezone.utc)

        # Build result summary
        summary_parts = [
            f"emails_fetched={len(emails)}",
            f"emails_parsed={sync_log.emails_parsed}",
            f"records_created={sync_log.records_created}",
            f"skipped_dedup={skipped_dedup}",
            f"skipped_no_match={skipped_no_tokens}",
        ]
        if monitored:
            summary_parts.append(f"skipped_provider_filter={skipped_provider_filter}")
        if unmatched_senders:
            top_unmatched = sorted(unmatched_senders.items(), key=lambda x: -x[1])[:5]
            summary_parts.append(f"top_unmatched_senders={top_unmatched}")
        if debug_msgs:
            summary_parts.append("debug(first5): " + " | ".join(debug_msgs[:5]))
        # Add helpful hint when no emails were found
        if len(emails) == 0:
            summary_parts.append(
                "HINT: No AI provider emails found in the last 30 days. "
                "Make sure AI providers send usage reports to this email, "
                "or check provider filter settings."
            )

        sync_log.error_message = "; ".join(summary_parts)
        sync_log.status = "success"
        logger.info("Sync complete for account %d: %s", account.id, sync_log.error_message)

    except Exception as e:
        logger.exception(f"Sync failed for account {account_id}")
        sync_log.status = "error"
        sync_log.error_message = f"ERROR: {e}"

    sync_log.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sync_log)
    return sync_log
