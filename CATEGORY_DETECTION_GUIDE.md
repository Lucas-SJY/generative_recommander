# 类别自动检测功能说明

## 功能概述

推荐系统现在集成了**自动商品类别检测**功能。系统会根据用户的自然语言输入，自动识别用户要购买的产品属于哪个类别，然后**只推荐该类别的相关产品**。

## 工作流程

```
用户输入: "我需要一台笔记本电脑用于编程"
    ↓
[1] Query Understanding
    Intent: "用户寻求购买一台适合编程的笔记本电脑"
    Keywords: ["电脑", "编程"]
    ↓
[2] Category Detection
    → Keyword matching: "电脑" → Electronics
    ✓ Detected: Electronics
    ↓
[3] Multi-path Recommendation with Category Filtering
    ✗ Vector Search: 搜索相关products
        → Only include items with category == "Electronics"
    ✗ Keyword Search: 搜索"电脑", "编程"
        → Only include items with category == "Electronics"
    ✗ Category Search: 在Electronics类别内搜索
    ✗ Popular Items: 推荐电子产品类别的热门商品
    ↓
[4] Result
    推荐: XPS 13笔记本, MacBook Pro, Dell Inspiron, ASUS VivoBook...
    ✓ 都是电脑产品，不会推荐音箱、书籍等其他类别
```

## 核心组件

### 1. 类别检测引擎 (`detect_category()`)

**实现方式：两层策略**

#### 第1层：关键词映射 (快速、准确)
```python
def _category_mapping_from_keywords(keywords):
    """
    使用预定义的关键词-类别映射表
    
    例如：
    - "电脑", "笔记本", "laptop" → Electronics
    - "书", "书籍", "编程书" → Books
    - "音箱", "speaker" → Electronics
    - "刀片", "刀" → Home_and_Kitchen
    """
```

**优势：**
- 速度快，不需要调用LLM
- 准确性高
- 支持中英文混合

#### 第2层：LLM分类 (当关键词匹配失败时)
```python
system_prompt = """根据用户查询，识别出产品类别。
返回值必须是以下之一：Electronics, Books, Home_and_Kitchen, ..."""

response = ollama_client.generate_text(user_query, system_prompt)
```

**优势：**
- 处理复杂的描述性查询
- 理解上下文
- 提高覆盖率

### 2. 多路径推荐中的类别过滤

在 `multi_path_recommend()` 方法中，每个搜索路径都添加了类别过滤：

```python
# 向量搜索 + 类别过滤
if target_category:
    vector_results = [item for item in vector_results 
                     if item.get('category') == target_category]

# 关键词搜索 + 类别过滤  
if target_category:
    keyword_results = [item for item in keyword_results 
                      if item.get('category') == target_category]

# 分类搜索 + 类别过滤
if target_category:
    category_results = [item for item in category_results 
                       if item.get('category') == target_category]

# 热门商品 + 类别过滤
if target_category:
    popular_results = [item for item in popular_results 
                      if item.get('category') == target_category]
```

**好处：**
- 确保推荐的都是相关类别的产品
- 避免推荐无关的产品
- 提高用户满意度

## 使用示例

### 示例1：电脑产品

```
用户输入: 我需要一台用于编程的电脑
      ↓
检测到类别: Electronics
      ↓
推荐结果:
  1. MacBook Pro 14-inch M3 Pro
  2. Dell XPS 13 Plus  
  3. ASUS ROG Zephyrus G14
  4. Lenovo ThinkPad X1 Carbon
  (全部是笔记本电脑)
```

### 示例2：书籍产品

```
用户输入: 推荐一本关于Python的书
      ↓
检测到类别: Books
      ↓
推荐结果:
  1. Fluent Python: Clear, Concise, and Effective Programming
  2. Python Crash Course
  3. Automate the Boring Stuff with Python
  4. Learning Python, 5th Edition
  (全部是书籍)
```

### 示例3：厨房用品

```
用户输入: 我需要一个不锈钢刀片
      ↓
检测到类别: Home_and_Kitchen
      ↓
推荐结果:
  1. Stainless Steel Kitchen Knife Set
  2. Professional Chef's Knife 8-inch
  3. Damascus Stainless Steel Knife
  4. Japanese Sashimi Knife Stainless
  (全部是厨房刀具)
```

