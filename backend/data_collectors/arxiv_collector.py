import requests
import xml.etree.ElementTree as ET
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class ArxivCollector:
    """Collector for ArXiv research papers"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limit_delay = 3  # seconds between requests
        
    def search_papers(self, 
                     categories: List[str] = None,
                     max_results: int = 100,
                     start_date: str = "2023-01-01",
                     end_date: str = "2024-12-31",
                     sort_by: str = "submittedDate",
                     sort_order: str = "descending") -> List[Dict]:
        """
        Search ArXiv papers by categories and date range
        
        Args:
            categories: List of ArXiv categories (e.g., ['cs.AI', 'cs.LG'])
            max_results: Maximum number of results to fetch
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sort_by: Sort criteria (submittedDate, lastUpdatedDate, relevance)
            sort_order: Sort order (ascending, descending)
        """
        if categories is None:
            categories = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.MA']
            
        papers = []
        batch_size = 100  # ArXiv API limit per request
        
        for category in categories:
            logger.info(f"Fetching papers from category: {category}")
            
            # Build search query
            date_query = f"submittedDate:[{start_date.replace('-', '')} TO {end_date.replace('-', '')}]"
            search_query = f"cat:{category} AND {date_query}"
            
            # Fetch papers in batches
            start_idx = 0
            category_papers = []
            
            while start_idx < max_results and len(category_papers) < max_results:
                current_batch = min(batch_size, max_results - start_idx)
                
                params = {
                    'search_query': search_query,
                    'start': start_idx,
                    'max_results': current_batch,
                    'sortBy': sort_by,
                    'sortOrder': sort_order
                }
                
                try:
                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()
                    
                    batch_papers = self._parse_arxiv_response(response.text)
                    if not batch_papers:
                        break
                        
                    category_papers.extend(batch_papers)
                    start_idx += current_batch
                    
                    logger.info(f"Fetched {len(batch_papers)} papers, total: {len(category_papers)}")
                    
                    # Rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error fetching ArXiv papers: {e}")
                    break
                    
            papers.extend(category_papers[:max_results])
            
        logger.info(f"Total ArXiv papers collected: {len(papers)}")
        return papers
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse ArXiv API XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                paper = self._extract_paper_info(entry, namespaces)
                if paper:
                    papers.append(paper)
                    
        except ET.ParseError as e:
            logger.error(f"Error parsing ArXiv XML: {e}")
            
        return papers
    
    def _extract_paper_info(self, entry, namespaces: Dict) -> Optional[Dict]:
        """Extract paper information from XML entry"""
        try:
            # Basic information
            title = entry.find('atom:title', namespaces)
            title = title.text.strip().replace('\n', ' ') if title is not None else ""
            
            summary = entry.find('atom:summary', namespaces)
            abstract = summary.text.strip().replace('\n', ' ') if summary is not None else ""
            
            # ArXiv ID and URL
            arxiv_id = entry.find('atom:id', namespaces)
            arxiv_url = arxiv_id.text if arxiv_id is not None else ""
            arxiv_id = arxiv_url.split('/')[-1] if arxiv_url else ""
            
            # Authors
            authors = []
            for author in entry.findall('atom:author', namespaces):
                name = author.find('atom:name', namespaces)
                if name is not None:
                    authors.append(name.text.strip())
            
            # Publication date
            published = entry.find('atom:published', namespaces)
            pub_date = published.text if published is not None else ""
            
            updated = entry.find('atom:updated', namespaces)
            update_date = updated.text if updated is not None else ""
            
            # Categories
            categories = []
            for category in entry.findall('atom:category', namespaces):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # Primary category
            primary_category = entry.find('arxiv:primary_category', namespaces)
            primary_cat = primary_category.get('term') if primary_category is not None else ""
            
            # DOI
            doi = entry.find('arxiv:doi', namespaces)
            doi_value = doi.text if doi is not None else ""
            
            # Journal reference
            journal_ref = entry.find('arxiv:journal_ref', namespaces)
            journal = journal_ref.text if journal_ref is not None else ""
            
            paper = {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'arxiv_id': arxiv_id,
                'arxiv_url': arxiv_url,
                'published_date': pub_date,
                'updated_date': update_date,
                'categories': categories,
                'primary_category': primary_cat,
                'doi': doi_value,
                'journal_reference': journal,
                'source': 'arxiv',
                'document_type': 'research_paper',
                'content': f"{title}\n\nAuthors: {', '.join(authors)}\n\nAbstract: {abstract}",
                'metadata': {
                    'arxiv_id': arxiv_id,
                    'categories': categories,
                    'primary_category': primary_cat,
                    'authors_count': len(authors),
                    'published_year': pub_date[:4] if pub_date else "",
                    'doi': doi_value,
                    'journal': journal
                }
            }
            
            return paper
            
        except Exception as e:
            logger.error(f"Error extracting paper info: {e}")
            return None
    
    def get_paper_details(self, arxiv_id: str) -> Optional[Dict]:
        """Get detailed information for a specific ArXiv paper"""
        params = {
            'id_list': arxiv_id,
            'max_results': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            papers = self._parse_arxiv_response(response.text)
            return papers[0] if papers else None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ArXiv paper {arxiv_id}: {e}")
            return None
    
    def search_by_keywords(self, 
                          keywords: List[str],
                          max_results: int = 100,
                          categories: List[str] = None) -> List[Dict]:
        """Search papers by keywords"""
        if categories is None:
            categories = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV']
            
        papers = []
        
        for keyword in keywords:
            logger.info(f"Searching for keyword: {keyword}")
            
            # Build search query
            keyword_query = f'all:"{keyword}"'
            if categories:
                cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
                search_query = f"({keyword_query}) AND ({cat_query})"
            else:
                search_query = keyword_query
            
            params = {
                'search_query': search_query,
                'max_results': max_results // len(keywords),
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                
                keyword_papers = self._parse_arxiv_response(response.text)
                papers.extend(keyword_papers)
                
                logger.info(f"Found {len(keyword_papers)} papers for keyword: {keyword}")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error searching for keyword {keyword}: {e}")
                
        # Remove duplicates by ArXiv ID
        unique_papers = {}
        for paper in papers:
            arxiv_id = paper.get('arxiv_id')
            if arxiv_id and arxiv_id not in unique_papers:
                unique_papers[arxiv_id] = paper
                
        papers = list(unique_papers.values())
        logger.info(f"Total unique papers after deduplication: {len(papers)}")
        
        return papers

def collect_arxiv_papers(max_papers: int = 300) -> List[Dict]:
    """Main function to collect ArXiv papers"""
    collector = ArxivCollector()
    
    # Define research areas of interest
    categories = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.MA', 'cs.IR', 'cs.HC']
    keywords = [
        'large language models',
        'transformer neural networks',
        'graph neural networks',
        'retrieval augmented generation',
        'knowledge graphs',
        'multimodal learning',
        'reinforcement learning',
        'computer vision',
        'natural language processing'
    ]
    
    papers = []
    
    # Collect by categories (70% of papers)
    category_papers = collector.search_papers(
        categories=categories,
        max_results=int(max_papers * 0.7),
        start_date="2023-01-01",
        end_date="2024-12-31"
    )
    papers.extend(category_papers)
    
    # Collect by keywords (30% of papers)
    keyword_papers = collector.search_by_keywords(
        keywords=keywords,
        max_results=int(max_papers * 0.3),
        categories=categories
    )
    papers.extend(keyword_papers)
    
    # Remove duplicates
    unique_papers = {}
    for paper in papers:
        arxiv_id = paper.get('arxiv_id')
        if arxiv_id and arxiv_id not in unique_papers:
            unique_papers[arxiv_id] = paper
            
    final_papers = list(unique_papers.values())[:max_papers]
    
    logger.info(f"Collected {len(final_papers)} unique ArXiv papers")
    return final_papers

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    papers = collect_arxiv_papers(max_papers=50)  # Test with smaller number
    print(f"Collected {len(papers)} papers")
    if papers:
        print(f"Sample paper: {papers[0]['title']}")