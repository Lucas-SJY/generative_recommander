"""Development and testing utilities"""
import json
from backend.database import SessionLocal
from backend.models import Item
from backend.recommendation_engine import RecommendationEngine

# Test queries for development
TEST_QUERIES = [
    "我想要一个轻便的无线充电宝",
    "高性能游戏笔记本，价格在 8000 以内",
    "什么运动鞋比较舒服，用于日常穿着",
    "我需要一个学生用的平板电脑",
    "找一个高质量的咖啡机，家用的",
    "儿童教育平板，要性价比好的",
    "职业摄影师用的相机包",
]


def test_recommendation(query: str):
    """Test a single recommendation query"""
    db = SessionLocal()
    try:
        rec_engine = RecommendationEngine(db)
        
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        # Get recommendations
        recommendations = rec_engine.generate_recommendations(query)
        
        print(f"\nFound {len(recommendations)} recommendations:")
        print()
        
        for i, item in enumerate(recommendations, 1):
            print(f"{i}. {item['title'][:50]}")
            print(f"   ASIN: {item['asin']}")
            print(f"   Category: {item['category']}")
            print(f"   Price: ${item['price']}" if item['price'] else "   Price: N/A")
            print(f"   Rating: {item['rating_avg']:.1f} ({item['rating_count']} reviews)")
            print(f"   Similarity: {item['similarity']:.2%}")
            print()
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close()


def test_all_queries():
    """Test all sample queries"""
    for query in TEST_QUERIES:
        test_recommendation(query)


def count_items():
    """Count items in database"""
    db = SessionLocal()
    try:
        count = db.query(Item).count()
        print(f"Total items in database: {count}")
        
        # Get category breakdown
        items_by_category = db.query(Item.category, Item.__count__).group_by(Item.category).all()
        print("\nItems by category:")
        for cat, cnt in items_by_category:
            if cnt > 0:
                print(f"  {cat}: {cnt}")
    
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        test_recommendation(query)
    else:
        print("Development Testing Utilities")
        print("="*60)
        print("\nUsage:")
        print("  python dev_test.py <query>    - Test a single query")
        print("  python dev_test.py --all      - Test all sample queries")
        print("  python dev_test.py --count    - Count items in database")
        print("\nExamples:")
        print("  python dev_test.py 我想要一个轻便的无线充电宝")
        print("  python dev_test.py --all")
        print("  python dev_test.py --count")