## 支持的产品类别

系统支持以下产品类别的自动检测：

| 类别代码 | 中文名称 | 示例关键词 |
|---------|---------|----------|
| Electronics | 电子产品 | 电脑, 笔记本, 手机, 音箱, 耳机 |
| Books | 书籍 | 书, 图书, 编程书, 小说 |
| Home_and_Kitchen | 家庭厨房 | 厨房, 刀具, 锅, 冰箱 |
| Clothing_Shoes_and_Jewelry | 服装鞋帽 | 衣服, 鞋, 衣裤, 珠宝 |
| Sports_and_Outdoors | 运动户外 | 运动, 户外, 登山, 骑行 |
| Toys_and_Games | 玩具游戏 | 玩具, 游戏, 积木, 棋牌 |
| Beauty_and_Personal_Care | 美妆个护 | 美妆, 护肤, 口红, 面膜 |
| Pet_Supplies | 宠物用品 | 宠物, 狗, 猫, 狗粮 |
| Automotive | 汽车用品 | 汽车, 车, 轮胎, 机油 |
| Software | 软件 | 软件, 程序, 应用, 系统 |

## API响应格式

API现在返回检测到的类别信息：

```json
{
  "query": "我需要一台笔记本电脑",
  "intent": "用户寻求购买一台笔记本电脑",
  "detected_category": "Electronics",
  "recommendations": [
    {
      "asin": "B09MXPC5XX",
      "title": "MacBook Pro 14-inch",
      "category": "Electronics",
      "brand": "Apple",
      "price": 1999.0,
      "rating_avg": 4.8,
      "rating_count": 12345,
      "similarity": 0.95
    },
    ...
  ],
  "session_id": "abc123"
}
```

## 前端显示

前端会在推荐结果之前显示检测到的类别：

```
💬 用户: 我需要一台笔记本电脑

🤖 助手: 理解到你的需求: 用户寻求购买一台笔记本电脑

📁 检测到商品类别: Electronics

推荐商品:
  [1] MacBook Pro 14-inch...
  [2] Dell XPS 13...
  ...
```

## 性能优化

### 缓存策略
- **类别检测结果**会与用户会话绑定
- 相同查询不会重复检测

### 降级策略
- 如果类别检测失败 → 使用所有类别的推荐
- 如果特定类别没有匹配结果 → 自动扩展到相关类别

### 日志信息
```
[INFO] Detected category from keywords: Electronics
[INFO] Multi-path recommendation for category: Electronics
[INFO] Vector path returned 25 items
[INFO] Keyword path returned 30 items
[INFO] Category search for Electronics: 40 items
```

## 测试方法

运行测试脚本验证功能：
```bash
cd /home/lucas/ucsc/yi
python test_category_detection.py
```

该脚本会测试多个查询并显示：
1. ✓ 类别检测是否正确
2. ✓ 推荐结果是否匹配检测的类别
3. ✓ 推荐列表的质量

## 后续改进建议

1. **动态类别映射** - 根据数据库实际有的类别自动生成关键词映射

2. **多类别支持** - 允许一个查询匹配多个类别（如"无线音箱"可能属于Electronics也可能属于Home_and_Kitchen）

3. **用户反馈学习** - 根据用户点击和转化率优化类别检测

4. **A/B测试** - 对比有/无类别过滤的推荐效果

5. **跨类别推荐** - 在同一类别推荐多样性有限时，自动扩展到相关类别

## 关键改动文件

- **backend/recommendation_engine.py**
  - 新增: `detect_category()` 方法
  - 新增: `_category_mapping_from_keywords()` 方法
  - 新增: `_validate_category()` 方法
  - 修改: `multi_path_recommend()` 添加类别过滤
  - 修改: `generate_recommendations()` 集成类别检测

- **backend/main.py**
  - 修改: `/api/recommend` 端点返回检测的类别

- **backend/schemas.py**
  - 修改: `RecommendationResponse` 添加 `detected_category` 字段

- **frontend/index.html**
  - 修改: 显示检测到的类别信息

- **test_category_detection.py** (新增)
  - 测试脚本，验证类别检测功能
