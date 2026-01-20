#!/usr/bin/env python3
"""Diagnostic script to check database contents and recommendation paths"""
import sys
import logging
from backend.database import init_db, get_db
from backend.recommendation_engine import RecommendationEngine
from backend.ollama_client import ollama_client
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Check database contents"""
    print("\n" + "="*80)
    print("DATABASE DIAGNOSTIC CHECK")
    print("="*80)
    
    try:
        init_db()
        db = next(get_db())
        
        # Check total items
        result = db.execute(text("SELECT COUNT(*) as count FROM lmrc.items"))
        total_items = result.scalar()
        print(f"\nTotal items in database: {total_items}")
        
        # Check categories
        result = db.execute(text("""
            SELECT category, COUNT(*) as count 
            FROM lmrc.items 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 10
        """))
        
        print("\nTop 10 categories:")
        for row in result:
            print(f"  {row.category}: {row.count} items")
        
        # Check popular items
        result = db.execute(text("""
            SELECT title, category, rating_avg, rating_count 
            FROM lmrc.items 
            WHERE rating_avg >= 4.0 AND rating_count >= 100
            ORDER BY rating_count DESC 
            LIMIT 5
        """))
        
        print("\nTop popular items (rating >= 4.0, reviews >= 100):")
        for i, row in enumerate(result, 1):
            print(f"  [{i}] {row.title[:50]}... ({row.category})")
            print(f"      Rating: {row.rating_avg}/5 ({row.rating_count} reviews)")
        
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()


def test_keyword_search():
    """Test keyword search functionality"""
    print("\n" + "="*80)
    print("KEYWORD SEARCH TEST")
    print("="*80)
    
    try:
        db = next(get_db())
        rec_engine = RecommendationEngine(db)
        
        test_keywords = [
            ["电脑", "笔记本"],
            ["音箱", "speaker"],
            ["刀片", "刀"],
            ["书", "书籍"],
        ]
        
        for keywords in test_keywords:
            print(f"\nSearching for keywords: {keywords}")
            results = rec_engine.keyword_search(keywords, limit=5)
            print(f"  Found {len(results)} results")
            for i, item in enumerate(results[:3], 1):
                print(f"    [{i}] {item['title'][:40]}...")
                print(f"        Category: {item['category']}, Score: {item['similarity']:.2f}")
        
    except Exception as e:
        print(f"Error testing keyword search: {e}")
        import traceback
        traceback.print_exc()


def test_full_recommendation_flow():
    """Test full recommendation flow"""
    print("\n" + "="*80)
    print("FULL RECOMMENDATION FLOW TEST")
    print("="*80)
    
    try:
        db = next(get_db())
        rec_engine = RecommendationEngine(db)
        
        test_queries = [
            "我需要一台笔记本电脑用于编程",
            "推荐一个好的蓝牙音箱",
            "我想要一本Python编程书",
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print("="*60)
            
            # Step 1: Understand query
            print("\n[Step 1] Query Understanding:")
            intent, keywords = rec_engine.understand_query(query)
            print(f"  Intent: {intent}")
            print(f"  Keywords: {keywords}")
            
            # Step 2: Create embedding
            print("\n[Step 2] Embedding Generation:")
            try:
                embedding = ollama_client.embed_text(intent if intent != query else query)
                print(f"  Embedding dimension: {len(embedding) if embedding else 0}")
                print(f"  Valid: {'✓' if embedding else '✗'}")
            except Exception as e:
                print(f"  Error: {e}")
                embedding = []
            
            # Step 3: Generate recommendations
            print("\n[Step 3] Recommendations:")
            try:
                recommendations = rec_engine.generate_recommendations(query)
                print(f"  Total recommendations: {len(recommendations)}")
                
                # Group by recall path
                path_dist = {}
                for item in recommendations:
                    path = item.get('recall_path', 'unknown')
                    path_dist[path] = path_dist.get(path, 0) + 1
                
                print(f"  Recall path distribution:")
                for path, count in sorted(path_dist.items()):
                    print(f"    {path}: {count}")
                
                print(f"\n  Top 3 recommendations:")
                for i, item in enumerate(recommendations[:3], 1):
                    print(f"    [{i}] {item['title'][:40]}...")
                    print(f"        Category: {item['category']}, Score: {item['score']:.3f}")
                    print(f"        Path: {item['recall_path']}, Similarity: {item['similarity']:.3f}")
                
            except Exception as e:
                print(f"  Error generating recommendations: {e}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"Error in recommendation flow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_database()
    test_keyword_search()
    test_full_recommendation_flow()
    
    print("\n" + "="*80)
    print("DIAGNOSTIC CHECK COMPLETE")
    print("="*80)
