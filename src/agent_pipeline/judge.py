"""LLM judge for generated advice reports.

Usage:
    # Judge a single run folder
    python -m agent_pipeline.judge --path outputs/client_03_202606201418

    # Judge every run folder under a directory
    python -m agent_pipeline.judge --path outputs
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent_pipeline.accounts import build_isa_headroom, load_accounts
from agent_pipeline.generate import read_client_context


_VERDICT_SCHEMA = """\
Return JSON with this exact shape (no other keys):
{
  "conforms": true | false,
  "errors": [
    {
      "description": "...",
      "severity": "low" | "medium" | "high",
      "recommended_fix": "..."
    }
  ]
}
If there are no errors, return "errors": [].
"""


class ReportJudge:
    def __init__(self, openai_client: OpenAI, model: str, config: dict) -> None:
        self._openai = openai_client
        self._model = model
        self._config = config
        self._global_instructions = config.get("global_instructions", "")

    # ------------------------------------------------------------------
    # LLM helpers
    # ------------------------------------------------------------------

    def _ask_json(self, instruction: str, context: str) -> dict:
        """Call the LLM expecting JSON. Returns fallback error dict on failure."""
        try:
            response = self._openai.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": f"{context}\n\n---\n\n{instruction}"}],
            )
            return json.loads(response.choices[0].message.content.strip())
        except Exception as exc:
            return {
                "conforms": False,
                "errors": [{
                    "description": f"Judge call failed: {exc}",
                    "severity": "low",
                    "recommended_fix": "Re-run the judge.",
                }],
            }

    def _ask_yes_no(self, instruction: str, context: str) -> bool:
        try:
            response = self._openai.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": f"{context}\n\n---\n\n{instruction}"}],
            )
            return response.choices[0].message.content.strip().lower().startswith("y")
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Judgement calls
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_placeholder_errors(result: dict) -> dict:
        """Drop errors that flag the intentional <<insert value here>> placeholder."""
        marker = "<<insert value here>>"
        kept = [
            e for e in result.get("errors", [])
            if marker not in e.get("description", "") and marker not in e.get("recommended_fix", "")
        ]
        return {"conforms": len(kept) == 0, "errors": kept}

    def judge_global(self, report_text: str, context: str) -> dict:
        """Check the whole report against global_instructions."""
        instruction = (
            f"You are evaluating a generated financial advice report.\n\n"
            f"The report was generated with these global instructions:\n"
            f"{self._global_instructions}\n\n"
            f"The full report text is:\n\n{report_text}\n\n"
            f"Check the report for any violations of the global instructions. "
            f"Common violations: use of first-person singular ('I', 'me', 'my'), "
            f"non-British English spelling, extra headings or commentary that should "
            f"not be present, or unprofessional tone.\n\n"
            f"IMPORTANT: This is a draft report. Any occurrence of '<<insert value here>>' "
            f"is intentional — it marks a figure that could not be derived from the source "
            f"documents and must be filled in by the adviser. Do NOT flag these as errors.\n\n"
            f"{_VERDICT_SCHEMA}"
        )
        return self._ask_json(instruction, context)

    def judge_section(self, section_cfg: dict, section_content: str, context: str) -> dict:
        """Check one section's content against its template and placeholder prompts."""
        placeholders = section_cfg.get("placeholders", {})
        placeholder_prompts = "\n\n".join(
            f"Placeholder <<{name}>>:\n{spec['prompt']}"
            for name, spec in placeholders.items()
        )
        template = section_cfg.get("template", "")

        instruction = (
            f"You are evaluating the '{section_cfg['title']}' section of a generated "
            f"financial advice report.\n\n"
            f"Global instructions that applied when this section was generated:\n"
            f"{self._global_instructions}\n\n"
            f"Section template (<<placeholder>> slots were filled by the LLM):\n"
            f"{template}\n\n"
        )
        if placeholder_prompts:
            instruction += (
                f"Instructions given to the LLM for each placeholder:\n"
                f"{placeholder_prompts}\n\n"
            )
        instruction += (
            f"The generated section content is:\n\n{section_content}\n\n"
            f"Identify any errors where the content fails to follow the instructions "
            f"or contains factual inconsistencies with the client source data. "
            f"Look for: missing required information, incorrect figures, wrong account "
            f"names, violation of guardrail rules (e.g. using approximate figures when "
            f"precision is required, double-counting funds, mentioning tax when prohibited), "
            f"or structural problems.\n\n"
            f"IMPORTANT: This is a draft report. Any occurrence of '<<insert value here>>' "
            f"is intentional — it marks a figure that could not be derived from the source "
            f"documents and must be filled in by the adviser. Do NOT flag these as errors.\n\n"
            f"{_VERDICT_SCHEMA}"
        )
        return self._ask_json(instruction, context)

    def _check_use_if(self, section_cfg: dict, is_present: bool, context: str) -> bool:
        """Returns True if there is a presence/absence mismatch for a conditional section."""
        rule = section_cfg.get("use_if", "always")
        if rule == "always":
            return False
        instruction = (
            f"{self._global_instructions}\n\n"
            f"Decide whether this section applies to the client.\n"
            f"Rule: {rule}\n"
            f"Reply with only 'yes' or 'no'."
        )
        should_be_present = self._ask_yes_no(instruction, context)
        return should_be_present != is_present

    # ------------------------------------------------------------------
    # Report parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_report_sections(report_text: str) -> dict[str, str]:
        """Return {section_title: content} by splitting on '## ' headings."""
        parts = re.split(r"^## (.+)$", report_text, flags=re.MULTILINE)
        # parts = [preamble, title1, content1, title2, content2, ...]
        result: dict[str, str] = {}
        for i in range(1, len(parts) - 1, 2):
            result[parts[i].strip()] = parts[i + 1].strip()
        return result

    # ------------------------------------------------------------------
    # Main entry point per run
    # ------------------------------------------------------------------

    def judge_run(self, run_dir: Path, data_dir: Path) -> dict:
        """Judge one output run folder. Returns a metrics dict (empty on skip)."""
        md_files = [
            f for f in run_dir.iterdir()
            if f.suffix == ".md" and f.stem != "judge_report"
        ]
        if not md_files:
            print(f"  [skip] No report .md in {run_dir}")
            return {}

        report_path = md_files[0]
        client_name = report_path.stem  # e.g. client_03_hard

        client_dir = data_dir / client_name
        if not client_dir.exists():
            print(f"  [skip] Data folder not found: {client_dir}")
            return {}

        # Rebuild source context exactly as the generator did
        db_path = client_dir / "client_data_db.json"
        filenames = sorted(p.name for p in client_dir.iterdir() if p.is_file())
        context = read_client_context(client_dir, filenames)
        if db_path.exists():
            accounts = load_accounts(db_path)
            isa_headroom = build_isa_headroom(accounts)
            if isa_headroom:
                context += f"\n\n=== isa_headroom ===\n{isa_headroom}"

        report_text = report_path.read_text(encoding="utf-8")
        sections_by_title = self.parse_report_sections(report_text)

        # Global check
        global_result = self._filter_placeholder_errors(self.judge_global(report_text, context))
        print(f"  Global rules: {len(global_result.get('errors', []))} error(s)")

        # Per-section checks
        section_results: dict[str, dict] = {}
        for section_cfg in self._config["sections"]:
            sid = section_cfg["id"]
            title = section_cfg["title"]
            is_present = title in sections_by_title

            use_if_mismatch = self._check_use_if(section_cfg, is_present, context)

            if is_present:
                result = self._filter_placeholder_errors(
                    self.judge_section(section_cfg, sections_by_title[title], context)
                )
                if use_if_mismatch:
                    result["errors"].insert(0, {
                        "description": "Section is present but should not be included per the use_if rule.",
                        "severity": "high",
                        "recommended_fix": "Remove this section from the report.",
                    })
                    result["conforms"] = False
            else:
                if use_if_mismatch:
                    result = {
                        "conforms": False,
                        "errors": [{
                            "description": "Required section is missing from the report.",
                            "severity": "high",
                            "recommended_fix": (
                                f"Add the '{title}' section — it should be included "
                                f"per the rule: {section_cfg['use_if']}"
                            ),
                        }],
                    }
                else:
                    # Correctly absent optional section
                    result = {"conforms": True, "errors": []}

            section_results[sid] = result
            print(f"  {title}: {len(result.get('errors', []))} error(s)")

        self._write_judge_report(run_dir, client_name, global_result, section_results)

        metrics: dict = {
            "judged_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "run_dir": str(run_dir),
            "client": client_name,
            "model": self._model,
            "global_rule_errors": len(global_result.get("errors", [])),
        }
        for section_cfg in self._config["sections"]:
            sid = section_cfg["id"]
            metrics[f"{sid}_errors"] = len(section_results.get(sid, {}).get("errors", []))
        metrics["total_errors"] = sum(v for k, v in metrics.items() if k.endswith("_errors"))
        return metrics

    def _write_judge_report(
        self,
        run_dir: Path,
        client_name: str,
        global_result: dict,
        section_results: dict[str, dict],
    ) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        global_errors = global_result.get("errors", [])

        lines: list[str] = [
            "# Judge Report",
            "",
            f"**Client:** {client_name}  ",
            f"**Run:** {run_dir.name}  ",
            f"**Model:** {self._model}  ",
            f"**Judged at:** {now}",
            "",
            "---",
            "",
            "## Global Rules",
            "",
            f"**Errors:** {len(global_errors)}",
            "",
        ]
        for err in global_errors:
            lines.append(f"- **[{err.get('severity', '?').upper()}]** {err.get('description', '')}")
            lines.append(f"  - *Fix:* {err.get('recommended_fix', '')}")
        lines.append("")

        for section_cfg in self._config["sections"]:
            sid = section_cfg["id"]
            title = section_cfg["title"]
            result = section_results.get(sid, {"conforms": True, "errors": []})
            errors = result.get("errors", [])
            lines += [
                f"## Section: {title}",
                "",
                f"**Errors:** {len(errors)}",
                "",
            ]
            for err in errors:
                lines.append(f"- **[{err.get('severity', '?').upper()}]** {err.get('description', '')}")
                lines.append(f"  - *Fix:* {err.get('recommended_fix', '')}")
            lines.append("")

        # Summary table
        total = len(global_errors) + sum(
            len(section_results.get(s["id"], {}).get("errors", []))
            for s in self._config["sections"]
        )
        lines += [
            "---",
            "",
            "## Error Count Summary",
            "",
            "| Section | Errors |",
            "|---------|--------|",
            f"| Global Rules | {len(global_errors)} |",
        ]
        for section_cfg in self._config["sections"]:
            sid = section_cfg["id"]
            count = len(section_results.get(sid, {}).get("errors", []))
            lines.append(f"| {section_cfg['title']} | {count} |")
        lines.append(f"| **Total** | **{total}** |")
        lines.append("")

        out_path = run_dir / "judge_report.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Wrote {out_path}")


