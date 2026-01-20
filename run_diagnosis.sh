#!/bin/bash
# 诊断脚本 - 在正确的 conda 环境中运行

source /home/lucas/anaconda3/etc/profile.d/conda.sh
conda activate yi

cd /home/lucas/ucsc/yi

echo "======================================================================"
echo "推荐系统诊断检查"
echo "======================================================================"

echo ""
echo "[1] 检查Python环境..."
python --version
which python

echo ""
echo "[2] 检查必要的包..."
python -c "
import sqlalchemy
import fastapi
import ollama
import pydantic
print('✓ 所有必要的包都已安装')
"

echo ""
echo "[3] 检查数据库连接..."
python -c "
from backend.database import init_db, get_db
init_db()
db = next(get_db())
print('✓ 数据库连接成功')
"

echo ""
echo "[4] 检查推荐引擎初始化..."
python -c "
from backend.recommendation_engine import RecommendationEngine
from backend.database import init_db, get_db
init_db()
db = next(get_db())
rec_engine = RecommendationEngine(db)
print('✓ 推荐引擎初始化成功')
"

echo ""
echo "[5] 测试类别检测..."
python -c "
from backend.recommendation_engine import RecommendationEngine
from backend.database import init_db, get_db
init_db()
db = next(get_db())
rec_engine = RecommendationEngine(db)

test_cases = [
    ('我需要一台电脑', 'Electronics'),
    ('推荐一本书', 'Books'),
    ('我需要一个音箱', 'Electronics'),
]

for query, expected in test_cases:
    _, keywords = rec_engine.understand_query(query)
    category = rec_engine.detect_category(query, keywords)
    status = '✓' if category == expected else '⚠'
    print(f'{status} {query} → {category}')
"

echo ""
echo "[6] 测试完整推荐流程..."
python -c "
from backend.recommendation_engine import RecommendationEngine
from backend.database import init_db, get_db
init_db()
db = next(get_db())
rec_engine = RecommendationEngine(db)

query = '我需要一台笔记本电脑'
print(f'查询: {query}')
recs = rec_engine.generate_recommendations(query)
print(f'✓ 成功生成 {len(recs)} 条推荐')
if recs:
    print(f'  第一条: {recs[0][\"title\"][:50]}...')
"

echo ""
echo "======================================================================"
echo "诊断检查完成"
echo "======================================================================"
