import re

from bs4 import BeautifulSoup
import html2text


def _clean_html(raw: str) -> str:
    """If the input looks like HTML, convert it to plain text."""
    if "<html" in raw.lower() or "<body" in raw.lower() or "<div" in raw.lower():
        soup = BeautifulSoup(raw, "html.parser")
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0
        return converter.handle(str(soup)).strip()
    return raw.strip()


def parse_owu_daily(raw_email_text: str, email_date: str) -> dict:
    """Parse an OWU Daily digest email into a structured document dict.

    Keeps clear section breaks so that the chunker can split each
    event/announcement into its own chunk for better retrieval.
    """
    cleaned = _clean_html(raw_email_text)

    lines = cleaned.split("\n")
    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.isupper() and len(stripped) > 3:
            if current:
                sections.append("\n".join(current))
                current = []
            current.append(stripped)
        else:
            current.append(stripped)

    if current:
        sections.append("\n".join(current))

    content = "\n\n".join(sections)

    return {
        "title": f"OWU Daily - {email_date}",
        "content": content,
        "source_type": "email",
        "metadata": {
            "date": email_date,
            "type": "daily_digest",
        },
    }
