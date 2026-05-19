"""Example: look up an entity (company or person) across federal courts.

Useful for compliance + risk research: "has this issuer been sued?"

Requires CLERK_AGENT_KEY in env (or 1B+ $CLERK held by that wallet for free tier).
"""
import os
from clerk_api import ClerkClient

client = ClerkClient(wallet_private_key=os.environ["CLERK_AGENT_KEY"])

# Look up an entity by name
parties = client.parties("Coinbase", limit=10)

print(f"Found {len(parties)} parties:\n")
for party in parties:
    name = party.get("name", "(unknown)")
    case_count = party.get("case_count", "?")
    role = party.get("role", "")
    print(f"  {name} — {case_count} cases · {role}")