# ------------------------------------------------------------------
# CLI helpers
# ------------------------------------------------------------------

def _find_run_dirs(path: Path) -> list[Path]:
    """Return run directories to judge. path can be a single run or a parent dir."""
    if path.is_dir():
        has_report = any(
            f.suffix == ".md" and f.stem != "judge_report" for f in path.iterdir()
        )
        if has_report:
            return [path]
        runs = []
        for sub in sorted(path.iterdir()):
            if sub.is_dir() and any(
                f.suffix == ".md" and f.stem != "judge_report" for f in sub.iterdir()
            ):
                runs.append(sub)
        return runs
    return []


def _csv_path_for(path: Path) -> Path:
    """Locate run_metrics.csv: next to run folders (parent dir), or alongside a single run."""
    has_report = path.is_dir() and any(
        f.suffix == ".md" and f.stem != "judge_report" for f in path.iterdir()
    )
    return (path.parent if has_report else path) / "run_metrics.csv"


def _append_metrics_row(csv_path: Path, metrics: dict, section_ids: list[str]) -> None:
    fieldnames = [
        "judged_at", "run_dir", "client", "model", "global_rule_errors",
        *[f"{sid}_errors" for sid in section_ids],
        "total_errors",
    ]
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({k: metrics.get(k, 0) for k in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM judge for generated advice reports.")
    parser.add_argument(
        "--path", type=Path, required=True,
        help="A single run folder or a parent directory containing run folders.",
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--config", type=Path, default=Path("config/template_config.json"))
    args = parser.parse_args()

    load_dotenv()
    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    section_ids = [s["id"] for s in config["sections"]]

    judge = ReportJudge(client, model, config)
    run_dirs = _find_run_dirs(args.path)

    if not run_dirs:
        print(f"No run folders found under {args.path}")
        return

    csv_path = _csv_path_for(args.path)

    for run_dir in run_dirs:
        print(f"\nJudging {run_dir.name} ...")
        metrics = judge.judge_run(run_dir, args.data_dir)
        if metrics:
            _append_metrics_row(csv_path, metrics, section_ids)
            print(f"  Total errors: {metrics['total_errors']}")

    print(f"\nMetrics written to {csv_path}")


if __name__ == "__main__":
    main()
