"""Recommendation engine with vector similarity search"""
import logging
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
from backend.models import Item, ItemEmbedding
from backend.ollama_client import ollama_client
from backend.config import settings

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Main recommendation engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.topk = settings.retrieve_topk
        self.topn = settings.return_topn
        # Set logger level based on config to reduce overhead
        try:
            logger.setLevel(getattr(logging, settings.log_level, logging.WARNING))
        except Exception:
            logger.setLevel(logging.WARNING)
    
    def search_similar_items(self, query_embedding: List[float], limit: int = None) -> List[Dict[str, Any]]:
        """Search for similar items using vector similarity"""
        if limit is None:
            limit = self.topk
        
        try:
            # Use pgvector similarity search
            query = text(f"""
                SELECT 
                    i.asin,
                    i.title,
                    i.category,
                    i.brand,
                    i.price,
                    i.rating_avg,
                    i.rating_count,
                    i.category_path,
                    i.attributes,
                    1 - (ie.embedding <=> :embedding) as similarity
                FROM lmrc.items i
                JOIN lmrc.item_embeddings ie ON i.asin = ie.asin
                ORDER BY ie.embedding <=> :embedding
                LIMIT :limit
            """)
            
            # Execute with embedding as string (pgvector format)
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
            result = self.db.execute(
                query,
                {"embedding": embedding_str, "limit": limit}
            )
            
            items = []
            for row in result:
                items.append({
                    "asin": row.asin,
                    "title": row.title,
                    "category": row.category,
                    "brand": row.brand,
                    "price": float(row.price) if row.price else None,
                    "rating_avg": float(row.rating_avg),
                    "rating_count": row.rating_count,
                    "category_path": row.category_path if row.category_path else [],
                    "attributes": row.attributes if row.attributes else {},
                    "similarity": float(row.similarity),
                    "recall_path": "vector"
                })
            
            return items
        except Exception as e:
            logger.error(f"Error searching similar items: {e}")
            raise
    
    def keyword_search(self, keywords: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Search items by keywords using text matching - highly tolerant to find any match"""
        try:
            from sqlalchemy import text, or_
            
            if not keywords:
                return []
            
            logger.info(f"Keyword search with keywords: {keywords}")
            
            # Expand Chinese keywords to English equivalents for better matching
            chinese_to_english = {
                "扬声器": ["speaker"],
                "耳机": ["headphone", "earphone"],
                "音箱": ["speaker"],
                "刀": ["knife"],
                "书": ["book"],
                "电脑": ["computer", "laptop"],
                "手机": ["phone", "mobile"],
                "平板": ["tablet"],
            }
            
            expanded_keywords = list(keywords)
            for keyword in keywords:
                if keyword in chinese_to_english:
                    expanded_keywords.extend(chinese_to_english[keyword])
            
            logger.info(f"Expanded keywords: {expanded_keywords}")
            
            items = []
            seen_asins = set()
            
            # Try multiple matching strategies for robustness
            # Strategy 1: Match any keyword in title
            for keyword in expanded_keywords:
                if len(items) >= limit:
                    break
                    
                query = text("""
                    SELECT 
                        i.asin,
                        i.title,
                        i.category,
                        i.brand,
                        i.price,
                        i.rating_avg,
                        i.rating_count,
                        i.category_path,
                        i.attributes
                    FROM lmrc.items i
                    WHERE i.title ILIKE :keyword
                    ORDER BY i.rating_avg DESC NULLS LAST, i.rating_count DESC
                    LIMIT :limit
                """)
                
                keyword_param = f'%{keyword}%'
                result = self.db.execute(
                    query,
                    {"keyword": keyword_param, "limit": limit}
                )
                
                for row in result:
                    if row.asin not in seen_asins:
                        items.append({
                            "asin": row.asin,
                            "title": row.title,
                            "category": row.category,
                            "brand": row.brand,
                            "price": float(row.price) if row.price else None,
                            "rating_avg": float(row.rating_avg) if row.rating_avg else None,
                            "rating_count": row.rating_count,
                            "category_path": row.category_path if row.category_path else [],
                            "attributes": row.attributes if row.attributes else {},
                            "similarity": 0.8,  # Default high score for keyword matches
                            "recall_path": "keyword"
                        })
                        seen_asins.add(row.asin)
            
            logger.info(f"Keyword search returned {len(items)} results")
            return items
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def category_search(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search items by category"""
        try:
            from sqlalchemy import text
            
            if not category:
                return []
            
            # Search by category with rating-based ranking
            query = text("""
                SELECT 
                    i.asin,
                    i.title,
                    i.category,
                    i.brand,
                    i.price,
                    i.rating_avg,
                    i.rating_count,
                    i.category_path,
                    i.attributes
                FROM lmrc.items i
                WHERE i.category = :category
                    AND i.rating_avg IS NOT NULL
                    AND i.rating_count > 0
                ORDER BY i.rating_avg DESC, i.rating_count DESC
                LIMIT :limit
            """)
            
            result = self.db.execute(
                query,
                {"category": category, "limit": limit}
            )
            
            items = []
            for row in result:
                items.append({
                    "asin": row.asin,
                    "title": row.title,
                    "category": row.category,
                    "brand": row.brand,
                    "price": float(row.price) if row.price else None,
                    "rating_avg": float(row.rating_avg) if row.rating_avg else None,
                    "rating_count": row.rating_count,
                    "category_path": row.category_path if row.category_path else [],
                    "attributes": row.attributes if row.attributes else {},
                    "similarity": row.rating_avg / 5.0 if row.rating_avg else 0.0,
                    "recall_path": "category"
                })
            
            return items
        except Exception as e:
            logger.error(f"Error in category search: {e}")
            return []
    
    def popular_items(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular items as fallback"""
        try:
            from sqlalchemy import text
            
            # Get popular items with high ratings and review counts
            query = text("""
                SELECT 
                    i.asin,
                    i.title,
                    i.category,
                    i.brand,
                    i.price,
                    i.rating_avg,
                    i.rating_count,
                    i.category_path,
                    i.attributes
                FROM lmrc.items i
                WHERE i.rating_avg >= 4.0
                    AND i.rating_count >= 100
                ORDER BY i.rating_count DESC, i.rating_avg DESC
                LIMIT :limit
            """)
            
            result = self.db.execute(
                query,
                {"limit": limit}
            )
            
            items = []
            for row in result:
                items.append({
                    "asin": row.asin,
                    "title": row.title,
                    "category": row.category,
                    "brand": row.brand,
                    "price": float(row.price) if row.price else None,
                    "rating_avg": float(row.rating_avg) if row.rating_avg else None,
                    "rating_count": row.rating_count,
                    "category_path": row.category_path if row.category_path else [],
                    "attributes": row.attributes if row.attributes else {},
                    "similarity": row.rating_avg / 5.0 if row.rating_avg else 0.0,
                    "recall_path": "popular"
                })
            
            return items
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return []
    
    def search_by_review_embedding(self, query_embedding: List[float], limit: int = 30) -> List[Dict[str, Any]]:
        """Search items by similar review embeddings"""
        try:
            from sqlalchemy import text
            
            if not query_embedding:
                return []
            
            # Use pgvector similarity search on review embeddings
            query = text(f"""
                SELECT 
                    rs.asin,
                    i.title,
                    i.category,
                    i.brand,
                    i.price,
                    i.rating_avg,
                    i.rating_count,
                    rs.pros,
                    rs.cons,
                    rs.summary_text,
                    1 - (rs.embedding <=> :embedding) as similarity
                FROM lmrc.reviews_summary rs
                JOIN lmrc.items i ON rs.asin = i.asin
                WHERE rs.embedding IS NOT NULL
                ORDER BY rs.embedding <=> :embedding
                LIMIT :limit
            """)
            
            # Execute with embedding as string
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
            result = self.db.execute(
                query,
                {"embedding": embedding_str, "limit": limit}
            )
            
            items = []
            for row in result:
                items.append({
                    "asin": row.asin,
                    "title": row.title,
                    "category": row.category,
                    "brand": row.brand,
                    "price": float(row.price) if row.price else None,
                    "rating_avg": float(row.rating_avg),
                    "rating_count": row.rating_count,
                    "similarity": float(row.similarity),
                    "recall_path": "review_embedding",
                    "review_summary": {
                        "pros": row.pros if row.pros else [],
                        "cons": row.cons if row.cons else [],
                        "text": row.summary_text[:200] if row.summary_text else ""
                    }
                })
            
            logger.info(f"Review embedding search returned {len(items)} items")
            return items
        except Exception as e:
            logger.error(f"Error searching by review embedding: {e}")
            return []
    
    def multi_path_recommend(self, user_query: str, query_embedding: List[float], keywords: List[str], target_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Multi-path recall: vector + keyword + category + popular with optional category filtering"""
        try:
            all_candidates = []
            seen_asins = set()
            
            logger.info(f"Multi-path recommendation for category: {target_category if target_category else 'Any'}")
            
            # Path 1: Vector similarity search (main path)
            logger.info("Path 1: Vector similarity search")
            vector_results = []
            if query_embedding:  # Only attempt if embedding is not empty
                try:
                    vector_results = self.search_similar_items(query_embedding, limit=self.topk)
                    # Filter by category if specified
                    if target_category:
                        vector_results = [item for item in vector_results if item.get('category') == target_category]
                    logger.info(f"Vector path returned {len(vector_results)} items")
                except Exception as e:
                    logger.warning(f"Vector similarity search failed: {e}")
                    vector_results = []
            else:
                logger.info("Skipping vector search: no embedding available")
            
            # Add vector results with high weight
            for idx, item in enumerate(vector_results):
                if item["asin"] not in seen_asins:
                    item["score"] = item["similarity"] * 0.6 + (1 - idx / max(len(vector_results), 1)) * 0.4
                    all_candidates.append(item)
                    seen_asins.add(item["asin"])
            
            # Path 2: Keyword search
            if keywords:
                logger.info(f"Path 2: Keyword search with {len(keywords)} keywords")
                keyword_results = self.keyword_search(keywords, limit=50)
                # Filter by category if specified
                if target_category:
                    keyword_results = [item for item in keyword_results if item.get('category') == target_category]
                logger.info(f"Keyword path returned {len(keyword_results)} items")
                
                for idx, item in enumerate(keyword_results):
                    if item["asin"] not in seen_asins:
                        # Keyword search has high priority when embedding fails
                        item["score"] = item["similarity"] * 0.7 + (1 - idx / max(len(keyword_results), 1)) * 0.3
                        all_candidates.append(item)
                        seen_asins.add(item["asin"])
                    else:
                        # If already in candidates, boost score for keyword match
                        for candidate in all_candidates:
                            if candidate["asin"] == item["asin"]:
                                candidate["score"] = min(1.0, candidate["score"] + 0.3)
                                break
            
            # Path 3: Category search (extract category from keyword results if no vector results)
            if not vector_results and keyword_results:
                # Try to extract category from keyword results
                categories = {}
                for item in keyword_results[:5]:
                    cat = item.get("category")
                    if cat:
                        categories[cat] = categories.get(cat, 0) + 1
                
                if categories:
                    top_category = max(categories, key=categories.get)
                    logger.info(f"Path 3: Category search for {top_category}")
                    category_results = self.category_search(top_category, limit=15)
                    # Apply category filter if specified
                    if target_category:
                        category_results = [item for item in category_results if item.get('category') == target_category]
                    logger.info(f"Category path returned {len(category_results)} items")
                    
                    for idx, item in enumerate(category_results):
                        if item["asin"] not in seen_asins:
                            item["score"] = item["similarity"] * 0.4 + (1 - idx / max(len(category_results), 1)) * 0.2
                            all_candidates.append(item)
                            seen_asins.add(item["asin"])
            elif vector_results:
                top_category = vector_results[0].get("category")
                if top_category:
                    logger.info(f"Path 3: Category search for {top_category}")
                    category_results = self.category_search(top_category, limit=15)
                    # Apply category filter if specified
                    if target_category:
                        category_results = [item for item in category_results if item.get('category') == target_category]
                    logger.info(f"Category path returned {len(category_results)} items")
                    
                    for idx, item in enumerate(category_results):
                        if item["asin"] not in seen_asins:
                            item["score"] = item["similarity"] * 0.2 + (1 - idx / max(len(category_results), 1)) * 0.1
                            all_candidates.append(item)
                            seen_asins.add(item["asin"])
            
            # Path 4: Review embedding search (NEW - search by similar reviews)
            if query_embedding:
                logger.info("Path 4: Review embedding search")
                review_results = self.search_by_review_embedding(query_embedding, limit=30)
                # Filter by category if specified
                if target_category:
                    review_results = [item for item in review_results if item.get('category') == target_category]
                logger.info(f"Review embedding path returned {len(review_results)} items")
                
                for idx, item in enumerate(review_results):
                    if item["asin"] not in seen_asins:
                        item["score"] = item["similarity"] * 0.5 + (1 - idx / max(len(review_results), 1)) * 0.3
                        all_candidates.append(item)
                        seen_asins.add(item["asin"])
                    else:
                        # If already in candidates, boost score for review match
                        for candidate in all_candidates:
                            if candidate["asin"] == item["asin"]:
                                candidate["score"] = min(1.0, candidate["score"] + 0.2)
                                break
            
            # Path 5: Category-wide fallback (before generic popular items)
            # When specific category is detected but no good results yet, search whole category
            if len(all_candidates) < self.topn * 2 and target_category:
                logger.info(f"Path 5: Category fallback search for {target_category} (current candidates: {len(all_candidates)})")
                category_fallback = self.category_search(target_category, limit=self.topn * 3)
                logger.info(f"Category fallback returned {len(category_fallback)} items")
                
                for idx, item in enumerate(category_fallback):
                    if item["asin"] not in seen_asins:
                        item["score"] = (1 - idx / max(len(category_fallback), 1)) * 0.3
                        all_candidates.append(item)
                        seen_asins.add(item["asin"])
            
            # Path 6: Popular items (final fallback when we have very few results)
            if len(all_candidates) < self.topn * 2:
                logger.info(f"Path 6: Popular items fallback (current candidates: {len(all_candidates)})")
                popular_results = self.popular_items(limit=min(20, self.topn * 2))
                # Apply category filter if specified
                if target_category:
                    popular_results = [item for item in popular_results if item.get('category') == target_category]
                logger.info(f"Popular path returned {len(popular_results)} items")
                
                for idx, item in enumerate(popular_results):
                    if item["asin"] not in seen_asins:
                        pop_weight = (1 - idx / max(len(popular_results), 1)) * 0.05
                        item["score"] = item["similarity"] * 0.1 + pop_weight
                        all_candidates.append(item)
                        seen_asins.add(item["asin"])
            
            # Sort by final score
            all_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            logger.info(f"Total candidates after multi-path recall: {len(all_candidates)}")
            logger.info(f"Recall path distribution: " + 
                       ", ".join([f"{path}: {sum(1 for item in all_candidates if item['recall_path'] == path)}" 
                                 for path in ['vector', 'keyword', 'category', 'popular']]))
            
            return all_candidates[:self.topn]
        except Exception as e:
            logger.error(f"Error in multi-path recommend: {e}")
            raise
    
    def understand_query(self, user_query: str) -> Tuple[str, List[str]]:
        """Use LLM to understand user query and extract intent"""
        # Fast path: skip LLM if disabled for performance
        if not getattr(settings, "enable_llm_intent", True):
            keywords = self._extract_keywords_fallback(user_query)
            return user_query, keywords
        system_prompt = """你是一个专业的电商推荐系统助手。分析用户的自然语言查询，理解其潜在需求。
        
        请以JSON格式返回（必须是有效的JSON）：
        {
            "intent": "用户的核心需求描述（1-2句话，中文）",
            "keywords": ["关键词1", "关键词2", ...]
        }
        
        只返回JSON，不要其他任何内容。"""
        
        try:
            response = ollama_client.generate_text(user_query, system_prompt, temperature=0.3)
            logger.info(f"LLM response for query understanding: {response[:100]}...")
            
            # Parse JSON response
            import json
            import re
            
            # Try to extract JSON from response (in case LLM adds extra text)
            try:
                # First try direct parsing
                data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON block from response
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {response}")
            
            intent = data.get("intent", user_query)
            keywords = data.get("keywords", [])
            
            # Validate and clean keywords
            if not isinstance(keywords, list):
                keywords = []
            keywords = [kw for kw in keywords if isinstance(kw, str) and kw.strip()]
            
            # If keywords are empty, extract them from query directly
            if not keywords:
                keywords = self._extract_keywords_fallback(user_query)
            
            logger.info(f"Query understanding result - Intent: {intent}, Keywords: {keywords}")
            return intent, keywords
        except Exception as e:
            logger.error(f"Error understanding query: {e}")
            # Fallback: use query as-is and extract keywords
            keywords = self._extract_keywords_fallback(user_query)
            return user_query, keywords
    
    def _extract_keywords_fallback(self, query: str) -> List[str]:
        """Fallback method to extract keywords from query without LLM"""
        # Simple keyword extraction: split by common delimiters
        import re
        # Split by Chinese punctuation and spaces
        words = re.split(r'[，。！？、\s]+', query.strip())
        # Filter out empty strings and very short words
        keywords = [w for w in words if len(w) >= 2]
        logger.info(f"Fallback keywords extracted: {keywords}")
        return keywords
    
    def detect_category(self, user_query: str, keywords: List[str]) -> Optional[str]:
        """Detect product category from user query using LLM or keyword matching"""
        try:
            # First try category mapping using keywords
            detected_category = self._category_mapping_from_keywords(keywords)
            if detected_category:
                logger.info(f"Category detected from keywords: {detected_category}")
                return detected_category
            
            # If keyword matching fails, use LLM to detect category
            if not getattr(settings, "enable_llm_category_fallback", True):
                return None
            system_prompt = """你是一个电商产品分类助手。根据用户的查询，识别出用户想要购买的产品类别。
            
            可能的类别包括：
            - Electronics: 电子产品、电脑、手机等
            - Home_and_Kitchen: 家庭和厨房用品
            - Books: 书籍
            - Clothing: 服装鞋帽
            - Sports: 运动户外
            - Toys: 玩具游戏
            - Beauty: 美妆个护
            - Automotive: 汽车用品
            - Pet_Supplies: 宠物用品
            - Software: 软件
            - Office_Products: 办公用品
            
            请只返回一个类别名称，不要其他内容。如果无法确定，返回 'General'。"""
            
            response = ollama_client.generate_text(user_query, system_prompt, temperature=0.2)
            category = response.strip().upper()
            
            # Validate category exists in database
            if self._validate_category(category):
                logger.info(f"Category detected from LLM: {category}")
                return category
            
            logger.info(f"LLM returned invalid category: {category}")
            return None
            
        except Exception as e:
            logger.warning(f"Error detecting category: {e}")
            return None
    
    def _category_mapping_from_keywords(self, keywords: List[str]) -> Optional[str]:
        """Map keywords to product categories"""
        # Build keyword-category mappings (Chinese keywords + English equivalents)
        category_keywords = {
            # Electronics/Computer
            "Electronics": ["电脑", "笔记本", "laptop", "computer", "手机", "phone", "平板", "tablet",
                          "显示器", "monitor", "键盘", "鼠标", "mouse", "硬盘", "内存", "GPU", "CPU",
                          "音箱", "speaker", "耳机", "headphone", "earphone", "音频", "扬声器", "蓝牙", "bluetooth"],
            
            # Books
            "Books": ["书", "书籍", "图书", "小说", "教科书", "教材", "编程书", "python", "java",
                     "数据结构", "算法", "深度学习", "机器学习"],
            
            # Home and Kitchen
            "Home_and_Kitchen": ["厨房", "锅", "刀具", "刀片", "砧板", "灶", "冰箱", "微波炉",
                               "家居", "家具", "装饰", "家里", "knife", "kitchen"],
            
            # Clothing
            "Clothing_Shoes_and_Jewelry": ["衣服", "衣", "裤子", "鞋", "衣裤", "服装", "T恤", "裙子",
                                          "外套", "夹克", "珠宝", "项链", "shoes", "dress"],
            
            # Sports
            "Sports_and_Outdoors": ["运动", "户外", "足球", "篮球", "羽毛球", "登山", "骑行",
                                   "游泳", "瑜伽", "健身", "sports"],
            
            # Toys
            "Toys_and_Games": ["玩具", "游戏", "积木", "拼图", "骰子", "棋牌", "toys", "games"],
            
            # Beauty
            "Beauty_and_Personal_Care": ["美妆", "护肤", "化妆", "面膜", "口红", "粉底", "护肤品",
                                        "洗面奶", "沐浴露", "beauty", "skincare"],
            
            # Pet Supplies
            "Pet_Supplies": ["宠物", "狗", "猫", "鱼", "鸟", "狗粮", "猫粮", "宠物用品", "pet", "dog", "cat"],
            
            # Automotive
            "Automotive": ["汽车", "车", "轮胎", "机油", "配件", "雨刷", "automotive", "car"],
            
            # Software
            "Software": ["软件", "程序", "应用", "app", "系统", "software"],
        }
        
        # Also map Chinese terms to English keywords for better search
        chinese_to_english = {
            "扬声器": ["speaker"],
            "耳机": ["headphone", "earphone"],
            "音箱": ["speaker"],
            "刀": ["knife"],
            "书": ["book"],
        }
        
        # Check if any keyword matches
        for category, keyword_list in category_keywords.items():
            for keyword in keywords:
                for category_keyword in keyword_list:
                    if keyword.lower() == category_keyword.lower() or \
                       category_keyword.lower() in keyword.lower():
                        logger.info(f"Keyword '{keyword}' matched to category '{category}'")
                        return category
        
        return None
    
    def _validate_category(self, category: str) -> bool:
        """Check if category exists in database"""
        try:
            from sqlalchemy import text
            result = self.db.execute(
                text("SELECT COUNT(*) FROM lmrc.items WHERE category = :cat"),
                {"cat": category}
            )
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.warning(f"Error validating category '{category}': {e}")
            return False
    
    def generate_recommendations(self, user_query: str) -> List[Dict[str, Any]]:
        """Generate recommendations based on user query using multi-path recall with category detection"""
        try:
            # Step 1: Understand the query
            intent, keywords = self.understand_query(user_query)
            logger.info(f"Query intent: {intent}, keywords: {keywords}")
            
            # Step 1b: Detect product category from query
            target_category = self.detect_category(user_query, keywords)
            logger.info(f"Detected category: {target_category}")
            
            # Step 2: Create embedding for the query
            # Use the original query if intent understanding failed
            text_to_embed = intent if intent != user_query else user_query
            
            query_embedding: List[float] = []
            if getattr(settings, "enable_embeddings", True):
                try:
                    query_embedding = ollama_client.embed_text(text_to_embed)
                    if not query_embedding:
                        raise ValueError("Empty embedding returned")
                    logger.info(f"Embedding created successfully, dimension: {len(query_embedding)}")
                except Exception as e:
                    logger.warning(f"Failed to create embedding for '{text_to_embed}': {e}")
                    logger.info("Falling back to keyword-only search")
                    # If embedding fails, try with original query
                    try:
                        query_embedding = ollama_client.embed_text(user_query)
                        if not query_embedding:
                            logger.warning("Embedding for original query also failed, will rely on keyword search")
                            query_embedding = []
                    except:
                        logger.warning("All embedding attempts failed, will rely on keyword search")
                        query_embedding = []
            else:
                logger.info("Embeddings disabled by config; using keyword search only")
            
            # Step 3: Multi-path recall (vector + keyword + category + popular)
            # Pass the detected category for filtering
            top_items = self.multi_path_recommend(user_query, query_embedding, keywords, target_category)
            logger.info(f"Multi-path recall returned {len(top_items)} items")
            
            if not top_items:
                logger.warning("Multi-path recall returned no items, returning popular items")
                top_items = self.popular_items(limit=self.topn)
            
            return top_items
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def get_item_details(self, asin: str) -> Dict[str, Any]:
        """Get detailed information about an item"""
        try:
            item = self.db.query(Item).filter(Item.asin == asin).first()
            if not item:
                return None
            
            return {
                "asin": item.asin,
                "title": item.title,
                "category": item.category,
                "brand": item.brand,
                "price": float(item.price) if item.price else None,
                "rating_avg": item.rating_avg,
                "rating_count": item.rating_count,
                "category_path": item.category_path,
                "attributes": item.attributes if item.attributes else {}
            }
        except Exception as e:
            logger.error(f"Error getting item details: {e}")
            raise
