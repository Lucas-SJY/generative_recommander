# Amazon Recommendation System

一个基于 LLM 和向量相似性搜索的电商推荐系统。用户可以用自然语言描述需求，系统会使用大语言模型理解意图，然后通过**自动类别检测**和**多路径推荐**推荐最合适的商品。

## 🎯 核心特性（最新版本）

✨ **自动类别检测**：自动识别用户要购买的产品类别
✨ **智能过滤**：只推荐检测到的类别中的产品
✨ **多路径推荐**：使用向量搜索、关键词搜索、分类搜索等多种策略
✨ **中英文支持**：完全支持中文和英文的混合查询

## 🚀 快速开始

```bash
# 1. 激活环境
conda activate yi

# 2. 启动服务
cd /home/lucas/ucsc/yi
bash start_server.sh

# 3. 打开浏览器访问
# http://10.0.0.134:8001
```

## 📚 文档（推荐按顺序阅读）

| 优先级 | 文档 | 内容 |
|-------|------|------|
| ⭐⭐⭐ | [QUICK_START.md](QUICK_START.md) | 一分钟快速入门 |
| ⭐⭐ | [SETUP_GUIDE.md](SETUP_GUIDE.md) | 完整环境配置指南 |
| ⭐ | [CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) | 类别检测功能详解 |
| - | [ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md) | 问题诊断和修复 |
| - | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 完整项目概览 |

## 🎨 使用示例

### 查询电脑产品
```
用户：我需要一台笔记本电脑用于编程
系统：📁 检测到商品类别: Electronics
推荐：MacBook Pro、Dell XPS、ASUS VivoBook...
```

### 查询书籍
```
用户：推荐一本编程书
系统：📁 检测到商品类别: Books  
推荐：Python Crash Course、Fluent Python...
```

### 查询厨房用品
```
用户：我需要一个不锈钢刀片
系统：📁 检测到商品类别: Home_and_Kitchen
推荐：不锈钢刀具套装、主厨刀...
```

## 🔧 系统检查

运行诊断脚本：
```bash
cd /home/lucas/ucsc/yi
bash run_diagnosis.sh
```

## 📋 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端 (Frontend)                          │
│                   HTML + JavaScript                         │
│          (8001端口，交互式Web界面)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 后端 (Backend)                              │
│              FastAPI + SQLAlchemy                           │
│                    (8000端口)                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  推荐引擎         │  │  对话处理         │               │
│  │ - 向量搜索       │  │ - LLM 理解       │               │
│  │ - 相似度计算     │  │ - 生成回复       │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │  Ollama LLM │  │   Ollama    │  │ PostgreSQL  │
   │(qwen2.5:14b│  │  Embeddings │  │ + pgvector  │
   │   模型)     │  │(nomic-embed)│  │ (向量库)    │
   └─────────────┘  └─────────────┘  └─────────────┘
```

## 功能特性

- 🤖 **LLM 理解**: 使用 Qwen2.5 14B 理解用户自然语言意图
- 🔍 **向量搜索**: 基于 pgvector 的高效向量相似性搜索
- 💬 **多轮对话**: 支持会话管理和上下文记忆
- 📊 **实时推荐**: 快速返回最相关的商品推荐
- 🌐 **Web 界面**: 美观的响应式前端界面

## 前提条件

1. **PostgreSQL 数据库** (已创建 lmrc schema)
2. **Ollama** (本地部署)
   - 模型: `qwen2.5:14b`
   - 模型: `nomic-embed-text`
3. **Python 3.9+**

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件 (已预设):

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@0.0.0.0:5432/recsys?options=-csearch_path%3Dlmrc,public
OLLAMA_BASE_URL=http://0.0.0.0:11434
LLM_MODEL=qwen2.5:14b
EMBED_MODEL=nomic-embed-text
RETRIEVE_TOPK=80
RETURN_TOPN=8
OLLAMA_TIMEOUT_S=60
```

### 3. 准备数据

#### 启动 Ollama

```bash
ollama serve
```

#### 在另一个终端加载模型

```bash
# 拉取 Qwen 模型 (首次需要)
ollama pull qwen2.5:14b

# 拉取 embedding 模型 (首次需要)
ollama pull nomic-embed-text
```

#### 加载 Amazon 数据

```bash
python backend/load_data.py
```

这个脚本会:
1. 从 `dataset/raw/meta_categories/` 加载产品元数据
2. 使用 Ollama embedding 模型生成向量表示
3. 存储到 PostgreSQL + pgvector

## 快速开始

### 方式 1: 使用启动脚本

```bash
chmod +x start_services.sh
./start_services.sh
```

### 方式 2: 手动启动

**终端 1 - 启动后端 API:**

```bash
python -m backend.main
```

后端运行在: `http://0.0.0.0:8000`
API 文档: `http://0.0.0.0:8000/docs`

**终端 2 - 启动前端服务:**

```bash
python -m frontend.main
```

前端运行在: `http://0.0.0.0:8001`

### 在浏览器中访问

打开浏览器访问: `http://0.0.0.0:8001`

## API 端点

