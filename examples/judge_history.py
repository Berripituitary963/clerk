"""Example: look up a federal judge + their case history.

Useful when forecasting how a pending case might be decided based on the
presiding judge's prior rulings.

Requires CLERK_AGENT_KEY in env.
"""
import os
from clerk_api import ClerkClient

client = ClerkClient(wallet_private_key=os.environ["CLERK_AGENT_KEY"])

# Search judges by name
judges = client.judges("Alvin Hellerstein", limit=5)

print(f"Found {len(judges)} judges:\n")
for judge in judges:
    name = judge.get("name", "(unknown)")
    court = judge.get("court", "")
    appointed = judge.get("date_appointed", "")
    print(f"  {name}")
    print(f"    {court} · appointed {appointed}")
    if judge.get("bio"):
        print(f"    {judge['bio'][:160]}...")
    print()
