"""Data loading script for Amazon reviews"""
import json
import logging
import sys
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, engine, Base, init_db
from backend.models import Item, ItemEmbedding, ReviewSummary
from backend.ollama_client import ollama_client
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure extensions and schema, then create tables
init_db()
Base.metadata.create_all(bind=engine)


def load_metadata(db: Session, meta_dir: Path):
    """Load item metadata from meta_categories files"""
    logger.info(f"Loading metadata from {meta_dir}")
    
    meta_files = list(meta_dir.glob("meta_*.jsonl"))
    logger.info(f"Found {len(meta_files)} metadata files")
    
    total_items = 0
    for meta_file in meta_files:
        category = meta_file.stem.replace("meta_", "")
        logger.info(f"Processing {category}...")
        
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                for line in tqdm(f, desc=f"Loading {category}"):
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        # Some files lack 'asin', use parent_asin as fallback
                        asin = data.get('asin') or data.get('parent_asin')
                        
                        if not asin:
                            continue
                        
                        # Title is required (NOT NULL constraint)
                        title = data.get('title')
                        if not title:
                            continue
                        
                        # Check if item already exists
                        existing = db.query(Item).filter(Item.asin == asin).first()
                        if existing:
                            continue
                        
                        # Normalize fields from dataset keys
                        rating_avg = data.get('avg_rating') or data.get('average_rating') or 0
                        category_path = data.get('category') or data.get('categories') or ''
                        price = data.get('price')
                        if isinstance(price, str):
                            try:
                                price = float(price)
                            except Exception:
                                price = None
                        
                        item = Item(
                            asin=asin,
                            parent_asin=data.get('parent_asin'),
                            title=title,
                            category=category,
                            category_path=category_path,
                            brand=data.get('brand') or data.get('store'),
                            price=price,
                            rating_avg=rating_avg,
                            rating_count=data.get('rating_number', 0),
                            attributes=data.get('attributes', {}) or data.get('details', {})
                        )
                        
                        db.add(item)
                        total_items += 1
                        
                        # Commit in batches
                        if total_items % 1000 == 0:
                            db.commit()
                            logger.info(f"Committed {total_items} items")
                    
                    except Exception as e:
                        logger.error(f"Error processing line in {category}: {e}")
                        db.rollback()
                        continue
        
        except Exception as e:
            logger.error(f"Error processing {meta_file}: {e}")
            continue
    
    db.commit()
    logger.info(f"Metadata loading completed: {total_items} items")
    return total_items


