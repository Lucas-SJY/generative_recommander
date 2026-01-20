#!/usr/bin/env python3
"""Test script to verify the recommendation engine fixes"""
import sys
import json
from backend.database import get_db, init_db
from backend.recommendation_engine import RecommendationEngine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test queries
TEST_QUERIES = [
    "我需要一台用于电子工程学习的笔记本电脑",
    "找一个好的音箱",
    "推荐一本Python编程书",
    "我想要一个用于编程的高性能电脑",
    "寻找电子产品",
]

def test_recommendations():
    """Test the recommendation engine with various queries"""
    print("=" * 80)
    print("Testing Recommendation Engine Fixes")
    print("=" * 80)
    
    try:
        # Initialize database
        init_db()
        
        # Get database session
        db = next(get_db())
        
        # Initialize recommendation engine
        rec_engine = RecommendationEngine(db)
        
        # Test each query
        for i, query in enumerate(TEST_QUERIES, 1):
            print(f"\n{'='*80}")
            print(f"Test {i}: {query}")
            print("="*80)
            
            try:
                # Test query understanding
                print("\n[1] Query Understanding:")
                intent, keywords = rec_engine.understand_query(query)
                print(f"   Intent: {intent}")
                print(f"   Keywords: {keywords}")
                
                # Test embedding generation
                print("\n[2] Embedding Generation:")
                from backend.ollama_client import ollama_client
                embedding = ollama_client.embed_text(intent if intent != query else query)
                print(f"   Embedding dimension: {len(embedding) if embedding else 0}")
                print(f"   Embedding valid: {bool(embedding)}")
                
                # Test recommendations
                print("\n[3] Recommendations:")
                recommendations = rec_engine.generate_recommendations(query)
                
                print(f"   Total items: {len(recommendations)}")
                print(f"   Top 3 recommendations:")
                
                for j, item in enumerate(recommendations[:3], 1):
                    print(f"\n   [{j}] {item.get('title', 'N/A')}")
                    print(f"       Category: {item.get('category', 'N/A')}")
                    print(f"       Brand: {item.get('brand', 'N/A')}")
                    print(f"       Rating: {item.get('rating_avg', 'N/A')}/5.0")
                    print(f"       Price: ${item.get('price', 'N/A')}")
                    print(f"       Recall Path: {item.get('recall_path', 'N/A')}")
                    print(f"       Similarity: {item.get('similarity', 'N/A'):.4f}")
                
                print("\n✓ Test passed")
                
            except Exception as e:
                print(f"\n✗ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*80}")
        print("All tests completed!")
        print("="*80)
        
    except Exception as e:
        print(f"Error initializing tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_recommendations()
