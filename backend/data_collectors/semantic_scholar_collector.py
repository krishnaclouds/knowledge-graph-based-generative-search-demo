import requests
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

class SemanticScholarCollector:
    """Collector for academic papers from Semantic Scholar API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.rate_limit_delay = 1  # seconds between requests
        
        self.headers = {
            'User-Agent': 'KnowledgeGraph-RAG-Demo'
        }
        
        if self.api_key:
            self.headers['x-api-key'] = self.api_key
            logger.info("Semantic Scholar API key configured")
        else:
            logger.warning("No Semantic Scholar API key - using public tier (lower rate limits)")
    
    def search_papers(self, 
                     query: str,
                     max_results: int = 100,
                     year_range: Optional[str] = "2022-2024",
                     min_citations: int = 5,
                     fields: Optional[List[str]] = None) -> List[Dict]:
        """Search for papers using Semantic Scholar API"""
        
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'authors', 'year', 'citationCount',
                'referenceCount', 'venue', 'publicationTypes', 'publicationDate',
                'journal', 'doi', 'url', 'tldr', 'fieldsOfStudy'
            ]
        
        papers = []
        offset = 0
        limit = 100  # API limit per request
        
        while len(papers) < max_results:
            params = {
                'query': query,
                'offset': offset,
                'limit': min(limit, max_results - len(papers)),
                'fields': ','.join(fields)
            }
            
            if year_range:
                params['year'] = year_range
            
            try:
                response = requests.get(
                    f"{self.base_url}/paper/search",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                batch_papers = data.get('data', [])
                
                if not batch_papers:
                    break
                
                # Filter by citation count
                filtered_papers = []
                for paper in batch_papers:
                    if paper.get('citationCount', 0) >= min_citations:
                        parsed_paper = self._parse_paper(paper)
                        if parsed_paper:
                            filtered_papers.append(parsed_paper)
                
                papers.extend(filtered_papers)
                logger.info(f"Fetched {len(filtered_papers)} papers (filtered from {len(batch_papers)}), total: {len(papers)}")
                
                offset += len(batch_papers)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error searching papers: {e}")
                break
        
        logger.info(f"Total papers collected from search: {len(papers)}")
        return papers[:max_results]
    
    def get_paper_details(self, paper_id: str, fields: Optional[List[str]] = None) -> Optional[Dict]:
        """Get detailed information for a specific paper"""
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'authors', 'year', 'citationCount',
                'referenceCount', 'venue', 'publicationTypes', 'publicationDate',
                'journal', 'doi', 'url', 'tldr', 'fieldsOfStudy', 'citations', 'references'
            ]
        
        try:
            params = {'fields': ','.join(fields)}
            response = requests.get(
                f"{self.base_url}/paper/{paper_id}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            paper_data = response.json()
            return self._parse_paper(paper_data, include_relations=True)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching paper {paper_id}: {e}")
            return None
    
    def get_author_papers(self, author_id: str, max_papers: int = 50) -> List[Dict]:
        """Get papers by a specific author"""
        try:
            params = {
                'fields': 'paperId,title,abstract,year,citationCount,venue,doi',
                'limit': max_papers
            }
            
            response = requests.get(
                f"{self.base_url}/author/{author_id}/papers",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for paper_data in data.get('data', []):
                paper = self._parse_paper(paper_data)
                if paper:
                    papers.append(paper)
            
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching papers for author {author_id}: {e}")
            return []
    
    def collect_ai_papers(self, max_papers: int = 300) -> List[Dict]:
        """Collect papers related to AI and machine learning"""
        search_queries = [
            "large language models",
            "transformer neural networks", 
            "deep learning computer vision",
            "natural language processing",
            "reinforcement learning",
            "graph neural networks",
            "knowledge graphs machine learning",
            "retrieval augmented generation",
            "multimodal learning",
            "artificial intelligence ethics",
            "neural architecture search",
            "federated learning",
            "few-shot learning",
            "self-supervised learning",
            "contrastive learning"
        ]
        
        all_papers = []
        papers_per_query = max_papers // len(search_queries)
        
        for query in search_queries:
            logger.info(f"Searching for: {query}")
            
            papers = self.search_papers(
                query=query,
                max_results=papers_per_query,
                year_range="2022-2024",
                min_citations=10
            )
            
            all_papers.extend(papers)
            
            # Rate limiting between queries
            time.sleep(self.rate_limit_delay * 2)
        
        # Remove duplicates by paper ID
        unique_papers = {}
        for paper in all_papers:
            paper_id = paper.get('paper_id')
            if paper_id and paper_id not in unique_papers:
                unique_papers[paper_id] = paper
        
        final_papers = list(unique_papers.values())[:max_papers]
        logger.info(f"Collected {len(final_papers)} unique AI papers")
        
        return final_papers
    
    def collect_citation_network(self, seed_paper_ids: List[str], max_depth: int = 2) -> List[Dict]:
        """Collect papers through citation network expansion"""
        collected_papers = {}
        to_process = [(pid, 0) for pid in seed_paper_ids]  # (paper_id, depth)
        
        while to_process:
            paper_id, depth = to_process.pop(0)
            
            if paper_id in collected_papers or depth > max_depth:
                continue
            
            # Get paper details with citations and references
            paper = self.get_paper_details(paper_id)
            if paper:
                collected_papers[paper_id] = paper
                logger.info(f"Collected paper at depth {depth}: {paper['title'][:60]}...")
                
                # Add references and citations for next level
                if depth < max_depth:
                    # Add references (papers this paper cites)
                    for ref in paper.get('references', [])[:5]:  # Limit to top 5
                        ref_id = ref.get('paperId')
                        if ref_id and ref_id not in collected_papers:
                            to_process.append((ref_id, depth + 1))
                    
                    # Add citations (papers that cite this paper)
                    for cite in paper.get('citations', [])[:5]:  # Limit to top 5
                        cite_id = cite.get('paperId')
                        if cite_id and cite_id not in collected_papers:
                            to_process.append((cite_id, depth + 1))
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        papers = list(collected_papers.values())
        logger.info(f"Collected {len(papers)} papers through citation network")
        return papers
    
    def _parse_paper(self, paper_data: Dict, include_relations: bool = False) -> Optional[Dict]:
        """Parse paper data from Semantic Scholar API response"""
        try:
            # Extract authors
            authors = []
            author_ids = []
            if paper_data.get('authors'):
                for author in paper_data['authors']:
                    name = author.get('name')
                    if name:
                        authors.append(name)
                        if author.get('authorId'):
                            author_ids.append(author['authorId'])
            
            # Extract venue information
            venue = ""
            if paper_data.get('venue'):
                venue = paper_data['venue']
            elif paper_data.get('journal') and paper_data['journal'].get('name'):
                venue = paper_data['journal']['name']
            
            # Extract fields of study
            fields_of_study = []
            if paper_data.get('fieldsOfStudy'):
                fields_of_study = paper_data['fieldsOfStudy']
            
            # Build content
            content_parts = [
                f"Title: {paper_data.get('title', '')}",
                f"Authors: {', '.join(authors)}",
            ]
            
            if paper_data.get('abstract'):
                content_parts.append(f"Abstract: {paper_data['abstract']}")
            
            if paper_data.get('tldr') and paper_data['tldr'].get('text'):
                content_parts.append(f"TL;DR: {paper_data['tldr']['text']}")
            
            if venue:
                content_parts.append(f"Venue: {venue}")
            
            paper = {
                'paper_id': paper_data.get('paperId'),
                'title': paper_data.get('title', ''),
                'authors': authors,
                'author_ids': author_ids,
                'abstract': paper_data.get('abstract', ''),
                'year': paper_data.get('year'),
                'citation_count': paper_data.get('citationCount', 0),
                'reference_count': paper_data.get('referenceCount', 0),
                'venue': venue,
                'doi': paper_data.get('doi'),
                'url': paper_data.get('url'),
                'publication_date': paper_data.get('publicationDate'),
                'publication_types': paper_data.get('publicationTypes', []),
                'fields_of_study': fields_of_study,
                'tldr': paper_data.get('tldr', {}).get('text', '') if paper_data.get('tldr') else '',
                'source': 'semantic_scholar',
                'document_type': 'research_paper',
                'content': '\n\n'.join(content_parts),
                'metadata': {
                    'paper_id': paper_data.get('paperId'),
                    'citation_count': paper_data.get('citationCount', 0),
                    'reference_count': paper_data.get('referenceCount', 0),
                    'year': paper_data.get('year'),
                    'venue': venue,
                    'authors_count': len(authors),
                    'fields_of_study': fields_of_study,
                    'publication_types': paper_data.get('publicationTypes', []),
                    'doi': paper_data.get('doi'),
                    'has_abstract': bool(paper_data.get('abstract')),
                    'has_tldr': bool(paper_data.get('tldr', {}).get('text'))
                }
            }
            
            # Add citation and reference information if available
            if include_relations:
                if paper_data.get('citations'):
                    paper['citations'] = [
                        {
                            'paperId': cite.get('paperId'),
                            'title': cite.get('title'),
                            'authors': [a.get('name') for a in cite.get('authors', []) if a.get('name')]
                        }
                        for cite in paper_data['citations'][:10]  # Limit to first 10
                    ]
                
                if paper_data.get('references'):
                    paper['references'] = [
                        {
                            'paperId': ref.get('paperId'),
                            'title': ref.get('title'),
                            'authors': [a.get('name') for a in ref.get('authors', []) if a.get('name')]
                        }
                        for ref in paper_data['references'][:10]  # Limit to first 10
                    ]
            
            return paper
            
        except Exception as e:
            logger.error(f"Error parsing paper data: {e}")
            return None

def collect_semantic_scholar_papers(max_papers: int = 300) -> List[Dict]:
    """Main function to collect papers from Semantic Scholar"""
    collector = SemanticScholarCollector()
    
    # Collect AI papers using search
    papers = collector.collect_ai_papers(max_papers=max_papers)
    
    # Optionally expand through citation network for highly cited papers
    if papers:
        # Take top 5 most cited papers as seeds for citation network expansion
        top_papers = sorted(papers, key=lambda x: x.get('citation_count', 0), reverse=True)[:5]
        seed_ids = [p['paper_id'] for p in top_papers if p.get('paper_id')]
        
        if seed_ids:
            logger.info("Expanding collection through citation network...")
            citation_papers = collector.collect_citation_network(seed_ids, max_depth=1)
            
            # Add new papers to collection
            existing_ids = {p.get('paper_id') for p in papers}
            new_papers = [p for p in citation_papers if p.get('paper_id') not in existing_ids]
            papers.extend(new_papers[:50])  # Limit additional papers
    
    return papers[:max_papers]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    papers = collect_semantic_scholar_papers(max_papers=30)  # Test with smaller number
    print(f"Collected {len(papers)} papers")
    if papers:
        print(f"Sample paper: {papers[0]['title']}")