def load_reviews(db: Session, review_dir: Path):
    """Load review data and aggregate into review_summary"""
    logger.info(f"Loading reviews from {review_dir}")
    
    review_files = list(review_dir.glob("*.jsonl"))
    logger.info(f"Found {len(review_files)} review files")
    
    total_reviews = 0
    skipped_duplicates = 0
    skipped_invalid = 0
    
    # Aggregate reviews by asin
    review_aggregates = {}  # {asin: {pros: [], cons: [], reviews: []}}
    
    for review_file in review_files:
        category = review_file.stem
        logger.info(f"Processing category: {category}")
        
        file_reviews = 0
        file_invalid = 0
        
        try:
            with open(review_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(tqdm(f, desc=f"[{category}]"), 1):
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        asin = data.get('asin') or data.get('parent_asin')
                        
                        if not asin:
                            file_invalid += 1
                            continue
                        
                        # Check if item exists
                        item_exists = db.query(Item).filter(Item.asin == asin).first()
                        if not item_exists:
                            file_invalid += 1
                            continue
                        
                        # Initialize aggregation for this asin
                        if asin not in review_aggregates:
                            review_aggregates[asin] = {
                                'pros': [],
                                'cons': [],
                                'reviews': []
                            }
                        
                        # Extract review text
                        text = data.get('text') or data.get('review_text')
                        if text:
                            # Limit to 200 chars per review snippet
                            review_aggregates[asin]['reviews'].append(text[:200])
                        
                        # Try to extract pros/cons if available
                        if 'pros' in data and data.get('pros'):
                            pros_list = data.get('pros') if isinstance(data.get('pros'), list) else [data.get('pros')]
                            review_aggregates[asin]['pros'].extend(pros_list)
                        
                        if 'cons' in data and data.get('cons'):
                            cons_list = data.get('cons') if isinstance(data.get('cons'), list) else [data.get('cons')]
                            review_aggregates[asin]['cons'].extend(cons_list)
                        
                        file_reviews += 1
                        total_reviews += 1
                    
                    except Exception as e:
                        logger.error(f"[{category}] Error at line {line_num}: {e}")
                        file_invalid += 1
                        continue
            
            skipped_invalid += file_invalid
            logger.info(
                f"[{category}] Complete: {file_reviews} reviews processed, {file_invalid} invalid skipped"
            )
        
        except Exception as e:
            logger.error(f"Error processing {review_file}: {e}")
            continue
    
    # Save aggregated reviews to database
    logger.info(f"Saving {len(review_aggregates)} items with aggregated reviews...")
    
    for asin, agg_data in tqdm(review_aggregates.items(), desc="Saving reviews"):
        try:
            # Check if already exists
            existing = db.query(ReviewSummary).filter(ReviewSummary.asin == asin).first()
            if existing:
                skipped_duplicates += 1
                continue
            
            # Remove duplicates and limit to top 10
            pros_list = list(dict.fromkeys(agg_data['pros']))[:10]  # Remove duplicates, keep order, limit 10
            cons_list = list(dict.fromkeys(agg_data['cons']))[:10]
            
            # Aggregate review text - join first 5 reviews with separator
            summary_text = " | ".join(agg_data['reviews'][:5]) if agg_data['reviews'] else None
            
            review_summary = ReviewSummary(
                asin=asin,
                pros=pros_list,
                cons=cons_list,
                summary_text=summary_text
            )
            
            db.add(review_summary)
            
            # Commit in batches
            if (asg_count := sum(1 for _ in db.query(ReviewSummary))) % 1000 == 0:
                db.commit()
                logger.info(f"Committed {asg_count} review summaries")
        
        except Exception as e:
            logger.error(f"Error saving review summary for {asin}: {e}")
            db.rollback()
            continue
    
    db.commit()
    logger.info(
        f"Review loading completed: {total_reviews} reviews processed into "
        f"{len(review_aggregates)} summaries, {skipped_duplicates} duplicates skipped, "
        f"{skipped_invalid} invalid skipped"
    )
    return total_reviews


def load_review_embeddings(db: Session, batch_size: int = 32):
    """Generate and store embeddings for review summaries without embeddings"""
    logger.info("Loading review embeddings...")
    
    # Find review summaries without embeddings
    reviews_without_embeddings = db.query(ReviewSummary).filter(
        ReviewSummary.embedding == None
    ).all()
    
    logger.info(f"Found {len(reviews_without_embeddings)} reviews without embeddings")
    
    if not reviews_without_embeddings:
        logger.info("All reviews already have embeddings")
        return
    
    # Process in batches
    for i in tqdm(range(0, len(reviews_without_embeddings), batch_size), desc="Embedding reviews"):
        batch = reviews_without_embeddings[i:i+batch_size]
        
        # Create text for embedding from summary + pros/cons
        texts = []
        for review in batch:
            # Combine pros, cons, and summary text
            pros_text = " ".join(review.pros) if review.pros and isinstance(review.pros, list) else ""
            cons_text = " ".join(review.cons) if review.cons and isinstance(review.cons, list) else ""
            summary_text = review.summary_text or ""
            
            combined_text = f"{pros_text} {cons_text} {summary_text}".strip()
            if not combined_text:
                # Fallback: use asin if no text available
                combined_text = review.asin
            
            texts.append(combined_text[:1000])  # Limit to 1000 chars
        
        try:
            # Get embeddings
            embeddings = ollama_client.embed_batch(texts)
            
            # Store embeddings
            for review, embedding in zip(batch, embeddings):
                review.embedding = embedding
                review.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Processed {i + len(batch)} reviews")
        
        except Exception as e:
            logger.error(f"Error processing review embeddings batch: {e}")
            db.rollback()
            continue
    
    logger.info("Review embedding loading completed!")


def load_embeddings(db: Session, batch_size: int = 32):
    """Generate and store embeddings for items without embeddings"""
    logger.info("Loading embeddings...")
    
    # Find items without embeddings
    items_without_embeddings = db.query(Item).outerjoin(ItemEmbedding).filter(
        ItemEmbedding.asin == None
    ).all()
    
    logger.info(f"Found {len(items_without_embeddings)} items without embeddings")
    
    if not items_without_embeddings:
        logger.info("All items already have embeddings")
        return
    
    # Process in batches
    for i in tqdm(range(0, len(items_without_embeddings), batch_size)):
        batch = items_without_embeddings[i:i+batch_size]
        
        # Create text for embedding
        texts = []
        for item in batch:
            text = f"{item.title} {item.brand or ''} {item.category or ''}".strip()
            texts.append(text)
        
        try:
            # Get embeddings
            embeddings = ollama_client.embed_batch(texts)
            
            # Store embeddings
            for item, embedding in zip(batch, embeddings):
                item_emb = ItemEmbedding(
                    asin=item.asin,
                    embedding=embedding
                )
                db.add(item_emb)
            
            db.commit()
            logger.info(f"Processed {i + len(batch)} items")
        
        except Exception as e:
            logger.error(f"Error processing embeddings batch: {e}")
            db.rollback()
            continue


def main():
    """Main loading function"""
    db = SessionLocal()
    
    try:
        # Load metadata
        data_dir = Path("/home/lucas/ucsc/yi/dataset/raw")
        meta_dir = data_dir / "meta_categories"
        
        if meta_dir.exists():
            load_metadata(db, meta_dir)
        else:
            logger.warning(f"Metadata directory not found: {meta_dir}")
        
        # Load reviews
        review_dir = data_dir / "review_categories"
        if review_dir.exists():
            load_reviews(db, review_dir)
        else:
            logger.warning(f"Review directory not found: {review_dir}")
        
        # Load embeddings for items
        load_embeddings(db)
        
        # Load embeddings for reviews
        load_review_embeddings(db)
        
        logger.info("Data loading completed successfully!")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
