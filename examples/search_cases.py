"""Example: search federal court cases by query string.

Works in demo mode (no payment) for the /search endpoint.
For full access, set CLERK_AGENT_KEY in your env.
"""
import os
from clerk_api import ClerkClient

# Demo mode — no key required for /search.
# For paid endpoints, pass wallet_private_key (load from env, never hardcode).
client = ClerkClient(wallet_private_key=os.environ.get("CLERK_AGENT_KEY"))

# Search for cases involving a specific entity
cases = client.search("Binance", limit=10)

print(f"Found {len(cases)} cases:\n")
for case in cases:
    print(f"  {case['case_name']}")
    print(f"    {case['case_number']} · {case['court']} · filed {case['date_filed']}")
    if case.get("nature_of_suit"):
        print(f"    {case['nature_of_suit']}")
    print()
