# 快速参考卡 - 推荐系统使用

## ⚡ 一分钟快速启动

```bash
# 1. 激活环境
conda activate yi

# 2. 启动服务
cd /home/lucas/ucsc/yi
bash start_server.sh

# 3. 打开浏览器
# http://10.0.0.134:8001
```

## 🔍 常用命令

### 激活环境
```bash
conda activate yi
```

### 启动后端服务
```bash
cd /home/lucas/ucsc/yi
bash start_server.sh
```

### 运行诊断
```bash
cd /home/lucas/ucsc/yi
bash run_diagnosis.sh
```

### 测试类别检测
```bash
cd /home/lucas/ucsc/yi
conda activate yi
python test_category_detection.py
```

### 初始化数据库
```bash
cd /home/lucas/ucsc/yi
conda activate yi
python -c "from backend.database import init_db; init_db()"
```

### 检查服务状态
```bash
lsof -i :8001
```

### 停止服务
```bash
# 按 Ctrl+C
```

## 📚 文档导航

| 需求 | 文档 |
|------|------|
| 第一次设置 | [SETUP_GUIDE.md](SETUP_GUIDE.md) |
| 理解类别检测 | [CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) |
| 问题分析 | [ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md) |
| 推荐算法 | [RECOMMENDATION_FIX_REPORT.md](RECOMMENDATION_FIX_REPORT.md) |
| 完整概览 | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |

## 🐛 问题快速排查

### 推荐结果相同
```bash
bash run_diagnosis.sh
# 查看 [5] 测试类别检测 部分的输出
```

### 前端无法连接后端
```bash
# 检查服务是否运行
lsof -i :8001

# 如果没有运行，启动它
bash start_server.sh
```

### 数据库连接错误
```bash
# 检查数据库是否运行
psql -U postgres -c "SELECT version();"

# 初始化数据库
python -c "from backend.database import init_db; init_db()"
```

### ModuleNotFoundError
```bash
# 确保在正确的环境中
conda activate yi
python --version

# 检查缺少的包
pip list | grep [包名]

# 安装缺少的包
pip install [包名]
```

## 🎯 系统功能检查清单

### 基本功能
- [ ] 后端服务正在运行（端口 8001）
- [ ] 前端能访问（http://10.0.0.134:8001）
- [ ] 数据库能连接

### 推荐功能
- [ ] 能输入查询
- [ ] 检测到正确的类别
- [ ] 获得推荐结果
- [ ] 不同查询有不同结果

### 类别检测
- [ ] Electronics（电子产品）- "电脑"
- [ ] Books（书籍）- "书"
- [ ] Home_and_Kitchen（厨房）- "刀片"
- [ ] 其他类别正常工作

## 🚀 API 端点

### 获取推荐

```bash
curl -X POST http://localhost:8001/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我需要一台电脑",
    "session_id": "test123"
  }'
```

### 响应示例

```json
{
  "query": "我需要一台电脑",
  "intent": "用户需要购买一台电脑。",
  "detected_category": "Electronics",
  "recommendations": [
    {
      "asin": "B0...",
      "title": "...",
      "category": "Electronics",
      "price": 999.0,
      "rating_avg": 4.8
    }
  ],
  "session_id": "test123"
}
```

## ✅ 系统状态检查

```bash
# 完整诊断（最推荐）
bash run_diagnosis.sh

# 或者逐项检查：

# 1. Python 环境
conda activate yi && python --version

# 2. 数据库
python -c "from backend.database import init_db, get_db; init_db(); db = next(get_db()); print('✓ DB OK')"

# 3. 推荐引擎
python -c "from backend.recommendation_engine import RecommendationEngine; from backend.database import init_db, get_db; init_db(); db = next(get_db()); rec_engine = RecommendationEngine(db); print('✓ Engine OK')"

# 4. 类别检测
python -c "from backend.recommendation_engine import RecommendationEngine; from backend.database import init_db, get_db; init_db(); db = next(get_db()); rec_engine = RecommendationEngine(db); _, kw = rec_engine.understand_query('电脑'); cat = rec_engine.detect_category('电脑', kw); print(f'✓ Category: {cat}')"

# 5. 完整推荐
python -c "from backend.recommendation_engine import RecommendationEngine; from backend.database import init_db, get_db; init_db(); db = next(get_db()); rec_engine = RecommendationEngine(db); recs = rec_engine.generate_recommendations('我需要电脑'); print(f'✓ Got {len(recs)} recommendations')"
```

## 📝 重要提醒

⚠️ **所有命令执行前必须激活 conda 环境！**

```bash
conda activate yi
```

## 💡 有用的技巧

### 查看后端日志

```bash
# 后端会在控制台输出日志
# 查看关键信息：
# - "Detected category from keywords: XXX"
# - "Multi-path recall returned X items"
# - "Keyword path returned X items"
```

### 查看数据库中的数据

```bash
conda activate yi
python -c "
from backend.database import init_db, get_db
from sqlalchemy import text
init_db()
db = next(get_db())

# 查看 Electronics 类别的产品
result = db.execute(text('''
    SELECT title FROM lmrc.items 
    WHERE category = 'Electronics' 
    LIMIT 5
'''))
for row in result:
    print(row.title)
"
```

### 重置服务

```bash
# 1. 停止现有服务（按 Ctrl+C）

# 2. 重新启动
cd /home/lucas/ucsc/yi
conda activate yi
bash start_server.sh
```

---

**有问题？查看完整的 [SETUP_GUIDE.md](SETUP_GUIDE.md)**
