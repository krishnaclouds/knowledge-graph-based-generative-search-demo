import feedparser
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse
import html

logger = logging.getLogger(__name__)

class NewsCollector:
    """Collector for tech news and blog posts"""
    
    def __init__(self):
        self.news_sources = {
            "techcrunch": {
                "rss": "https://techcrunch.com/feed/",
                "base_url": "https://techcrunch.com",
                "topics": ["startups", "technology", "ai", "venture capital"]
            },
            "venturebeat": {
                "rss": "http://feeds.feedburner.com/venturebeat/SZYF",
                "base_url": "https://venturebeat.com",
                "topics": ["ai", "technology", "enterprise", "games"]
            },
            "arstechnica": {
                "rss": "http://feeds.arstechnica.com/arstechnica/technology-lab",
                "base_url": "https://arstechnica.com",
                "topics": ["science", "technology", "policy"]
            },
            "wired": {
                "rss": "https://www.wired.com/feed/rss",
                "base_url": "https://www.wired.com",
                "topics": ["technology", "science", "security", "business"]
            },
            "theverge": {
                "rss": "https://www.theverge.com/rss/index.xml",
                "base_url": "https://www.theverge.com",
                "topics": ["technology", "science", "entertainment"]
            }
        }
        
        self.company_blogs = {
            "google_research": {
                "rss": "https://research.googleblog.com/feeds/posts/default",
                "base_url": "https://research.googleblog.com",
                "company": "Google",
                "topics": ["ai research", "machine learning", "computer science"]
            },
            "microsoft_research": {
                "rss": "https://www.microsoft.com/en-us/research/feed/",
                "base_url": "https://www.microsoft.com/en-us/research",
                "company": "Microsoft",
                "topics": ["ai", "quantum computing", "systems"]
            },
            "openai_blog": {
                "rss": "https://openai.com/blog/rss.xml",
                "base_url": "https://openai.com/blog",
                "company": "OpenAI",
                "topics": ["ai safety", "research", "gpt models"]
            },
            "meta_ai": {
                "rss": "https://ai.meta.com/blog/rss.xml",
                "base_url": "https://ai.meta.com/blog",
                "company": "Meta",
                "topics": ["ai research", "computer vision", "nlp"]
            },
            "deepmind": {
                "rss": "https://deepmind.com/blog/rss.xml",
                "base_url": "https://deepmind.com/blog",
                "company": "DeepMind",
                "topics": ["ai research", "reinforcement learning", "protein folding"]
            }
        }
        
        self.rate_limit_delay = 2  # seconds between requests
        
    def collect_news_articles(self, 
                             days_back: int = 180,
                             max_articles_per_source: int = 50) -> List[Dict]:
        """Collect news articles from tech news sources"""
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for source_name, source_info in self.news_sources.items():
            logger.info(f"Collecting articles from {source_name}")
            
            try:
                feed = feedparser.parse(source_info["rss"])
                source_articles = []
                
                for entry in feed.entries:
                    article = self._parse_news_entry(entry, source_name, source_info)
                    if article and self._is_recent_article(article, cutoff_date):
                        source_articles.append(article)
                        
                    if len(source_articles) >= max_articles_per_source:
                        break
                
                articles.extend(source_articles)
                logger.info(f"Collected {len(source_articles)} articles from {source_name}")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error collecting from {source_name}: {e}")
                
        logger.info(f"Total news articles collected: {len(articles)}")
        return articles
    
    def collect_company_blogs(self, 
                             days_back: int = 365,
                             max_posts_per_company: int = 30) -> List[Dict]:
        """Collect blog posts from tech company research blogs"""
        posts = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for blog_name, blog_info in self.company_blogs.items():
            logger.info(f"Collecting posts from {blog_name}")
            
            try:
                feed = feedparser.parse(blog_info["rss"])
                blog_posts = []
                
                for entry in feed.entries:
                    post = self._parse_blog_entry(entry, blog_name, blog_info)
                    if post and self._is_recent_article(post, cutoff_date):
                        blog_posts.append(post)
                        
                    if len(blog_posts) >= max_posts_per_company:
                        break
                
                posts.extend(blog_posts)
                logger.info(f"Collected {len(blog_posts)} posts from {blog_name}")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error collecting from {blog_name}: {e}")
                
        logger.info(f"Total company blog posts collected: {len(posts)}")
        return posts
    
    def _parse_news_entry(self, entry, source_name: str, source_info: Dict) -> Optional[Dict]:
        """Parse RSS entry into standardized article format"""
        try:
            title = html.unescape(entry.title) if hasattr(entry, 'title') else ""
            
            # Get content
            content = ""
            if hasattr(entry, 'content') and entry.content:
                content = html.unescape(entry.content[0].value)
            elif hasattr(entry, 'summary'):
                content = html.unescape(entry.summary)
            elif hasattr(entry, 'description'):
                content = html.unescape(entry.description)
            
            # Clean HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Extract metadata
            url = entry.link if hasattr(entry, 'link') else ""
            pub_date = entry.published if hasattr(entry, 'published') else ""
            
            # Parse publication date
            published_datetime = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_datetime = datetime(*entry.published_parsed[:6])
            
            # Extract tags/categories
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags]
            
            # Extract author
            author = ""
            if hasattr(entry, 'author'):
                author = entry.author
            elif hasattr(entry, 'authors'):
                author = ", ".join([a.name for a in entry.authors])
            
            article = {
                'title': title,
                'content': content,
                'url': url,
                'published_date': pub_date,
                'published_datetime': published_datetime,
                'author': author,
                'source': source_name,
                'source_url': source_info["base_url"],
                'tags': tags,
                'topics': source_info["topics"],
                'document_type': 'news_article',
                'metadata': {
                    'source': source_name,
                    'url': url,
                    'author': author,
                    'tags': tags,
                    'topics': source_info["topics"],
                    'published_year': published_datetime.year if published_datetime else None,
                    'word_count': len(content.split()) if content else 0
                }
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing news entry: {e}")
            return None
    
    def _parse_blog_entry(self, entry, blog_name: str, blog_info: Dict) -> Optional[Dict]:
        """Parse company blog RSS entry"""
        try:
            title = html.unescape(entry.title) if hasattr(entry, 'title') else ""
            
            # Get content
            content = ""
            if hasattr(entry, 'content') and entry.content:
                content = html.unescape(entry.content[0].value)
            elif hasattr(entry, 'summary'):
                content = html.unescape(entry.summary)
            elif hasattr(entry, 'description'):
                content = html.unescape(entry.description)
            
            # Clean HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Extract metadata
            url = entry.link if hasattr(entry, 'link') else ""
            pub_date = entry.published if hasattr(entry, 'published') else ""
            
            # Parse publication date
            published_datetime = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_datetime = datetime(*entry.published_parsed[:6])
            
            # Extract tags/categories
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags]
            
            # Extract author
            author = ""
            if hasattr(entry, 'author'):
                author = entry.author
            elif hasattr(entry, 'authors'):
                author = ", ".join([a.name for a in entry.authors])
            
            post = {
                'title': title,
                'content': content,
                'url': url,
                'published_date': pub_date,
                'published_datetime': published_datetime,
                'author': author,
                'source': blog_name,
                'company': blog_info["company"],
                'source_url': blog_info["base_url"],
                'tags': tags,
                'topics': blog_info["topics"],
                'document_type': 'company_blog',
                'metadata': {
                    'source': blog_name,
                    'company': blog_info["company"],
                    'url': url,
                    'author': author,
                    'tags': tags,
                    'topics': blog_info["topics"],
                    'published_year': published_datetime.year if published_datetime else None,
                    'word_count': len(content.split()) if content else 0
                }
            }
            
            return post
            
        except Exception as e:
            logger.error(f"Error parsing blog entry: {e}")
            return None
    
    def _is_recent_article(self, article: Dict, cutoff_date: datetime) -> bool:
        """Check if article is within the specified date range"""
        if article.get('published_datetime'):
            return article['published_datetime'] >= cutoff_date
        return True  # Include if no date available
    
    def collect_all_content(self, 
                           news_days_back: int = 180,
                           blog_days_back: int = 365,
                           max_per_source: int = 50) -> List[Dict]:
        """Collect all news articles and company blog posts"""
        all_content = []
        
        # Collect news articles
        news_articles = self.collect_news_articles(
            days_back=news_days_back,
            max_articles_per_source=max_per_source
        )
        all_content.extend(news_articles)
        
        # Collect company blog posts
        blog_posts = self.collect_company_blogs(
            days_back=blog_days_back,
            max_posts_per_company=max_per_source
        )
        all_content.extend(blog_posts)
        
        # Filter and enhance content
        filtered_content = []
        for item in all_content:
            if self._is_tech_relevant(item):
                item = self._enhance_metadata(item)
                filtered_content.append(item)
        
        logger.info(f"Total relevant content collected: {len(filtered_content)}")
        return filtered_content
    
    def _is_tech_relevant(self, item: Dict) -> bool:
        """Check if content is relevant to tech/AI domain"""
        tech_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'algorithm', 'data science', 'cloud computing',
            'software', 'hardware', 'startup', 'technology', 'innovation',
            'computer vision', 'natural language', 'robotics', 'automation',
            'blockchain', 'cryptocurrency', 'quantum computing', 'semiconductor'
        ]
        
        text = f"{item.get('title', '')} {item.get('content', '')}".lower()
        
        # Check for tech keywords
        for keyword in tech_keywords:
            if keyword in text:
                return True
                
        # Check if from tech company blog
        if item.get('document_type') == 'company_blog':
            return True
            
        return False
    
    def _enhance_metadata(self, item: Dict) -> Dict:
        """Enhance item metadata with extracted entities"""
        content = f"{item.get('title', '')} {item.get('content', '')}"
        
        # Extract company mentions
        companies = ['Google', 'Apple', 'Microsoft', 'Amazon', 'Meta', 'Tesla', 
                    'OpenAI', 'Netflix', 'NVIDIA', 'Intel', 'IBM', 'Oracle']
        mentioned_companies = []
        for company in companies:
            if company.lower() in content.lower():
                mentioned_companies.append(company)
        
        # Extract technology mentions
        technologies = ['AI', 'ML', 'blockchain', 'quantum', 'cloud', 'IoT',
                       'VR', 'AR', 'autonomous', 'robotics', 'cryptocurrency']
        mentioned_tech = []
        for tech in technologies:
            if tech.lower() in content.lower():
                mentioned_tech.append(tech)
        
        # Update metadata
        item['metadata']['mentioned_companies'] = mentioned_companies
        item['metadata']['mentioned_technologies'] = mentioned_tech
        item['metadata']['content_length'] = len(content)
        
        return item

def collect_news_content(max_articles: int = 400) -> List[Dict]:
    """Main function to collect news and blog content"""
    collector = NewsCollector()
    
    # Calculate articles per source
    total_sources = len(collector.news_sources) + len(collector.company_blogs)
    max_per_source = max(10, max_articles // total_sources)
    
    content = collector.collect_all_content(
        news_days_back=180,  # 6 months of news
        blog_days_back=365,  # 1 year of company blogs
        max_per_source=max_per_source
    )
    
    return content[:max_articles]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    content = collect_news_content(max_articles=50)  # Test with smaller number
    print(f"Collected {len(content)} articles")
    if content:
        print(f"Sample article: {content[0]['title']}")