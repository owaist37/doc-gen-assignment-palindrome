"""Generate an advice report for a client from the template config.

Usage:
    python -m agent_pipeline.generate --client client_01_clean
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent_pipeline.accounts import build_holdings_table, format_accounts, load_accounts
from document_formatter.formatting import format_document
from document_formatter.loading import read_file


class ReportGenerator:
    """Builds a report one section at a time from the template config."""

    def __init__(self, openai_client: OpenAI, model: str) -> None:
        self._openai = openai_client
        self._model = model

    def generate(self, config: dict, context: str, precomputed: dict[str, str] | None = None) -> str:
        instructions = config.get("global_instructions", "")
        sections = []
        for section in config["sections"]:
            if not self._section_applies(section, context, instructions):
                continue
            sections.append(
                {
                    "title": section.get("title", ""),
                    "content": self._build_section(section, context, instructions, precomputed),
                }
            )
        return format_document(config, sections)

    def _section_applies(self, section: dict, context: str, instructions: str) -> bool:
        rule = section.get("use_if", "always")
        if rule == "always":
            return True
        verdict = self._ask(
            f"{instructions}\n\n"
            f"Decide whether this section applies to the client.\n"
            f"Rule: {rule}\n"
            f"Reply with only 'yes' or 'no'.",
            context,
        )
        return verdict.lower().startswith("y")

    def _build_section(
        self,
        section: dict,
        context: str,
        instructions: str,
        precomputed: dict[str, str] | None = None,
    ) -> str:
        content = section["template"]
        for name, spec in section.get("placeholders", {}).items():
            baseline = (precomputed or {}).get(name)
            if baseline:
                prompt = (
                    f"{instructions}\n\n"
                    f"Baseline (built deterministically from the account database, "
                    f"valuation dates shown in the account data above):\n\n"
                    f"{baseline}\n\n"
                    f"{spec['prompt']}"
                )
            else:
                prompt = f"{instructions}\n\n{spec['prompt']}"
            value = self._ask(prompt, context)
            content = content.replace(f"<<{name}>>", value)
        return content

    def _ask(self, instruction: str, context: str) -> str:
        response = self._openai.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "user", "content": f"{context}\n\n---\n\n{instruction}"}
            ],
        )
        return response.choices[0].message.content.strip()


def read_client_context(client_dir: Path, filenames: list[str]) -> str:
    """Read the named files from the client folder and concatenate them into one context string."""
    parts = []
    for name in filenames:
        if name == "client_data_db.json":
            db_path = client_dir / name
            db = json.loads(db_path.read_text(encoding="utf-8"))
            content = format_accounts(db["snapshot_date"], load_accounts(db_path))
        else:
            content = read_file(client_dir / name)
        parts.append(f"=== {name} ===\n{content}")
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an advice report for a client."
    )
    parser.add_argument("--client", required=True, help="folder name under data/")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument(
        "--config", type=Path, default=Path("config/template_config.json")
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    load_dotenv()
    generator = ReportGenerator(OpenAI(), os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))

    config = json.loads(args.config.read_text(encoding="utf-8"))
    client_dir = args.data_dir / args.client
    db_path = client_dir / "client_data_db.json"

    filenames = sorted(path.name for path in client_dir.iterdir() if path.is_file())
    context = read_client_context(client_dir, filenames)

    precomputed: dict[str, str] = {}
    if db_path.exists():
        precomputed["holdings_table"] = build_holdings_table(load_accounts(db_path))

    report = generator.generate(config, context, precomputed)

    client_num = "_".join(args.client.split("_")[:2])
    baseline_dir = args.output_dir / f"{client_num}_baseline"
    if not baseline_dir.exists():
        run_dir = baseline_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        run_dir = args.output_dir / f"{client_num}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / f"{args.client}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")

    if db_path.exists():
        db = json.loads(db_path.read_text(encoding="utf-8"))
        accounts_json = format_accounts(db["snapshot_date"], load_accounts(db_path))
        accounts_path = run_dir / "accounts.json"
        accounts_path.write_text(accounts_json, encoding="utf-8")
        print(f"Wrote {accounts_path}")


if __name__ == "__main__":
    main()
