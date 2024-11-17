from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import json
import time
import socket
import logging
import os

class Crawler:
    def __init__(self, domain, max_links=3):

        
        
        self.domain = domain
        self.max_links = max_links
        self.visited = set([domain])
        self.queue = deque([domain])
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.error_count = 0
        self.link_count = 1
        self.link_duplicate_count = 0

        self.file_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = Path(os.path.join(self.file_folder_path,f"{urlparse(domain).netloc}"))
        self.folder_path.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join(self.file_folder_path,"crawler.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filemode="w"
        )

        logging.info(f"Initialized Crawler for domain: {domain}")

    def is_internet_connected(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except OSError:
            return False

    def fetch_page(self, url):
        while not self.is_internet_connected():
            logging.warning("Internet connection lost. Pausing crawl...")
            time.sleep(5)  # Wait before checking again

        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200 :
                if 'text/html' in response.headers['Content-Type']:
                    return response.text
                else:
                    logging.error(f"Error fetching {url}: Content Type {response.headers['Content-Type']}")
            else:
                logging.error(f"Error fetching {url}: Status Code {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
        self.error_count += 1
        return None

    def parse_links(self, html, base_url):
        soup = BeautifulSoup(html, 'lxml')
        for link in soup.find_all('a', href=True):
            raw_url = link['href']
            full_url = urljoin(base_url, raw_url)
            clean_url, _ = urldefrag(full_url)
            if urlparse(self.domain).netloc in urlparse(clean_url).netloc and self.is_unique_link(clean_url):
                self.queue.append(clean_url)

    def is_unique_link(self, link):
        self.link_count += 1
        if link in self.visited:
            self.link_duplicate_count += 1
            return False
        self.visited.add(link)
        return True

    def crawl(self):
        start_time = time.time()
        successful_crawls = 0
        while self.queue and successful_crawls < self.max_links:
            current_url = self.queue.popleft()
            logging.info(f"Crawling {successful_crawls + 1} of {self.max_links}: {current_url}")
            html_content = self.fetch_page(current_url)
            if html_content:
                with open(os.path.join(self.folder_path,f"{successful_crawls}.html"), "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)
                self.results.append({
                    "url": current_url,
                    "html_path": os.path.join(self.folder_path,f"{successful_crawls}.html")
                })
                successful_crawls += 1
                self.parse_links(html_content, current_url)
            time.sleep(1)
        total_time = time.time() - start_time
        logging.info(f"Crawling completed. Total time taken: {total_time:.2f} seconds.")
        return self.results

    def save_to_json(self, filename='output.json'):
        with open(os.path.join(self.folder_path,filename), 'w', encoding='utf-8') as json_file:
            json.dump(self.results, json_file, ensure_ascii=False, indent=4)
        logging.info(f"Saved results to {filename}")

if __name__ == "__main__":
    domain = input("Enter the domain (e.g., https://example.com/): ")
    crawler = Crawler(domain, max_links=10)
    crawled_data = crawler.crawl()
    crawler.save_to_json()
    logging.info(f"Crawled {len(crawled_data)} links from {domain}")
    logging.info(f"Percentage of duplicate links: {crawler.link_duplicate_count * 100 / crawler.link_count:.2f}%")
    logging.info(f"Number of Errors: {crawler.error_count}")
    logging.info(f"Number of enternal links in {domain}: {crawler.link_count}")
    logging.info(f"Number of elements in queue: {len(crawler.queue)}")
    logging.info(f"Number of duplicate links: {crawler.link_duplicate_count}")
