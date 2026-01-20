# 推荐系统环境配置和运行指南

## 重要：必须使用 conda yi 环境运行

所有的代码执行、测试和服务启动都必须在 `conda yi` 环境中进行。

## 快速开始

### 1. 激活 conda 环境

```bash
conda activate yi
```

### 2. 启动后端服务

#### 方式 A：使用启动脚本（推荐）

```bash
cd /home/lucas/ucsc/yi
bash start_server.sh
```

#### 方式 B：手动启动

```bash
cd /home/lucas/ucsc/yi
conda activate yi
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. 访问前端

打开浏览器访问：`http://10.0.0.134:8001`

## 完整的设置步骤

### 第一次设置

```bash
# 1. 导航到项目目录
cd /home/lucas/ucsc/yi

# 2. 查看环境列表（确保 yi 环境存在）
conda env list

# 3. 激活 yi 环境
conda activate yi

# 4. 检查 Python 版本
python --version

# 5. 验证所有依赖都已安装
pip list | grep -E "fastapi|sqlalchemy|pydantic"

# 6. 初始化数据库
python -c "from backend.database import init_db; init_db()"

# 7. 启动服务
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### 每次使用

```bash
cd /home/lucas/ucsc/yi
conda activate yi
bash start_server.sh
```

## 运行诊断检查

如果遇到问题，运行诊断脚本：

```bash
cd /home/lucas/ucsc/yi
bash run_diagnosis.sh
```

该脚本会检查：
- ✓ Python 环境版本
- ✓ 必要的包是否安装
- ✓ 数据库连接
- ✓ 推荐引擎初始化
- ✓ 类别检测功能
- ✓ 完整的推荐流程

## 常见问题排查

### 问题 1：ModuleNotFoundError

**症状：** 
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案：**
- 确保使用了正确的环境：`conda activate yi`
- 检查环境中是否安装了该包：`pip list | grep xxx`
- 如果缺少包，安装它：`pip install xxx`

### 问题 2：PostgreSQL 连接失败

**症状：**
```
Error: could not translate host name "0.0.0.0" to address
```

**解决方案：**
- 确保 PostgreSQL 服务正在运行
- 检查数据库连接配置：`cat backend/config.py`
- 验证数据库是否存在和可访问

### 问题 3：前端无法连接到后端

**症状：**
```
API error: 502 Bad Gateway
Failed to fetch
```

**解决方案：**
- 确保后端服务在运行：`lsof -i :8001`
- 检查后端服务日志中是否有错误
- 确保使用了正确的 conda 环境
- 尝试重启服务：`bash start_server.sh`

## Conda 环境管理

### 查看已安装的环境

```bash
conda env list
```

### 激活特定环境

```bash
conda activate yi
```

### 查看当前环境中的包

```bash
conda list
# 或者
pip list
```

### 安装新包到 yi 环境

```bash
conda activate yi
pip install package_name
```

### 删除环境（如果需要）

```bash
conda env remove --name yi
```

## 推荐系统核心功能

### 1. 类别自动检测

系统会自动识别用户要购买的产品类别：

```bash
conda activate yi
python -c "
from backend.recommendation_engine import RecommendationEngine
from backend.database import init_db, get_db

init_db()
db = next(get_db())
rec_engine = RecommendationEngine(db)

query = '我需要一台笔记本电脑'
_, keywords = rec_engine.understand_query(query)
category = rec_engine.detect_category(query, keywords)
print(f'查询: {query}')
print(f'检测到类别: {category}')
"
```

### 2. 多路径推荐

系统使用多个推荐路径确保推荐质量：
- ✓ 向量相似度搜索（semantic search）
- ✓ 关键词搜索（keyword search）
- ✓ 分类搜索（category search）
- ✓ 热门商品（popular items）

### 3. 关键词-类别映射

支持的产品类别和关键词：

| 类别 | 示例关键词 |
|-----|---------|
| Electronics | 电脑, 笔记本, 手机, 音箱 |
| Books | 书, 书籍, 编程书 |
| Home_and_Kitchen | 厨房, 刀具, 锅, 冰箱 |
| Clothing_Shoes_and_Jewelry | 衣服, 鞋, 珠宝 |
| Sports_and_Outdoors | 运动, 户外, 登山 |
| Toys_and_Games | 玩具, 游戏, 积木 |
| Beauty_and_Personal_Care | 美妆, 护肤, 口红 |
| Pet_Supplies | 宠物, 狗, 猫, 狗粮 |
| Automotive | 汽车, 车, 轮胎 |
| Software | 软件, 程序, 应用 |

## API 使用示例

### 推荐 API

```bash
conda activate yi
python -c "
import requests
import json

# 调用推荐 API
response = requests.post('http://localhost:8001/api/recommend', json={
    'query': '我需要一台笔记本电脑',
    'session_id': 'test_session_123'
})

data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))
"
```

### 响应格式

```json
{
  "query": "我需要一台笔记本电脑",
  "intent": "用户需要购买一台笔记本电脑。",
  "detected_category": "Electronics",
  "recommendations": [
    {
      "asin": "B09MXPC5XX",
      "title": "MacBook Pro 14-inch M3 Pro",
      "category": "Electronics",
      "brand": "Apple",
      "price": 1999.0,
      "rating_avg": 4.8,
      "rating_count": 12345,
      "similarity": 0.95
    }
  ],
  "session_id": "test_session_123"
}
```

## 测试脚本

### 运行完整测试

```bash
cd /home/lucas/ucsc/yi
conda activate yi
python test_category_detection.py
```

### 运行诊断

```bash
cd /home/lucas/ucsc/yi
bash run_diagnosis.sh
```

## 环境文件位置

- 项目目录：`/home/lucas/ucsc/yi`
- Python 环境：`/home/lucas/anaconda3/envs/yi`
- Conda 配置：`/home/lucas/.condarc`

## 获取帮助

如果遇到问题：

1. 运行诊断脚本：`bash run_diagnosis.sh`
2. 检查后端日志是否有错误
3. 验证是否在正确的 conda 环境中运行
4. 查看文档：`CATEGORY_DETECTION_GUIDE.md`

---

**记住：始终在运行任何命令前激活 conda yi 环境！**

```bash
conda activate yi
```
