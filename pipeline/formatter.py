"""Assemble generated section content into the final markdown document.

This is provided for you and works as-is; you shouldn't need to change it. It turns the list
of generated sections into a single document. If you want a different output format, this is
where it would live.
"""


def format_document(config: dict, sections: list[dict]) -> str:
    """sections is a list of {"title": str, "content": str} in document order."""
    lines: list[str] = [f"# {config.get('document_title', 'Advice Report')}", ""]
    for section in sections:
        title = section.get("title", "").strip()
        if title:
            lines.append(f"## {title}")
            lines.append("")
        lines.append(section.get("content", "").strip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
