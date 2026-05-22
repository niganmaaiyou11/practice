export interface TokenUsage {
  id: number
  date: string
  model_name: string
  provider: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  notes: string | null
  user_id?: number
  source?: string | null
  created_at: string
}

export interface TokenUsageCreate {
  date: string
  model_name: string
  provider: string
  input_tokens: number
  output_tokens: number
  notes?: string | null
}

export interface TokenUsageUpdate {
  date?: string
  model_name?: string
  provider?: string
  input_tokens?: number
  output_tokens?: number
  notes?: string | null
}

export interface PaginatedResponse {
  records: TokenUsage[]
  total: number
}

export interface DailySummary {
  date: string
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  record_count: number
}

export interface ModelBreakdown {
  model_name: string
  provider: string
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  record_count: number
}

export interface ProviderBreakdown {
  provider: string
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  record_count: number
}

export interface Totals {
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  record_count: number
}

export interface FilterParams {
  start_date?: string
  end_date?: string
  provider?: string
}

export interface RecordQueryParams extends FilterParams {
  skip?: number
  limit?: number
  model_name?: string
}

export interface User {
  id: number
  email: string
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
  captcha_token: string
}

export interface RegisterRequest {
  email: string
  password: string
  captcha_token: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface CaptchaChallenge {
  token: string
}

export interface ProviderEntry {
  id: string
  name: string
  color: string
  models: string[]
}

export interface ModelsRegistry {
  providers: ProviderEntry[]
  updated_at: string | null
  source?: string
}

// ── Leaderboard ──────────────────────────────────────────

export interface LeaderboardEntry {
  id: number
  model_slug: string
  model_name: string
  provider: string
  organization: string | null
  overall_score: number | null
  rank_overall: number | null
  score_gpqa: number | null
  score_mmlu: number | null
  score_mmlu_pro: number | null
  score_math: number | null
  score_humaneval: number | null
  score_swebench: number | null
  score_coding_arena: number | null
  score_reasoning: number | null
  score_coding: number | null
  score_knowledge: number | null
  score_tool_use: number | null
  score_long_context: number | null
  score_vision: number | null
  category_math_score: number | null
  category_writing_score: number | null
  methodology_version: string | null
  tokens_per_second: number | null
  price_input: number | null
  price_output: number | null
  context_window: number | null
  max_output_tokens: number | null
  knowledge_cutoff: string | null
  modalities: string | null
  tags: string | null
  fetched_at: string
  category: string | null
  arena_rating: number | null
  output_resolution: string | null
  latency: number | null
}

export interface LeaderboardPaginatedResponse {
  entries: LeaderboardEntry[]
  total: number
}

export interface LeaderboardSummary {
  total_models: number
  total_providers: number
  avg_overall_score: number | null
  avg_price_input: number | null
  avg_tokens_per_second: number | null
  last_fetched_at: string | null
  methodology_version: string | null
}

export interface LeaderboardQueryParams {
  skip?: number
  limit?: number
  provider?: string
  search?: string
  sort_by?: string
  sort_dir?: 'asc' | 'desc'
  china_only?: boolean
  tags?: string
  modality?: string
}

// ── Email Sync ──────────────────────────────────────────

export interface EmailAccount {
  id: number
  email_address: string
  provider_type: string
  sync_enabled: boolean
  sync_interval_minutes: number
  last_synced_at: string | null
  monitored_providers: string | null
  created_at: string
}

export interface EmailAccountCreate {
  provider_type: string
  email_address: string
  imap_server?: string | null
  imap_username?: string | null
  imap_password?: string | null
  sync_interval_minutes?: number
  monitored_providers?: string[]
}

export interface EmailAccountUpdate {
  sync_enabled?: boolean
  sync_interval_minutes?: number
  monitored_providers?: string[]
}

export interface SyncResult {
  ok: boolean
  emails_fetched: number
  emails_parsed: number
  records_created: number
  errors: string[]
  sync_log_id?: number | null
  status?: string  // "running" | "success" | "error"
}

export interface SyncLog {
  id: number
  email_account_id: number
  started_at: string
  finished_at: string | null
  status: string
  emails_fetched: number
  emails_parsed: number
  records_created: number
  error_message: string | null
}

export interface PaginatedSyncLogs {
  logs: SyncLog[]
  total: number
}

export interface EmailAccountStatusItem {
  account_id: number
  email_address: string
  provider_type: string
  sync_enabled: boolean
  last_synced_at: string | null
  last_sync_status: string | null
  total_synced_emails: number
}

export interface SyncStatus {
  total_accounts: number
  active_accounts: number
  last_global_sync: string | null
  total_synced_emails: number
  total_synced_records: number
  accounts: EmailAccountStatusItem[]
}

export interface OAuthURL {
  url: string
}

export interface IMAPTestRequest {
  imap_server: string
  imap_username: string
  imap_password: string
}

export interface IMAPTestResponse {
  ok: boolean
  message: string
}

export interface EmailPreviewItem {
  message_id: string
  subject: string
  from_addr: string
  date: string | null
  provider: string
  model_name: string | null
  input_tokens: number | null
  output_tokens: number | null
  parsed: boolean
  body_snippet: string | null
}

export interface PreviewResponse {
  emails_fetched: number
  emails_parsed: number
  records_would_create: number
  items: EmailPreviewItem[]
}
