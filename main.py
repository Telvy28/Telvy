#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for the web scraping project.
"""

import os
import argparse
from scraper.utils import setup_logging
from scraper.amazon_scraper import AmazonScraper

# Definir el directorio de trabajo
os.chdir(r'D:\Estudios_extra\Big_Data_Python\Aplicando_WEB_SCRAPING')
print(f"Directorio de trabajo actual: {os.getcwd()}")

def main():
    """Main function to run the scraper."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Web Scraping Project')
    parser.add_argument('--site', type=str, help='Site to scrape (amazon, etc.)')
    parser.add_argument('--keyword', type=str, help='Keyword to search for')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages to scrape')
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info(f"Directorio de trabajo: {os.getcwd()}")
    logger.info("Starting web scraper")
    
    # Run the appropriate scraper
    if args.site and args.site.lower() == 'amazon':
        logger.info(f"Running Amazon scraper")
        scraper = AmazonScraper()
        keyword = args.keyword or 'laptop'  # Default keyword if none provided
        logger.info(f"Searching for '{keyword}' on Amazon")
        results = scraper.search_products(keyword, max_pages=args.pages)
        if results:
            scraper.save_results(results, f"amazon_{keyword.replace(' ', '_')}.csv")
    else:
        logger.info("No site specified or site not supported")
        logger.info("Supported sites: amazon")
        logger.info("Example usage: python main.py --site amazon --keyword 'gaming laptop' --pages 2")

if __name__ == "__main__":
    main()
