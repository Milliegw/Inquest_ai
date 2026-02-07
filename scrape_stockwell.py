"""
Scrape and download documents from the Stockwell Inquest archive.

This script downloads PDF/DOC files from the National Archives web archive
of the Stockwell Inquest website.

Uses Playwright to handle JavaScript challenges from the archive's WAF.
"""

import os
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright


PAGES = [
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235559/http://www.stockwellinquest.org.uk/index.htm",
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235630/http://www.stockwellinquest.org.uk/sitting_days/index.htm",
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235613/http://www.stockwellinquest.org.uk/hearing_transcripts/index.htm",
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
]

os.makedirs("downloads", exist_ok=True)


def download_file(page, file_url, local_path):
    """Download a file using Playwright's request context."""
    try:
        # Use the page's context to make the request (preserves cookies/session)
        response = page.request.get(file_url)
        if response.ok:
            with open(local_path, "wb") as f:
                f.write(response.body())
            print(f"  ✓ Downloaded: {local_path}")
            return True
        else:
            print(f"  ✗ Failed ({response.status}): {file_url}")
            return False
    except Exception as e:
        print(f"  ✗ Error downloading {file_url}: {e}")
        return False


def scrape_page(page, main_url):
    """Scrape a single page for document links and download them."""
    print(f"\nScanning: {main_url}")
    
    # Navigate and wait for the page to load
    page.goto(main_url, wait_until="networkidle", timeout=60000)
    
    # Wait a moment for any dynamic content
    time.sleep(2)
    
    # Get the page content
    content = page.content()
    
    # Check for iframe with archived content
    iframe = page.query_selector("iframe#replay_iframe")
    
    if iframe:
        # Get iframe source and navigate to it
        iframe_src = iframe.get_attribute("src")
        if iframe_src:
            print(f"  Found iframe, navigating to: {iframe_src}")
            page.goto(iframe_src, wait_until="networkidle", timeout=60000)
            time.sleep(2)
    
    # Find all document links
    links = page.query_selector_all("a[href]")
    doc_links = []
    
    for link in links:
        href = link.get_attribute("href")
        if href and href.lower().endswith((".pdf", ".doc", ".docx")):
            # Make absolute URL
            file_url = urljoin(page.url, href)
            doc_links.append(file_url)
    
    print(f"  Found {len(doc_links)} document links")
    
    # Download each document
    for file_url in doc_links:
        filename = os.path.basename(urlparse(file_url).path)
        # Clean up filename
        filename = filename.split("?")[0]  # Remove query params
        local_path = os.path.join("downloads", filename)
        
        if os.path.exists(local_path):
            print(f"  → Skipping (exists): {filename}")
            continue
            
        print(f"  Downloading: {filename}")
        download_file(page, file_url, local_path)


def main():
    with sync_playwright() as p:
        # Launch browser (headless by default)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            for main_url in PAGES:
                scrape_page(page, main_url)
        finally:
            browser.close()
    
    print("\n✓ Scraping complete!")


if __name__ == "__main__":
    main()