### 1. 获取推荐

```bash
POST /api/recommend
Content-Type: application/json

{
  "query": "我想要一个轻便的无线充电宝",
  "session_id": "optional",
  "user_id": "optional"
}

Response:
{
  "query": "我想要一个轻便的无线充电宝",
  "intent": "寻找轻便、易携带的无线充电设备",
  "session_id": "...",
  "recommendations": [
    {
      "asin": "...",
      "title": "...",
      "category": "...",
      "brand": "...",
      "price": 99.99,
      "rating_avg": 4.5,
      "rating_count": 1000,
      "similarity": 0.85
    }
  ]
}
```

### 2. 对话接口

```bash
POST /api/chat
Content-Type: application/json

{
  "session_id": "...",
  "message": "我需要一个高性能的游戏笔记本"
}

Response:
{
  "session_id": "...",
  "assistant_response": "我为您找到了几款高性能游戏本...",
  "recommendations": [...]
}
```

### 3. 获取商品详情

```bash
POST /api/item-details
Content-Type: application/json

{
  "asin": "B0..."
}

Response:
{
  "asin": "...",
  "title": "...",
  "category": "...",
  "brand": "...",
  "price": 99.99,
  "rating_avg": 4.5,
  "rating_count": 1000,
  "category_path": "...",
  "attributes": {...}
}
```

## 项目结构

```
yi/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 主应用
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接和初始化
│   ├── models.py               # SQLAlchemy ORM 模型
│   ├── ollama_client.py        # Ollama API 客户端
│   ├── recommendation_engine.py # 推荐引擎核心
│   ├── schemas.py              # Pydantic 数据模型
│   └── load_data.py            # 数据加载脚本
├── frontend/
│   ├── main.py                 # 前端服务器
│   └── index.html              # Web 界面
├── dataset/
│   └── raw/
│       ├── meta_categories/    # 产品元数据 (JSONL)
│       └── review_categories/  # 产品评价 (JSONL)
├── db/
│   └── ddl/
│       └── yddl.ddl            # 数据库 DDL
├── .env                        # 环境变量配置
├── requirements.txt            # Python 依赖
├── start_services.sh           # 启动脚本
└── README.md                   # 此文件
```

## 核心模块说明

### 推荐引擎 (recommendation_engine.py)

**主要功能:**

1. **understand_query()**: 使用 LLM 理解用户查询
   - 提取用户意图
   - 识别关键词

2. **search_similar_items()**: 向量相似性搜索
   - 使用 pgvector 的 HNSW 索引
   - 计算余弦相似度

3. **generate_recommendations()**: 生成推荐
   - 完整的推荐流程
   - 返回最相关的商品

### Ollama 客户端 (ollama_client.py)

**接口:**

- `generate_text()`: 文本生成
- `embed_text()`: 单个文本 embedding
- `embed_batch()`: 批量 embedding

## 工作流程

```
用户输入
  ↓
[LLM] 理解用户意图 & 提取关键词
  ↓
[Embedding] 生成查询向量
  ↓
[向量搜索] 在 pgvector 中查找相似商品 (TopK)
  ↓
[排序] 根据相似度排序，返回 TopN
  ↓
[LLM] 生成友好的推荐描述
  ↓
用户看到推荐
```

## 常见问题

### Q: Ollama 连接失败

A: 确保 Ollama 正在运行:
```bash
curl http://0.0.0.0:11434/api/tags
```

### Q: 数据加载很慢

A: 这是正常的，Ollama 生成 embedding 需要时间。可以:
1. 先加载少量数据测试
2. 调整 `load_data.py` 中的 `batch_size`

### Q: 向量维度不匹配

A: 检查 `config.py` 中的 `embed_dim` 是否为 768（nomic-embed-text 的输出维度）

### Q: 推荐结果不好

A: 可以尝试:
1. 调整 `RETRIEVE_TOPK` 和 `RETURN_TOPN`
2. 优化 LLM 的 system prompt
3. 加载更多数据

## 性能优化

### 数据库优化

```sql
-- 检查向量索引
SELECT * FROM pg_stat_user_indexes WHERE indexname LIKE '%embedding%';

-- 检查查询性能
EXPLAIN ANALYZE
SELECT * FROM lmrc.item_embeddings
ORDER BY embedding <=> '[...]'::vector
LIMIT 80;
```

### Ollama 优化

- 增加 `OLLAMA_TIMEOUT_S` (默认 60 秒)
- 调整批处理大小

## 开发指南

### 添加新的推荐策略

编辑 `recommendation_engine.py` 的 `RecommendationEngine` 类:

```python
def my_custom_strategy(self, user_query: str) -> List[Dict]:
    # 实现自定义逻辑
    pass
```

### 修改前端

编辑 `frontend/index.html` 的样式或 JavaScript

## 许可证

MIT

## 支持

如有问题，请检查：
1. `.env` 配置正确性
2. PostgreSQL 数据库连接
3. Ollama 服务状态
4. 日志文件 (`logs/` 目录)

---

**最后更新**: 2026-01-15
**系统版本**: 0.1.0
