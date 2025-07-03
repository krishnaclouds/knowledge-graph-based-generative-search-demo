import requests
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base64
import os

logger = logging.getLogger(__name__)

class GitHubCollector:
    """Collector for GitHub repository data and documentation"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.rate_limit_delay = 1  # seconds between requests
        
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'KnowledgeGraph-RAG-Demo'
        }
        
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
            logger.info("GitHub token configured - higher rate limits available")
        else:
            logger.warning("No GitHub token - using unauthenticated requests (lower rate limits)")
    
    def search_repositories(self, 
                           query: str,
                           max_repos: int = 100,
                           min_stars: int = 10) -> List[Dict]:
        """Search GitHub repositories"""
        repos = []
        per_page = 100  # GitHub API max
        page = 1
        
        while len(repos) < max_repos:
            search_query = f"{query} stars:>={min_stars}"
            params = {
                'q': search_query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': min(per_page, max_repos - len(repos)),
                'page': page
            }
            
            try:
                response = requests.get(
                    f"{self.base_url}/search/repositories",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                
                for item in items:
                    repo_data = self._parse_repository(item)
                    if repo_data:
                        repos.append(repo_data)
                
                logger.info(f"Fetched {len(items)} repositories, total: {len(repos)}")
                
                page += 1
                time.sleep(self.rate_limit_delay)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error searching repositories: {e}")
                break
                
        logger.info(f"Total repositories collected: {len(repos)}")
        return repos[:max_repos]
    
    def get_repository_details(self, owner: str, repo: str) -> Optional[Dict]:
        """Get detailed information about a specific repository"""
        try:
            # Get basic repo info
            repo_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self.headers
            )
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Get README content
            readme_content = self._get_readme_content(owner, repo)
            
            # Get repository topics
            topics = repo_data.get('topics', [])
            
            # Get languages
            languages = self._get_repository_languages(owner, repo)
            
            # Get contributors
            contributors = self._get_top_contributors(owner, repo)
            
            detailed_repo = {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'owner': repo_data['owner']['login'],
                'description': repo_data.get('description', ''),
                'url': repo_data['html_url'],
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'watchers': repo_data['watchers_count'],
                'language': repo_data.get('language'),
                'languages': languages,
                'topics': topics,
                'created_date': repo_data['created_at'],
                'updated_date': repo_data['updated_at'],
                'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                'readme_content': readme_content,
                'contributors': contributors,
                'document_type': 'github_repository',
                'source': 'github',
                'content': self._build_repo_content(repo_data, readme_content, topics),
                'metadata': {
                    'owner': repo_data['owner']['login'],
                    'stars': repo_data['stargazers_count'],
                    'forks': repo_data['forks_count'],
                    'language': repo_data.get('language'),
                    'languages': languages,
                    'topics': topics,
                    'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                    'contributors_count': len(contributors),
                    'created_year': repo_data['created_at'][:4],
                    'is_fork': repo_data.get('fork', False),
                    'has_wiki': repo_data.get('has_wiki', False),
                    'has_pages': repo_data.get('has_pages', False)
                }
            }
            
            return detailed_repo
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting repository details for {owner}/{repo}: {e}")
            return None
    
    def collect_ai_ml_repositories(self, max_repos: int = 200) -> List[Dict]:
        """Collect AI/ML focused repositories"""
        search_queries = [
            "machine learning python",
            "deep learning tensorflow pytorch",
            "artificial intelligence",
            "natural language processing nlp",
            "computer vision opencv",
            "neural networks",
            "reinforcement learning",
            "transformers huggingface",
            "graph neural networks",
            "knowledge graphs"
        ]
        
        all_repos = []
        repos_per_query = max_repos // len(search_queries)
        
        for query in search_queries:
            logger.info(f"Searching for: {query}")
            repos = self.search_repositories(
                query=query,
                max_repos=repos_per_query,
                min_stars=50  # Only popular repos
            )
            all_repos.extend(repos)
            
        # Remove duplicates by full_name
        unique_repos = {}
        for repo in all_repos:
            full_name = repo.get('full_name')
            if full_name and full_name not in unique_repos:
                unique_repos[full_name] = repo
        
        final_repos = list(unique_repos.values())[:max_repos]
        logger.info(f"Collected {len(final_repos)} unique AI/ML repositories")
        
        return final_repos
    
    def collect_company_repositories(self, max_repos: int = 100) -> List[Dict]:
        """Collect repositories from major tech companies"""
        tech_companies = [
            'google', 'microsoft', 'meta', 'openai', 'huggingface',
            'tensorflow', 'pytorch', 'nvidia', 'apple', 'amazon'
        ]
        
        all_repos = []
        repos_per_company = max_repos // len(tech_companies)
        
        for company in tech_companies:
            logger.info(f"Collecting repositories from {company}")
            
            try:
                # Get organization repositories
                params = {
                    'type': 'public',
                    'sort': 'stars',
                    'direction': 'desc',
                    'per_page': repos_per_company
                }
                
                response = requests.get(
                    f"{self.base_url}/orgs/{company}/repos",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    repos_data = response.json()
                    for repo_data in repos_data:
                        if repo_data['stargazers_count'] >= 10:  # Minimum threshold
                            repo = self._parse_repository(repo_data)
                            if repo:
                                all_repos.append(repo)
                else:
                    logger.warning(f"Could not fetch repos for {company}: {response.status_code}")
                
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error collecting from {company}: {e}")
        
        logger.info(f"Collected {len(all_repos)} company repositories")
        return all_repos[:max_repos]
    
    def _parse_repository(self, repo_data: Dict) -> Optional[Dict]:
        """Parse repository data from GitHub API response"""
        try:
            repo = {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'owner': repo_data['owner']['login'],
                'description': repo_data.get('description', ''),
                'url': repo_data['html_url'],
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'watchers': repo_data['watchers_count'],
                'language': repo_data.get('language'),
                'topics': repo_data.get('topics', []),
                'created_date': repo_data['created_at'],
                'updated_date': repo_data['updated_at'],
                'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                'document_type': 'github_repository',
                'source': 'github',
                'content': f"{repo_data['name']}\n\n{repo_data.get('description', '')}\n\nTopics: {', '.join(repo_data.get('topics', []))}",
                'metadata': {
                    'owner': repo_data['owner']['login'],
                    'stars': repo_data['stargazers_count'],
                    'forks': repo_data['forks_count'],
                    'language': repo_data.get('language'),
                    'topics': repo_data.get('topics', []),
                    'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                    'created_year': repo_data['created_at'][:4],
                    'is_fork': repo_data.get('fork', False)
                }
            }
            
            return repo
            
        except Exception as e:
            logger.error(f"Error parsing repository data: {e}")
            return None
    
    def _get_readme_content(self, owner: str, repo: str) -> str:
        """Get README content for a repository"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/readme",
                headers=self.headers
            )
            
            if response.status_code == 200:
                readme_data = response.json()
                if readme_data.get('encoding') == 'base64':
                    content = base64.b64decode(readme_data['content']).decode('utf-8')
                    # Remove markdown formatting for cleaner text
                    content = content.replace('#', '').replace('*', '').replace('`', '')
                    return content[:5000]  # Limit length
            
        except Exception as e:
            logger.error(f"Error fetching README for {owner}/{repo}: {e}")
            
        return ""
    
    def _get_repository_languages(self, owner: str, repo: str) -> Dict:
        """Get programming languages used in repository"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/languages",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            logger.error(f"Error fetching languages for {owner}/{repo}: {e}")
            
        return {}
    
    def _get_top_contributors(self, owner: str, repo: str, max_contributors: int = 10) -> List[Dict]:
        """Get top contributors for a repository"""
        try:
            params = {'per_page': max_contributors}
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contributors",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                contributors_data = response.json()
                contributors = []
                for contrib in contributors_data:
                    contributors.append({
                        'login': contrib['login'],
                        'contributions': contrib['contributions'],
                        'url': contrib['html_url']
                    })
                return contributors
                
        except Exception as e:
            logger.error(f"Error fetching contributors for {owner}/{repo}: {e}")
            
        return []
    
    def _build_repo_content(self, repo_data: Dict, readme: str, topics: List[str]) -> str:
        """Build comprehensive content string for repository"""
        content_parts = [
            f"Repository: {repo_data['name']}",
            f"Description: {repo_data.get('description', '')}",
            f"Owner: {repo_data['owner']['login']}",
            f"Language: {repo_data.get('language', 'Unknown')}",
            f"Stars: {repo_data['stargazers_count']}",
        ]
        
        if topics:
            content_parts.append(f"Topics: {', '.join(topics)}")
        
        if readme:
            content_parts.append(f"README:\n{readme}")
        
        return "\n\n".join(content_parts)

def collect_github_data(max_repos: int = 300) -> List[Dict]:
    """Main function to collect GitHub repository data"""
    collector = GitHubCollector()
    
    repos = []
    
    # Collect AI/ML repositories (70% of total)
    ai_ml_repos = collector.collect_ai_ml_repositories(
        max_repos=int(max_repos * 0.7)
    )
    repos.extend(ai_ml_repos)
    
    # Collect company repositories (30% of total)
    company_repos = collector.collect_company_repositories(
        max_repos=int(max_repos * 0.3)
    )
    repos.extend(company_repos)
    
    # Remove duplicates and limit to max_repos
    unique_repos = {}
    for repo in repos:
        full_name = repo.get('full_name')
        if full_name and full_name not in unique_repos:
            unique_repos[full_name] = repo
    
    final_repos = list(unique_repos.values())[:max_repos]
    logger.info(f"Final collection: {len(final_repos)} GitHub repositories")
    
    return final_repos

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repos = collect_github_data(max_repos=20)  # Test with smaller number
    print(f"Collected {len(repos)} repositories")
    if repos:
        print(f"Sample repo: {repos[0]['name']} ({repos[0]['stars']} stars)")