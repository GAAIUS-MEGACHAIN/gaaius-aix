"""
PHASE 9: Enterprise Search & Discovery Service
Full-text search, filtering, sorting, recommendations
Elasticsearch integration for production scalability
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import os

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


# ============================================================================
# SEARCH CONFIG
# ============================================================================

class SearchConfig:
    """Search configuration"""
    ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT = int(os.environ.get("ELASTICSEARCH_PORT", "9200"))
    ELASTICSEARCH_USERNAME = os.environ.get("ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD")
    
    INDEX_NAME = "netflix_content"
    MAX_RESULTS = 1000
    DEFAULT_PAGE_SIZE = 20


# ============================================================================
# SORT OPTIONS
# ============================================================================

class SortBy(Enum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    OLDEST = "oldest"
    MOST_POPULAR = "most_popular"
    HIGHEST_RATED = "highest_rated"
    TRENDING = "trending"
    ALPHABETICAL = "alphabetical"


# ============================================================================
# SEARCH SERVICE
# ============================================================================

class SearchService:
    """Full-text search with Elasticsearch"""
    
    def __init__(self):
        """Initialize Elasticsearch client"""
        try:
            auth = None
            if SearchConfig.ELASTICSEARCH_USERNAME and SearchConfig.ELASTICSEARCH_PASSWORD:
                auth = (SearchConfig.ELASTICSEARCH_USERNAME, SearchConfig.ELASTICSEARCH_PASSWORD)
            
            self.es = Elasticsearch(
                hosts=[{
                    "host": SearchConfig.ELASTICSEARCH_HOST,
                    "port": SearchConfig.ELASTICSEARCH_PORT
                }],
                basic_auth=auth if auth else None,
                request_timeout=30
            )
            
            info = self.es.info()
            logger.info(f"✅ Connected to Elasticsearch: {info['version']['number']}")
        except Exception as e:
            logger.warning(f"⚠️ Elasticsearch connection failed: {e}")
            self.es = None
    
    def index_content(self, content_id: str, content_data: Dict) -> bool:
        """Index content for search"""
        try:
            if not self.es:
                logger.warning("Elasticsearch not available")
                return False
            
            doc = {
                "id": content_id,
                "title": content_data.get("title"),
                "description": content_data.get("description"),
                "long_description": content_data.get("long_description"),
                "genres": content_data.get("genres", []),
                "cast": content_data.get("cast", []),
                "directors": content_data.get("directors", []),
                "producers": content_data.get("producers", []),
                "country": content_data.get("country"),
                "language": content_data.get("language"),
                "content_type": content_data.get("content_type"),
                "age_rating": content_data.get("age_rating"),
                "release_date": content_data.get("release_date"),
                "imdb_rating": content_data.get("imdb_rating"),
                "average_rating": content_data.get("average_rating", 0),
                "total_views": content_data.get("total_views", 0),
                "is_published": content_data.get("is_published", False),
                "is_available": content_data.get("is_available", False),
                "is_trending": content_data.get("is_trending", False),
                "trending_score": content_data.get("trending_score", 0),
                "indexed_at": datetime.utcnow().isoformat()
            }
            
            self.es.index(index=SearchConfig.INDEX_NAME, id=content_id, document=doc)
            return True
        except Exception as e:
            logger.error(f"Error indexing content: {e}")
            return False
    
    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        sort_by: SortBy = SortBy.RELEVANCE,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """Full-text search with filtering"""
        if not self.es:
            return self._fallback_search(query, filters, page, page_size)
        
        try:
            # Build query
            must_clauses = []
            filter_clauses = []
            
            if query:
                must_clauses.append({
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title^3",
                            "description^2",
                            "cast^2",
                            "directors^2",
                            "genres"
                        ],
                        "fuzziness": "AUTO"
                    }
                })
            
            # Only published and available content
            filter_clauses.append({"term": {"is_published": True}})
            filter_clauses.append({"term": {"is_available": True}})
            
            # Apply filters
            if filters:
                if "genres" in filters and filters["genres"]:
                    filter_clauses.append({
                        "terms": {"genres": filters["genres"]}
                    })
                
                if "content_type" in filters and filters["content_type"]:
                    filter_clauses.append({
                        "term": {"content_type": filters["content_type"]}
                    })
                
                if "age_rating" in filters and filters["age_rating"]:
                    filter_clauses.append({
                        "term": {"age_rating": filters["age_rating"]}
                    })
                
                if "country" in filters and filters["country"]:
                    filter_clauses.append({
                        "term": {"country": filters["country"]}
                    })
                
                if "language" in filters and filters["language"]:
                    filter_clauses.append({
                        "term": {"language": filters["language"]}
                    })
                
                if "min_rating" in filters:
                    filter_clauses.append({
                        "range": {"average_rating": {"gte": filters["min_rating"]}}
                    })
                
                if "release_year" in filters:
                    filter_clauses.append({
                        "term": {"release_year": filters["release_year"]}
                    })
            
            # Build sort
            sort_params = self._get_sort_params(sort_by)
            
            # Calculate pagination
            from_value = (page - 1) * min(page_size, SearchConfig.MAX_RESULTS)
            to_value = min(from_value + page_size, SearchConfig.MAX_RESULTS)
            
            # Execute search
            query_body = {
                "query": {
                    "bool": {
                        "must": must_clauses if must_clauses else [{"match_all": {}}],
                        "filter": filter_clauses
                    }
                },
                "sort": sort_params,
                "from": from_value,
                "size": to_value - from_value,
                "track_total_hits": True
            }
            
            response = self.es.search(index=SearchConfig.INDEX_NAME, body=query_body)
            
            results = {
                "query": query,
                "total_results": response["hits"]["total"]["value"],
                "page": page,
                "page_size": page_size,
                "total_pages": (response["hits"]["total"]["value"] + page_size - 1) // page_size,
                "results": [
                    {
                        "id": hit["_id"],
                        "title": hit["_source"]["title"],
                        "description": hit["_source"]["description"],
                        "content_type": hit["_source"]["content_type"],
                        "genres": hit["_source"]["genres"],
                        "rating": hit["_source"]["average_rating"],
                        "imdb_rating": hit["_source"]["imdb_rating"],
                        "release_date": hit["_source"]["release_date"],
                        "views": hit["_source"]["total_views"],
                        "score": hit["_score"]
                    }
                    for hit in response["hits"]["hits"]
                ]
            }
            
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return self._fallback_search(query, filters, page, page_size)
    
    def _get_sort_params(self, sort_by: SortBy) -> List:
        """Get sort parameters"""
        sort_map = {
            SortBy.RELEVANCE: [{"_score": {"order": "desc"}}],
            SortBy.NEWEST: [{"release_date": {"order": "desc"}}],
            SortBy.OLDEST: [{"release_date": {"order": "asc"}}],
            SortBy.MOST_POPULAR: [{"total_views": {"order": "desc"}}],
            SortBy.HIGHEST_RATED: [{"average_rating": {"order": "desc"}}],
            SortBy.TRENDING: [{"trending_score": {"order": "desc"}}],
            SortBy.ALPHABETICAL: [{"title.keyword": {"order": "asc"}}]
        }
        return sort_map.get(sort_by, sort_map[SortBy.RELEVANCE])
    
    def _fallback_search(
        self,
        query: str,
        filters: Optional[Dict],
        page: int,
        page_size: int
    ) -> Dict:
        """Fallback search without Elasticsearch"""
        # TODO: Implement fallback to database search
        return {
            "query": query,
            "total_results": 0,
            "page": page,
            "page_size": page_size,
            "results": [],
            "warning": "Using fallback search"
        }
    
    def search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions"""
        if not self.es or not query:
            return []
        
        try:
            response = self.es.search(
                index=SearchConfig.INDEX_NAME,
                body={
                    "query": {
                        "match": {
                            "title": {
                                "query": query,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    "_source": ["title"],
                    "size": limit
                }
            )
            
            return list(set([hit["_source"]["title"] for hit in response["hits"]["hits"]]))
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []
    
    def get_similar_content(self, content_id: str, limit: int = 10) -> List[Dict]:
        """Get similar content using Elasticsearch"""
        if not self.es:
            return []
        
        try:
            # Get the content to find similar items
            content = self.es.get(index=SearchConfig.INDEX_NAME, id=content_id)
            source = content["_source"]
            
            # More like this query
            response = self.es.search(
                index=SearchConfig.INDEX_NAME,
                body={
                    "query": {
                        "more_like_this": {
                            "fields": ["title", "description", "genres", "cast"],
                            "like": [{"_id": content_id}],
                            "min_term_freq": 1,
                            "min_doc_freq": 1
                        }
                    },
                    "size": limit
                }
            )
            
            return [
                {
                    "id": hit["_id"],
                    "title": hit["_source"]["title"],
                    "rating": hit["_source"]["average_rating"],
                    "similarity": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
        except Exception as e:
            logger.error(f"Error getting similar content: {e}")
            return []


# ============================================================================
# DISCOVERY SERVICE
# ============================================================================

class DiscoveryService:
    """Content discovery and recommendations"""
    
    @staticmethod
    def get_trending_now(limit: int = 20, country: Optional[str] = None) -> List[Dict]:
        """Get trending content"""
        # TODO: Query database for trending content
        # Filter by country if specified
        return []
    
    @staticmethod
    def get_new_releases(content_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get recently released content"""
        # TODO: Query database for new releases
        # Sort by release date descending
        # Filter by content type if specified
        return []
    
    @staticmethod
    def get_recommended_for_you(
        user_id: str,
        limit: int = 20,
        algorithm: str = "collaborative"
    ) -> List[Dict]:
        """Get personalized recommendations"""
        # TODO: Implement recommendation algorithm
        # collaborative: Based on similar users
        # content_based: Based on user's watch history
        # hybrid: Combination
        return []
    
    @staticmethod
    def get_genre_content(
        genre: str,
        sort_by: str = "rating",
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:
        """Get all content in a genre"""
        # TODO: Query database for genre content
        # Sort by specified field
        # Return results and total count
        return [], 0
    
    @staticmethod
    def get_featured_content() -> Dict:
        """Get featured/curated content for homepage"""
        return {
            "featured": [],  # Hero section content
            "trending": [],
            "new_releases": [],
            "my_recommendations": [],
            "continue_watching": [],
            "because_you_watched": []
        }
    
    @staticmethod
    def build_recommendation_matrix(user_watch_history: List[Dict]) -> Dict:
        """Build recommendation matrix from watch history"""
        # TODO: Implement collaborative filtering
        # TODO: Extract user preferences from history
        return {}
    
    @staticmethod
    def get_personalized_categories(user_id: str) -> List[Dict]:
        """Get personalized content categories"""
        # TODO: Build categories based on user preferences
        return []


# ============================================================================
# FILTER SERVICE
# ============================================================================

class FilterService:
    """Content filtering and faceted search"""
    
    @staticmethod
    def get_available_filters() -> Dict:
        """Get available filter options"""
        return {
            "genres": [
                "Action", "Comedy", "Drama", "Horror", "Thriller",
                "Romance", "Sci-Fi", "Fantasy", "Documentary", "Animation"
            ],
            "content_types": ["Movie", "Series", "Documentary", "Special"],
            "ratings": [
                {"value": "G", "label": "General Audiences"},
                {"value": "PG", "label": "Parental Guidance"},
                {"value": "PG-13", "label": "Parents Strongly Cautioned"},
                {"value": "R", "label": "Restricted"},
                {"value": "NC-17", "label": "No One 17 Under"}
            ],
            "release_years": list(range(2024, 1990, -1)),
            "languages": [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Spanish"},
                {"code": "fr", "name": "French"},
                {"code": "de", "name": "German"},
                {"code": "it", "name": "Italian"},
                {"code": "pt", "name": "Portuguese"},
                {"code": "ja", "name": "Japanese"},
                {"code": "ko", "name": "Korean"}
            ],
            "countries": [
                {"code": "US", "name": "United States"},
                {"code": "GB", "name": "United Kingdom"},
                {"code": "CA", "name": "Canada"},
                {"code": "AU", "name": "Australia"},
                {"code": "IN", "name": "India"},
                {"code": "JP", "name": "Japan"},
                {"code": "KR", "name": "South Korea"},
                {"code": "MX", "name": "Mexico"}
            ],
            "ratings_range": {
                "min": 0,
                "max": 10,
                "step": 0.5
            }
        }
    
    @staticmethod
    def get_facet_counts(search_results: List[Dict]) -> Dict:
        """Get facet counts from search results"""
        facets = {
            "genres": {},
            "content_types": {},
            "ratings": {},
            "years": {}
        }
        
        for result in search_results:
            # Count genres
            for genre in result.get("genres", []):
                facets["genres"][genre] = facets["genres"].get(genre, 0) + 1
            
            # Count content type
            ct = result.get("content_type")
            if ct:
                facets["content_types"][ct] = facets["content_types"].get(ct, 0) + 1
            
            # Count rating buckets
            rating = result.get("rating", 0)
            if rating:
                bucket = int(rating)
                facets["ratings"][bucket] = facets["ratings"].get(bucket, 0) + 1
        
        return facets


if __name__ == "__main__":
    # Test search service
    search = SearchService()
    
    # Test search
    results = search.search("action", filters={"genres": ["Action"]})
    print(f"✅ Search results: {results['total_results']} items")
    
    # Test suggestions
    suggestions = search.search_suggestions("mar")
    print(f"✅ Suggestions: {suggestions[:5]}")
    
    # Test discovery
    discovery = DiscoveryService()
    featured = discovery.get_featured_content()
    print(f"✅ Featured content ready")
    
    # Test filters
    filters = FilterService.get_available_filters()
    print(f"✅ Available filters: {len(filters)} categories")
