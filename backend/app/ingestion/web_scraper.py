import asyncio

import httpx
from bs4 import BeautifulSoup
import html2text

OWU_SEED_URLS: list[str] = [
    # ── Main landing pages ────────────────────────────────────────
    "https://www.owu.edu/about/",
    "https://www.owu.edu/academics/",
    "https://www.owu.edu/admission/",
    "https://www.owu.edu/student-life/",
    "https://www.owu.edu/campus-resources/",
    "https://www.owu.edu/the-owu-connection/",

    # ── Academics & Registrar ─────────────────────────────────────
    "https://www.owu.edu/academics/registrar/",
    "https://www.owu.edu/academics/academic-calendar/",
    "https://www.owu.edu/academics/academic-advising/",
    "https://www.owu.edu/academics/departments-programs/",
    "https://www.owu.edu/academics/study-abroad/",
    "https://www.owu.edu/academics/libraries/",
    "https://www.owu.edu/academics/honors-and-scholars/",
    "https://www.owu.edu/academics/office-of-the-registrar/schedules/",
    "https://www.owu.edu/academics/office-of-the-registrar/forms/",

    # ── Financial Aid & Tuition ───────────────────────────────────
    "https://www.owu.edu/academics/financial-aid/",
    "https://www.owu.edu/admission/tuition-and-financial-aid/",
    "https://www.owu.edu/admission/tuition-and-financial-aid/merit-based-scholarships/",
    "https://www.owu.edu/admission/tuition-and-financial-aid/types-of-aid/",
    "https://www.owu.edu/admission/tuition-and-financial-aid/cost-of-attendance/",

    # ── Student Life ──────────────────────────────────────────────
    "https://www.owu.edu/student-life/health-wellness/",
    "https://www.owu.edu/student-life/health-wellness/counseling-services/",
    "https://www.owu.edu/student-life/campus-life/",
    "https://www.owu.edu/student-life/student-accounts/",
    "https://www.owu.edu/student-life/housing-residential-life/",
    "https://www.owu.edu/student-life/dining-services/",
    "https://www.owu.edu/student-life/student-involvement/",
    "https://www.owu.edu/student-life/student-involvement/student-organizations/",
    "https://www.owu.edu/student-life/campus-safety/",
    "https://www.owu.edu/student-life/diversity-equity-inclusion/",
    "https://www.owu.edu/student-life/dean-of-students/",
    "https://www.owu.edu/student-life/new-student-orientation/",

    # ── Campus Resources ──────────────────────────────────────────
    "https://www.owu.edu/campus-resources/iocp/",
    "https://www.owu.edu/campus-resources/it-services/",
    "https://www.owu.edu/campus-resources/library/",
    "https://www.owu.edu/campus-resources/international-student-services/",
    "https://www.owu.edu/campus-resources/writing-center/",
    "https://www.owu.edu/campus-resources/sagan-academic-resource-center/",
    "https://www.owu.edu/campus-resources/accessibility-services/",

    # ── Admission details ─────────────────────────────────────────
    "https://www.owu.edu/admission/apply/",
    "https://www.owu.edu/admission/apply/first-year-students/",
    "https://www.owu.edu/admission/apply/transfer-students/",
    "https://www.owu.edu/admission/apply/international-students/",
    "https://www.owu.edu/admission/visit/",
    "https://www.owu.edu/admission/meet-your-admission-team/",

    # ── Athletics ─────────────────────────────────────────────────
    "https://www.owu.edu/about/athletics/",
    "https://bishops.owu.edu/",

    # ── OWU Connection / Experiential Learning ────────────────────
    "https://www.owu.edu/the-owu-connection/theory-to-practice-grants/",
    "https://www.owu.edu/the-owu-connection/travel-learning-courses/",
    "https://www.owu.edu/the-owu-connection/community-service-and-service-learning/",

    # ── Alumni & Campus Info ──────────────────────────────────────
    "https://www.owu.edu/about/offices-services-directory/",
    "https://www.owu.edu/about/campus-map/",
    "https://www.owu.edu/about/quick-facts/",
]

_STRIP_TAGS = {"nav", "footer", "script", "style", "header", "noscript", "aside"}


async def scrape_url(url: str) -> dict:
    """Fetch a single URL and return cleaned markdown content."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "OWU-Assistant-Bot/1.0"})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    main_content = soup.find("main") or soup.find(id="content") or soup.find("article")
    target = main_content if main_content else soup

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    content = converter.handle(str(target))

    return {"title": title, "content": content.strip(), "url": url}


async def scrape_owu_pages(urls: list[str] | None = None) -> list[dict]:
    """Scrape a list of URLs (defaults to OWU_SEED_URLS) sequentially so we
    don't hammer the server."""
    targets = urls or OWU_SEED_URLS
    results: list[dict] = []

    for url in targets:
        try:
            page = await scrape_url(url)
            if len(page["content"]) > 100:
                results.append(page)
                print(f"  [ok] {url}  ({len(page['content'])} chars)")
            else:
                print(f"  [skip] {url}  (too short: {len(page['content'])} chars)")
        except Exception as exc:
            print(f"  [FAIL] {url}  — {exc}")
        await asyncio.sleep(0.5)

    return results
