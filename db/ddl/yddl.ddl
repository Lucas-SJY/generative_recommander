-- 1) DB: recsys
-- CREATE DATABASE recsys;
-- \c recsys;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS items (
  asin TEXT PRIMARY KEY,
  parent_asin TEXT,
  title TEXT NOT NULL,
  category TEXT,
  category_path TEXT,
  brand TEXT,
  price NUMERIC,
  rating_avg REAL DEFAULT 0,
  rating_count INT DEFAULT 0,
  attributes JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS reviews_summary (
  asin TEXT PRIMARY KEY REFERENCES items(asin) ON DELETE CASCADE,
  pros JSONB DEFAULT '{}'::jsonb,
  cons JSONB DEFAULT '{}'::jsonb,
  summary_text TEXT
);

-- nomic-embed-text 常见维度 768（如不同请改这里 + 检索与写入）
CREATE TABLE IF NOT EXISTS item_embeddings (
  asin TEXT PRIMARY KEY REFERENCES items(asin) ON DELETE CASCADE,
  embedding VECTOR(768) NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT,
  memory_json JSONB DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events (
  event_id BIGSERIAL PRIMARY KEY,
  session_id TEXT,
  user_id TEXT,
  asin TEXT,
  event_type TEXT NOT NULL,
  payload JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- HNSW 索引（如果你的 pgvector 太老不支持 hnsw，把这行改成 ivfflat）
CREATE INDEX IF NOT EXISTS idx_item_embeddings_hnsw
  ON item_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_items_title_trgm
  ON items USING gin (title gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_parent_asin ON items(parent_asin);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
