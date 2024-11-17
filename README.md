# Python Web Crawler

This is a Python-based web crawler designed to scrape and store webpages from a specified domain. The crawler ensures it stays within the domain, saves the fetched HTML files locally, and logs key crawling statistics.

## Features

- Fetches HTML content from a specified domain.
- Stores HTML pages in a structured folder hierarchy.
- Logs crawling progress and errors in a `crawler.log` file.
- Avoids duplicate links and handles relative URLs.
- Respects network disconnections by pausing and retrying.
- Outputs results in a JSON file for easy data handling.

## Requirements

- Python 3.7+
- Internet connection

## Dependencies


Install the dependencies using pip:

```bash
pip install -r requirements.txt
