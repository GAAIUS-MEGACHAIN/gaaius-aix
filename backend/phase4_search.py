"""
PHASE 4: Advanced Search Engine with Elasticsearch
Production-grade full-text search with relevance scoring and aggregations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from motor.motor_asyncio import AsyncIOMotorDatabase


logger = logging.getLogger(__name__)


class SearchType(str, Enum):
    """Types of search queries"""
    VIDEO = "video"
    USER = "user"
    PLAYLIST = "playlist"
    CHANNEL = "channel"


class SearchFilter(str, Enum):
    """Common search filters"""
    DATE_24H = "day"
    DATE_WEEK = "week"
    DATE_MONTH = "month"
    RATING_HIGH = "rating_high"
    DURATION_SHORT = "duration_short"
    DURATION_LONG = "duration_long"


class ElasticsearchManager:
    """Elasticsearch integration for advanced search"""
    
    def __init__(self, es_url: str = "http://localhost:9200", db: Optional[AsyncIOMotorDatabase] = None):
        self.es_client = Elasticsearch([es_url])
        self.db = db
        self.indexes = {
            SearchType.VIDEO: "videos",
            SearchType.USER: "users",
            SearchType.PLAYLIST: "playlists",
            SearchType.CHANNEL: "channels",
        }
    
    async def initialize_indexes(self) -> None:
        """Create and configure Elasticsearch indexes"""
        # Video index configuration
        video_mapping = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "standard",
                            "stopwords": "_english_"
                        },
                        "autocomplete": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 20,
                            "tokenizer": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "video_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "autocomplete": {"type": "text", "analyzer": "autocomplete"}
                        },
                        "boost": 3.0
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard",
                        "boost": 1.5
                    },
                    "channel_name": {
                        "type": "text",
                        "analyzer": "standard",
                        "boost": 2.0
                    },
                    "tags": {
                        "type": "keyword"
                    },
                    "category": {
                        "type": "keyword"
                    },
                    "view_count": {
                        "type": "long"
                    },
                    "like_count": {
                        "type": "long"
                    },
                    "comment_count": {
                        "type": "long"
                    },
                    "upload_date": {
                        "type": "date"
                    },
                    "duration_seconds": {
                        "type": "integer"
                    },
                    "rating": {
                        "type": "float"
                    },
                    "is_public": {
                        "type": "boolean"
                    },
                    "channel_id": {
                        "type": "keyword"
                    },
                    "user_id": {
                        "type": "keyword"
                    },
                    "created_at": {
                        "type": "date"
                    },
                    "trending_score": {
                        "type": "float"
                    }
                }
            }
        }
        
        # Create video index
        try:
            self.es_client.indices.create(
                index=self.indexes[SearchType.VIDEO],
                body=video_mapping,
                ignore=400  # Ignore if already exists
            )
            logger.info(f"Created/verified index: {self.indexes[SearchType.VIDEO]}")
        except Exception as e:
            logger.error(f"Error creating video index: {e}")
    
    async def index_video(self, video_data: Dict[str, Any]) -> bool:
        """Index video document"""
        try:
            self.es_client.index(
                index=self.indexes[SearchType.VIDEO],
                id=video_data.get("_id"),
                body={
                    "video_id": str(video_data.get("_id")),
                    "title": video_data.get("title", ""),
                    "description": video_data.get("description", ""),
                    "channel_name": video_data.get("channel_name", ""),
                    "tags": video_data.get("tags", []),
                    "category": video_data.get("category", ""),
                    "view_count": video_data.get("view_count", 0),
                    "like_count": video_data.get("like_count", 0),
                    "comment_count": video_data.get("comment_count", 0),
                    "upload_date": video_data.get("created_at"),
                    "duration_seconds": video_data.get("duration_seconds", 0),
                    "rating": video_data.get("rating", 0.0),
                    "is_public": video_data.get("is_public", True),
                    "channel_id": str(video_data.get("channel_id")),
                    "user_id": str(video_data.get("user_id")),
                    "created_at": video_data.get("created_at"),
                    "trending_score": await self._calculate_trending_score(video_data),
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing video: {e}")
            return False
    
    async def bulk_index_videos(self, videos: List[Dict[str, Any]]) -> int:
        """Bulk index multiple videos"""
        actions = []
        for video in videos:
            action = {
                "_index": self.indexes[SearchType.VIDEO],
                "_id": str(video.get("_id")),
                "_source": {
                    "video_id": str(video.get("_id")),
                    "title": video.get("title", ""),
                    "description": video.get("description", ""),
                    "channel_name": video.get("channel_name", ""),
                    "tags": video.get("tags", []),
                    "category": video.get("category", ""),
                    "view_count": video.get("view_count", 0),
                    "like_count": video.get("like_count", 0),
                    "comment_count": video.get("comment_count", 0),
                    "upload_date": video.get("created_at"),
                    "duration_seconds": video.get("duration_seconds", 0),
                    "rating": video.get("rating", 0.0),
                    "is_public": video.get("is_public", True),
                    "channel_id": str(video.get("channel_id")),
                    "user_id": str(video.get("user_id")),
                    "created_at": video.get("created_at"),
                    "trending_score": await self._calculate_trending_score(video),
                }
            }
            actions.append(action)
        
        success, _ = bulk(self.es_client, actions)
        logger.info(f"Bulk indexed {success} videos")
        return success
    
    async def search_videos(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: str = "relevance",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search videos with advanced filtering"""
        size = page_size
        from_offset = (page - 1) * page_size
        
        # Build query
        es_query = {
            "bool": {
                "must": [],
                "filter": []
            }
        }
        
        # Full-text search with multi-field boost
        if query:
            es_query["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title^3",  # Title gets 3x boost
                        "description^1.5",
                        "tags^2",
                        "channel_name^2"
                    ],
                    "fuzziness": "AUTO",
                    "operator": "or"
                }
            })
        
        # Apply filters
        if filters:
            # Category filter
            if "category" in filters:
                es_query["bool"]["filter"].append({
                    "term": {"category.keyword": filters["category"]}
                })
            
            # Date filter
            if "date_filter" in filters:
                date_range = self._get_date_range(filters["date_filter"])
                es_query["bool"]["filter"].append({
                    "range": {"upload_date": date_range}
                })
            
            # Duration filter
            if "duration_filter" in filters:
                duration_range = self._get_duration_range(filters["duration_filter"])
                es_query["bool"]["filter"].append({
                    "range": {"duration_seconds": duration_range}
                })
            
            # Rating filter
            if "min_rating" in filters:
                es_query["bool"]["filter"].append({
                    "range": {"rating": {"gte": filters["min_rating"]}}
                })
            
            # Channel filter
            if "channel_id" in filters:
                es_query["bool"]["filter"].append({
                    "term": {"channel_id.keyword": filters["channel_id"]}
                })
        
        # Only public videos
        es_query["bool"]["filter"].append({"term": {"is_public": True}})
        
        # Determine sort
        sort_params = self._get_sort_params(sort)
        
        try:
            response = self.es_client.search(
                index=self.indexes[SearchType.VIDEO],
                query=es_query,
                sort=sort_params,
                size=size,
                from_=from_offset,
                highlight={
                    "fields": {
                        "title": {},
                        "description": {},
                    }
                }
            )
            
            # Format results
            hits = response["hits"]
            results = []
            
            for hit in hits["hits"]:
                result = hit["_source"]
                result["video_id"] = hit["_id"]
                result["score"] = hit["_score"]
                
                # Add highlighted fields if available
                if "highlight" in hit:
                    result["highlight"] = hit["highlight"]
                
                results.append(result)
            
            return {
                "query": query,
                "total": hits["total"]["value"],
                "page": page,
                "page_size": page_size,
                "results": results,
                "has_more": (page * page_size) < hits["total"]["value"]
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"query": query, "total": 0, "results": []}
    
    async def get_search_suggestions(
        self,
        prefix: str,
        limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions"""
        try:
            response = self.es_client.search(
                index=self.indexes[SearchType.VIDEO],
                query={
                    "match": {
                        "title.autocomplete": {
                            "query": prefix,
                            "fuzziness": 1
                        }
                    }
                },
                aggs={
                    "suggestions": {
                        "terms": {
                            "field": "title.keyword",
                            "size": limit
                        }
                    }
                },
                size=0
            )
            
            suggestions = [
                bucket["key"]
                for bucket in response["aggregations"]["suggestions"]["buckets"]
            ]
            
            return suggestions[:limit]
        except Exception as e:
            logger.error(f"Suggestion error: {e}")
            return []
    
    async def get_trending_videos(
        self,
        time_period: str = "day",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get trending videos based on scoring"""
        date_range = self._get_date_range(time_period)
        
        try:
            response = self.es_client.search(
                index=self.indexes[SearchType.VIDEO],
                query={
                    "bool": {
                        "filter": [
                            {"range": {"upload_date": date_range}},
                            {"term": {"is_public": True}}
                        ]
                    }
                },
                sort=[
                    {"trending_score": {"order": "desc"}},
                    {"_score": {"order": "desc"}}
                ],
                size=limit
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["video_id"] = hit["_id"]
                result["score"] = hit["_score"]
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Trending search error: {e}")
            return []
    
    async def get_related_videos(
        self,
        video_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get related videos using more-like-this"""
        try:
            response = self.es_client.search(
                index=self.indexes[SearchType.VIDEO],
                query={
                    "more_like_this": {
                        "fields": ["title", "tags", "category", "description"],
                        "like": [{"_id": video_id}],
                        "min_term_freq": 1,
                    }
                },
                size=limit
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["video_id"] = hit["_id"]
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Related videos error: {e}")
            return []
    
    async def update_video_stats(self, video_id: str, stats: Dict[str, int]) -> None:
        """Update video statistics in index"""
        try:
            self.es_client.update(
                index=self.indexes[SearchType.VIDEO],
                id=video_id,
                body={
                    "doc": {
                        "view_count": stats.get("view_count", 0),
                        "like_count": stats.get("like_count", 0),
                        "comment_count": stats.get("comment_count", 0),
                        "rating": stats.get("rating", 0.0),
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating video stats: {e}")
    
    async def delete_video(self, video_id: str) -> bool:
        """Delete video from index"""
        try:
            self.es_client.delete(
                index=self.indexes[SearchType.VIDEO],
                id=video_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting video from index: {e}")
            return False
    
    def _get_date_range(self, time_period: str) -> Dict[str, str]:
        """Get date range for time period"""
        ranges = {
            "day": {"gte": "now-24h"},
            "week": {"gte": "now-7d"},
            "month": {"gte": "now-30d"},
            "year": {"gte": "now-1y"},
        }
        return ranges.get(time_period, {"gte": "now-24h"})
    
    def _get_duration_range(self, duration_filter: str) -> Dict[str, int]:
        """Get duration range for filter"""
        ranges = {
            "duration_short": {"lte": 300},  # ≤ 5 min
            "duration_medium": {"gte": 300, "lte": 1200},  # 5-20 min
            "duration_long": {"gte": 1200},  # > 20 min
        }
        return ranges.get(duration_filter, {})
    
    def _get_sort_params(self, sort: str) -> List[Dict[str, Any]]:
        """Get sort parameters"""
        sorts = {
            "relevance": ["_score"],
            "newest": [{"upload_date": {"order": "desc"}}],
            "oldest": [{"upload_date": {"order": "asc"}}],
            "most_views": [{"view_count": {"order": "desc"}}],
            "most_liked": [{"like_count": {"order": "desc"}}],
            "trending": [{"trending_score": {"order": "desc"}}],
        }
        return sorts.get(sort, ["_score"])
    
    async def _calculate_trending_score(self, video: Dict[str, Any]) -> float:
        """Calculate trending score based on engagement"""
        now = datetime.utcnow()
        created = video.get("created_at")
        
        # Calculate age in hours
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        
        hours_old = max(1, (now - created).total_seconds() / 3600)
        
        # Trending formula: (views + likes + comments) / age_factor
        engagement = (
            video.get("view_count", 0) * 1.0 +
            video.get("like_count", 0) * 5.0 +
            video.get("comment_count", 0) * 10.0
        )
        
        trending_score = engagement / (hours_old ** 1.5)
        
        return min(10000.0, max(0.0, trending_score))
