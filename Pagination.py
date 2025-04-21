import csv
import asyncio
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
joblisting={"is_job_listing": True, "score": 9.5, "has_pagination": True, "pagination_parent_container_selector": "nav#widget-jobsearch-results-pages", "next_page_element": {"text": ">", "href": "#", "selector": "a[aria-label='Go to the next page of results.']"}, "individual_job_links": [{"href": "/job/21872563/clinical-admin-assistant-beachwood-oh/", "text": "Clinical Admin Assistant", "selector": "a[href]"}, {"href": "/job/21872564/clinical-admin-assistant-beachwood-oh/", "text": "Clinical Admin Assistant", "selector": "a[href]"}, {"href": "/job/21872562/supply-chain-tech-i-beachwood-oh/", "text": "Supply Chain Tech I", "selector": "a[href]"}, {"href": "/job/21872561/carpenter-shaker-heights-oh/", "text": "Carpenter", "selector": "a[href]"}, {"href": "/job/21872560/maintenance-generalist-willoughby-oh/", "text": "Maintenance Generalist", "selector": "a[href]"}, {"href": "/job/21871626/clinical-pharmacist-parma-oh/", "text": "Clinical Pharmacist", "selector": "a[href]"}, {"href": "/job/21871625/intern-finance-grants-accounting-cleveland-oh/", "text": "Intern, Finance & Grants Accounting", "selector": "a[id]"}, {"href": "/job/21871624/social-worker-1-acute-adult-inpatient-beachwood-oh/", "text": "Social Worker 1 - Acute Adult Inpatient", "selector": "a[id]"}, {"href": "/job/21871623/clinical-pharmacist-ambulatory-infusion-center-cleveland-oh/", "text": "Clinical Pharmacist Ambulatory Infusion Center", "selector": "a[id]"}, {"href": "/job/21870721/speech-pathologist-adult-prn-willoughby-oh/", "text": "Speech Pathologist Adult PRN", "selector": "a[id]"}], "total_token_count": 129816}
config = {
    "base_url": "https://careers.uhhospitals.org",
    "start_path": "/job-search-results/",
    "output_filename": "uhhospitals_jobs.csv",
    "container_selector": joblisting.get('pagination_parent_container_selector'),  # Update this after inspecting
    "job_selector": joblisting.get('individual_job_links')[0].get('selector'),     # Update this after inspecting
    "next_button_selector": joblisting.get('next_page_element').get('selector'),
    "headless": True
}

async def scrape_jobs_to_dict(base_url: str, start_path: str, container_selector: str, job_selector: str, next_button_selector: str, output_filename: str, headless: bool = True):
    all_jobs = []
    page_count = 1
    full_url = urljoin(base_url, start_path)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(full_url)

        while True:
            print(f"Scraping Page {page_count} for: {start_path}")

            await page.wait_for_selector(container_selector, timeout=10000)
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            container = soup.select_one(container_selector)

            job_links = container.select(job_selector) if container else []
            for job in job_links:
                title = job.get_text(strip=True)
                href = job.get('href')
                print(href)
                if href:
                    job_url = urljoin(base_url, href)
                    all_jobs.append({"Title": title, "URL": job_url})

            next_btn = await page.query_selector(next_button_selector)
            if not next_btn or "disabled" in (await next_btn.get_attribute("class") or ""):
                break

            await next_btn.click()
            await page.wait_for_timeout(2000)
            page_count += 1

        await browser.close()

    # Save to CSV
    with open(output_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "URL"])
        writer.writeheader()
        writer.writerows(all_jobs)

    print(f"\n Done. Collected {len(all_jobs)} job listings.")
    print(f" Saved to: {output_filename}")



async def scrape_jobs_to_csv(cfg: dict):
    await scrape_jobs_to_dict(cfg['base_url'],cfg['start_path'],cfg['container_selector'],cfg['job_selector'],cfg['next_button_selector'],cfg['output_filename'])

if __name__ == "__main__":
    asyncio.run(scrape_jobs_to_csv(config))
