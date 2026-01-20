#!/usr/bin/env python3
"""Test script for category detection feature"""
import sys
import logging
from backend.database import init_db, get_db
from backend.recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_category_detection():
    """Test the new category detection feature"""
    print("\n" + "="*80)
    print("CATEGORY DETECTION TEST")
    print("="*80)
    
    try:
        init_db()
        db = next(get_db())
        rec_engine = RecommendationEngine(db)
        
        # Test cases with different product categories
        test_cases = [
            {
                "query": "我需要一台笔记本电脑用于编程",
                "expected_category": "Electronics"
            },
            {
                "query": "推荐一个好的蓝牙音箱",
                "expected_category": "Electronics"
            },
            {
                "query": "我想要一本Python编程书",
                "expected_category": "Books"
            },
            {
                "query": "找一个不锈钢刀片",
                "expected_category": "Home_and_Kitchen"
            },
            {
                "query": "我需要运动装备进行登山",
                "expected_category": "Sports_and_Outdoors"
            },
            {
                "query": "帮我选择一个狗粮品牌",
                "expected_category": "Pet_Supplies"
            },
        ]
        
        for test_case in test_cases:
            query = test_case["query"]
            expected = test_case["expected_category"]
            
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"Expected Category: {expected}")
            print("="*60)
            
            # Test category detection
            intent, keywords = rec_engine.understand_query(query)
            print(f"  Intent: {intent}")
            print(f"  Keywords: {keywords}")
            
            detected_category = rec_engine.detect_category(query, keywords)
            print(f"  Detected Category: {detected_category}")
            
            if detected_category == expected:
                print("  ✓ PASS")
            elif detected_category:
                print(f"  ⚠ Category detected but different from expected")
            else:
                print("  ✗ FAIL - Category not detected")
            
            # Test recommendations with category filtering
            print(f"\n  Generating recommendations with category filtering...")
            try:
                recommendations = rec_engine.generate_recommendations(query)
                print(f"  Total recommendations: {len(recommendations)}")
                
                # Check if recommendations match detected category
                if detected_category:
                    matching_count = sum(1 for item in recommendations if item.get('category') == detected_category)
                    print(f"  Items matching detected category: {matching_count}/{len(recommendations)}")
                    
                    print(f"\n  Top 3 recommendations:")
                    for i, item in enumerate(recommendations[:3], 1):
                        print(f"    [{i}] {item['title'][:50]}...")
                        print(f"        Category: {item['category']}")
                        print(f"        Score: {item['score']:.3f}")
                
            except Exception as e:
                print(f"  Error generating recommendations: {e}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"Error in category detection test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_category_detection()
