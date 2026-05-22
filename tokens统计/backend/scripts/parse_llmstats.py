"""
Parse llm-stats.com homepage HTML to extract LLM STATS scores.
Usage: python scripts/parse_llmstats.py [path_to_html]
"""
import re
import sys

def parse_html(html: str) -> list[dict]:
    """Extract model name, LLM STATS score, and category scores from HTML."""
    results = []

    # Pattern: the table rows contain model name (with embedded provider),
    # followed by LLM Stats score, then category scores
    # Each row's first data cell after rank contains: ModelNameProvider

    # Look for self.__next_f.push patterns (RSC data)
    rsc_pattern = r'self\.__next_f\.push\(\[1,"([^"]*(?:\\.|[^"\\])*)"\]\)'
    rsc_matches = re.findall(rsc_pattern, html)
    print(f"Found {len(rsc_matches)} RSC data chunks")

    # Try to find structured data in the RSC payloads
    for i, chunk in enumerate(rsc_matches[:5]):
        if 'llmStats' in chunk or 'overall' in chunk.lower():
            print(f"\nRSC chunk {i} (first 500 chars):")
            print(chunk[:500])

    # Look for any JSON-like structures with model data
    # The RSC data uses escaped JSON
    for chunk in rsc_matches:
        # Unescape the chunk
        try:
            unescaped = chunk.encode().decode('unicode_escape')
        except:
            unescaped = chunk

        if 'llmStats' in unescaped or 'Claude Mythos' in unescaped:
            print(f"\nRelevant RSC chunk found (first 1000 chars):")
            print(unescaped[:1000])
            break

    return results

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/llmstats_home.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    print(f"HTML size: {len(html)} bytes")
    parse_html(html)
