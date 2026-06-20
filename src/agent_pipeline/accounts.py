"""Load and flatten client account data from a DB JSON file.

Produces one record per account_id, resolving joint ownership to real names
and falling back to older non-null values when the newest record has gaps.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def load_accounts(db_path: Path) -> list[dict]:
    """Return a deduplicated, flat list of accounts from a client DB JSON file."""
    data = json.loads(db_path.read_text(encoding="utf-8"))
    snapshot_date = data["snapshot_date"]
    holders = data["holders"]

    holder_names: list[str] = [h["name"] for h in holders.values()]

    tagged: list[dict] = []
    for holder in holders.values():
        for account in holder["accounts"]:
            tagged.append({**account, "_snapshot_date": snapshot_date, "_holder_name": holder["name"]})

    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in tagged:
        grouped[record["account_id"]].append(record)

    accounts: list[dict] = []
    for account_id, records in grouped.items():
        records.sort(
            key=lambda r: (r["_snapshot_date"] or "0000-00-00", r["valuation_date"] or "0000-00-00"),
            reverse=True,
        )
        base = dict(records[0])

        for field in ("value", "valuation_date"):
            if base.get(field) is None:
                for older in records[1:]:
                    if older.get(field) is not None:
                        base[field] = older[field]
                        break

        is_joint = any(r["owner"] == "Joint" for r in records)
        if is_joint:
            owner = " and ".join(dict.fromkeys(holder_names))
            owner_type = "joint"
        else:
            owner = base["owner"]
            owner_type = "single"

        accounts.append({
            "account_id": account_id,
            "platform": base.get("platform"),
            "type": base.get("type"),
            "owner": owner,
            "owner_type": owner_type,
            "status": base.get("status"),
            "value": base.get("value"),
            "currency": base.get("currency"),
            "valuation_date": base.get("valuation_date"),
        })

    return accounts


def format_accounts(snapshot_date: str, accounts: list[dict]) -> str:
    return json.dumps({"snapshot_date": snapshot_date, "accounts": accounts}, indent=2)


def build_holdings_table(accounts: list[dict], snapshot_date: str | None = None) -> str:
    """Return a deterministic markdown table with columns Account | Owner | Type | Value."""
    from datetime import date as _date
    lines = [
        "| Account | Owner | Type | Value |",
        "|---------|-------|------|-------|"
    ]
    for acc in accounts:
        owner = "Joint" if acc.get("owner_type") == "joint" else (acc.get("owner") or "—")
        value = acc.get("value")
        val_date = acc.get("valuation_date")
        value_str = f"£{value:,.2f}" if value is not None else "—"
        if snapshot_date and val_date and val_date != snapshot_date:
            parsed = _date.fromisoformat(val_date)
            value_str += f" (valued {parsed.strftime('%-d %b %Y')})"
        lines.append(
            f"| {acc.get('account_id', '—')} | {owner} | {acc.get('type', '—')} | {value_str} |"
        )
    return "\n".join(lines)


ISA_ANNUAL_ALLOWANCE = 20_000


def build_isa_headroom(accounts: list[dict], annual_allowance: int = ISA_ANNUAL_ALLOWANCE) -> str:
    """Return a formatted summary of ISA subscription headroom per open ISA account."""
    isa_accounts = [
        a for a in accounts
        if "ISA" in (a.get("type") or "") and a.get("status") == "open"
    ]
    if not isa_accounts:
        return ""
    lines = [
        f"ISA annual subscription limit: £{annual_allowance:,} per person per tax year.",
        "Headroom available (assumes no contributions made in the current tax year):",
    ]
    for acc in isa_accounts:
        lines.append(f"  - {acc['account_id']} ({acc['owner']}): £{annual_allowance:,}")
    return "\n".join(lines)
