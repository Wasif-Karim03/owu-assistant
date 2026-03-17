import asyncio
import logging

import httpx
from bs4 import BeautifulSoup
import html2text

logger = logging.getLogger(__name__)

OWU_SEED_URLS: list[str] = [
    # ── Top-level pages ───────────────────────────────────────────
    "https://www.owu.edu/about/",
    "https://www.owu.edu/academics/",
    "https://www.owu.edu/admission/",
    "https://www.owu.edu/student-life/",
    "https://www.owu.edu/current-students/",
    "https://www.owu.edu/about/fast-facts/",
    "https://www.owu.edu/about/mission-aims/",
    "https://www.owu.edu/campus-map/",

    # ── Offices & Services Directory (verified from sitemap) ──────
    "https://www.owu.edu/about/offices-services-directory/",
    "https://www.owu.edu/about/offices-services-directory/academic-advising/",
    "https://www.owu.edu/about/offices-services-directory/counseling-services/",
    "https://www.owu.edu/about/offices-services-directory/information-services/",
    "https://www.owu.edu/about/offices-services-directory/international-off-campus-programs-iocp/",
    "https://www.owu.edu/about/offices-services-directory/residential-life-and-dining-services/",
    "https://www.owu.edu/about/offices-services-directory/sagan-academic-resource-center/",
    "https://www.owu.edu/about/offices-services-directory/student-engagement-and-success/",
    "https://www.owu.edu/about/offices-services-directory/student-health-center/",
    "https://www.owu.edu/about/offices-services-directory/student-involvement-office/",
    "https://www.owu.edu/about/offices-services-directory/office-of-multicultural-student-affairs/",
    "https://www.owu.edu/about/offices-services-directory/office-of-student-integrity-community-standards/",

    # ── Registrar ─────────────────────────────────────────────────
    "https://www.owu.edu/academics/office-of-the-registrar/",
    "https://www.owu.edu/academics/office-of-the-registrar/add-drop-and-withdrawal/",
    "https://www.owu.edu/academics/office-of-the-registrar/forms/",
    "https://www.owu.edu/academics/academic-resources/academic-calendar/",
    "https://www.owu.edu/academics/departments-programs/",
    "https://www.owu.edu/academics/commencement-week/",
    "https://www.owu.edu/academics/commencement-week/frequently-asked-questions-faq/",
    "https://www.owu.edu/academics/the-owu-connection/",
    "https://www.owu.edu/academics/academic-resources/",

    # ── Financial Aid & Tuition (verified URLs from sitemap) ──────
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/tuition-expenses/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/types-of-financial-aid/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/merit-based-scholarships/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/need-based-grants/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/outside-grants-scholarships/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/policies-procedures/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/returning-students/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/international-students/",
    "https://www.owu.edu/admission/financial-aid-scholarships-tuition/loans/",

    # ── Admission ─────────────────────────────────────────────────
    "https://www.owu.edu/admission/apply/",
    "https://www.owu.edu/admission/apply/first-year-students/",
    "https://www.owu.edu/admission/transfer-students/",
    "https://www.owu.edu/admission/transfer-students/frequently-asked-questions/",
    "https://www.owu.edu/admission/apply/international-students/",
    "https://www.owu.edu/admission/visit/",
    "https://www.owu.edu/admission/meet-your-admission-team/",
    "https://www.owu.edu/admission/why-owu/",
    "https://www.owu.edu/admission/graduate-outcomes/",
    "https://www.owu.edu/admission/contact-us/",

    # ── Student Life ──────────────────────────────────────────────
    "https://www.owu.edu/student-life/health-wellness/",
    "https://www.owu.edu/student-life/department-of-public-safety/",
    "https://www.owu.edu/student-life/department-of-public-safety/parking/",
    "https://www.owu.edu/student-life/department-of-public-safety/emergency-information/",
    "https://www.owu.edu/student-life/department-of-public-safety/area-transportation/",
    "https://www.owu.edu/student-life/student-organizations/",
    "https://www.owu.edu/student-life/fraternity-sorority-life/",
    "https://www.owu.edu/student-life/fitness-recreation/",
    "https://www.owu.edu/student-life/the-arts/",

    # ── New Student / FAQ pages ───────────────────────────────────
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/academics-support/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/after-choosing-owu/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/amenities/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/before-you-arrive/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/bills-insurance-books/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/campus-activities-career-connection/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/campus-traditions/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/computer-support/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/food-dining/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/rooms-roommates/",
    "https://www.owu.edu/becoming-a-bishop/frequently-asked-questions/safety-security-maintenance/",
    "https://www.owu.edu/becoming-a-bishop/housing-information/forms/",
    "https://www.owu.edu/becoming-a-bishop/orientation-programs/camp-oh-wooo/",

    # ── Career Connection (careers.owu.edu) ───────────────────────
    "https://careers.owu.edu/",
    "https://careers.owu.edu/channels/faculty-and-staff/",
    "https://careers.owu.edu/resources/category/discover/",
    "https://careers.owu.edu/resources/category/prepare/",
    "https://careers.owu.edu/resources/category/launch/",

    # ── Title IX & Policies ───────────────────────────────────────
    "https://www.owu.edu/about/title-ix-sexual-misconduct-and-the-clery-act/",
    "https://www.owu.edu/about/title-ix-sexual-misconduct-and-the-clery-act/reporting-resources/",

    # ── Library ───────────────────────────────────────────────────
    "https://www.owu.edu/owu-library-services/",

    # ── OWU Hours & Help ──────────────────────────────────────────
    "https://www.owu.edu/owu-hours/",
    "https://www.owu.edu/help/",
    "https://www.owu.edu/forms/",
]

_STRIP_TAGS = {"nav", "footer", "script", "style", "header", "noscript", "aside", "iframe"}

_CONTENT_SELECTORS = [
    {"id": "page-content"},
    {"class_": "entry-content"},
    {"class_": "page-content"},
    {"role": "main"},
    "main",
    "article",
    {"id": "content"},
    {"class_": "content-area"},
]


def _extract_content(soup: BeautifulSoup) -> str:
    """Try multiple selectors to find the best content block, then convert
    to markdown.  Falls back to the full ``<body>`` if nothing else works."""

    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    target = None
    for selector in _CONTENT_SELECTORS:
        if isinstance(selector, str):
            target = soup.find(selector)
        else:
            target = soup.find(**selector)
        if target and len(target.get_text(strip=True)) > 150:
            break
        target = None

    if target is None:
        target = soup.find("body") or soup

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    raw = converter.handle(str(target))

    lines = raw.splitlines()
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        if stripped.startswith(("Skip to", "Current Students", "Faculty &", "Alumni &",
                                "Parents &", "Visit Apply Give", "Calendars News")):
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()


async def scrape_url(url: str) -> dict:
    """Fetch a single URL and return cleaned markdown content."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "OWU-Assistant-Bot/1.0"})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    content = _extract_content(soup)

    return {"title": title, "content": content, "url": url}


async def scrape_owu_pages(urls: list[str] | None = None) -> list[dict]:
    """Scrape a list of URLs (defaults to OWU_SEED_URLS) sequentially."""
    targets = urls or OWU_SEED_URLS
    results: list[dict] = []

    for url in targets:
        try:
            page = await scrape_url(url)
            if len(page["content"]) > 100:
                results.append(page)
                logger.info("[ok] %s  (%d chars)", url, len(page["content"]))
            else:
                logger.warning("[skip] %s  (too short: %d chars)", url, len(page["content"]))
        except Exception as exc:
            logger.warning("[FAIL] %s  — %s", url, exc)
        await asyncio.sleep(0.3)

    return results
