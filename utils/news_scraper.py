import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_google_news(self, company_name: str, num_articles: int = 10) -> List[str]:
        """
        Search Google News for articles about the given company.
        
        Args:
            company_name: Name of the company to search for
            num_articles: Number of articles to retrieve
            
        Returns:
            List of URLs to news articles
        """
        search_url = f"https://www.google.com/search?q={company_name}+news&tbm=nws"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_links = []
            
            # Find all search results
            result_divs = soup.find_all('div', class_='SoaBEf')
            
            for div in result_divs:
                if len(article_links) >= num_articles:
                    break
                
                # Find the link in the search result
                link_elem = div.find('a')
                if link_elem and 'href' in link_elem.attrs:
                    url = link_elem['href']
                    # Google search results have URLs in the format "/url?q=<actual_url>"
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    # Skip JavaScript-heavy websites that are difficult to scrape
                    if not self._is_js_heavy_site(url):
                        article_links.append(url)
            
            return article_links[:num_articles]
        
        except Exception as e:
            print(f"Error searching for news: {e}")
            return []
    
    def _is_js_heavy_site(self, url: str) -> bool:
        """
        Check if a website is likely to be JavaScript-heavy and difficult to scrape.
        
        Args:
            url: URL to check
            
        Returns:
            True if the site is JS-heavy, False otherwise
        """
        # List of domains that are known to be JS-heavy
        js_heavy_domains = [
            'bloomberg.com',
            'wsj.com',
            'ft.com',
            'nytimes.com',
            'washingtonpost.com'
        ]
        
        return any(domain in url for domain in js_heavy_domains)
    
    def extract_article_content(self, url: str) -> Dict[str, Any]:
        """
        Extract title and content from a news article.
        
        Args:
            url: URL of the article
            
        Returns:
            Dictionary containing article title and content
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ''
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.text.strip()
            
            # Extract article content
            # First try to find article content in common containers
            content = ''
            article_elem = soup.find('article') or soup.find('div', class_=re.compile(r'article|content|story')) 
            
            if article_elem:
                # Get all paragraphs from the article element
                paragraphs = article_elem.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs])
            else:
                # Fallback: get all paragraphs from the body
                paragraphs = soup.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs])
            
            # Clean up the content
            content = re.sub(r'\s+', ' ', content).strip()
            
            return {
                'title': title,
                'content': content,
                'url': url
            }
        
        except Exception as e:
            print(f"Error extracting article content from {url}: {e}")
            return {
                'title': '',
                'content': '',
                'url': url
            }