# import requests
# from bs4 import BeautifulSoup

# PAGES = [
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235559/http://www.stockwellinquest.org.uk/index.htm",
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235630/http://www.stockwellinquest.org.uk/sitting_days/index.htm",
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235613/http://www.stockwellinquest.org.uk/hearing_transcripts/index.htm",
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
# ]

# for page_url in PAGES:
#     print(f"\nScanning: {page_url}")
#     response = requests.get(page_url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     for link in soup.find_all("a", href=True):
#         href = link["href"]
#         if href.lower().endswith((".pdf", ".doc", ".docx")):
#             # Make sure the link is absolute
#             if not href.startswith("http"):
#                 # Combine with base page URL
#                 from urllib.parse import urljoin
#                 href = urljoin(page_url, href)
#             print(href)

# for page_url in PAGES:
#     print(f"\nScanning: {page_url}")
#     response = requests.get(page_url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     print("All links found on this page:")
#     for link in soup.find_all("a", href=True):
#         print(link["href"])


# import requests
# from bs4 import BeautifulSoup

# PAGES = [
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235559/http://www.stockwellinquest.org.uk/index.htm",
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235630/http://www.stockwellinquest.org.uk/sitting_days/index.htm",
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235613/http://www.stockwellinquest.org.uk/hearing_transcripts/index.htm",
#     "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
# ]

# for page_url in PAGES:
#     print(f"\nScanning: {page_url}")
#     response = requests.get(page_url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     # Print all frame and iframe sources
#     for frame in soup.find_all(['frame', 'iframe'], src=True):
#         print("Frame source found:", frame['src'])

# import requests
# from bs4 import BeautifulSoup

# page_url = "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
# response = requests.get(page_url)
# print(response.text)  # Print the raw HTML

# import requests
# from bs4 import BeautifulSoup

# page_url = "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
# response = requests.get(page_url)
# print("Status code:", response.status_code)
# print("Headers:", response.headers)
# print("Content length:", len(response.content))
# print(response.text)

# import requests
# from bs4 import BeautifulSoup

# headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
# }
# page_url = "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
# response = requests.get(page_url, headers=headers)
# print("Status code:", response.status_code)
# print("Content length:", len(response.content))
# print(response.text)

# import requests
# from bs4 import BeautifulSoup

# headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
# }
# main_url = "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
# response = requests.get(main_url, headers=headers)
# soup = BeautifulSoup(response.content, "html.parser")

# iframe = soup.find("iframe", id="replay_iframe")
# if iframe and iframe.has_attr("src"):
#     iframe_url = iframe["src"]
#     print("Fetching iframe content from:", iframe_url)
#     iframe_response = requests.get(iframe_url, headers=headers)
#     iframe_soup = BeautifulSoup(iframe_response.content, "html.parser")
#     # Print all document links
#     for link in iframe_soup.find_all("a", href=True):
#         href = link["href"]
#         if href.lower().endswith((".pdf", ".doc", ".docx")):
#             print(href)
# else:
#     print("No iframe found!")

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

PAGES = [
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235559/http://www.stockwellinquest.org.uk/index.htm",
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235630/http://www.stockwellinquest.org.uk/sitting_days/index.htm",
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235613/http://www.stockwellinquest.org.uk/hearing_transcripts/index.htm",
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20090317235617/http://www.stockwellinquest.org.uk/directions_decs/index.htm"
]

os.makedirs("downloads", exist_ok=True)

for main_url in PAGES:
    print(f"\nScanning: {main_url}")
    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    iframe = soup.find("iframe", id="replay_iframe")
    if iframe and iframe.has_attr("src"):
        iframe_url = iframe["src"]
        print("Fetching iframe content from:", iframe_url)
        iframe_response = requests.get(iframe_url, headers=headers)
        iframe_soup = BeautifulSoup(iframe_response.content, "html.parser")
        for link in iframe_soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().endswith((".pdf", ".doc", ".docx")):
                # Make absolute URL if needed
                file_url = urljoin(iframe_url, href)
                filename = os.path.basename(urlparse(file_url).path)
                local_path = os.path.join("downloads", filename)
                print(f"Downloading {file_url} -> {local_path}")
                try:
                    file_resp = requests.get(file_url, headers=headers)
                    with open(local_path, "wb") as f:
                        f.write(file_resp.content)
                except Exception as e:
                    print(f"Failed to download {file_url}: {e}")
    else:
        print("No iframe found!")