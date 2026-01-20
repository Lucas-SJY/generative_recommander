# 推荐系统问题修复报告

## 问题描述

推荐系统存在的主要问题：**不管用户问什么，系统推荐的产品都基本相同**。

例如：用户询问"我需要一台电子工程专业用的电脑"，系统却推荐了音箱（Echo Dot）、电视棒和其他电子产品，而不是电脑。

## 根本原因分析

### 1. **JSON解析失败导致关键词提取失败**
   - **位置**：`understand_query()` 方法
   - **问题**：Ollama LLM 返回的响应可能包含额外的文本或格式不标准的JSON
   - **后果**：当JSON解析失败时，代码直接抛出异常，导致 `intent` 和 `keywords` 都为空
   - **结果**：所有查询最终都退化到"热门商品"推荐路径，导致推荐结果相同

```python
# 原代码问题：直接parse，失败则返回空keywords
data = json.loads(response)  # 如果格式不对，直接报错
keywords = data.get("keywords", [])  # 失败后返回[]
```

### 2. **Embedding生成缺乏容错机制**
   - **位置**：`generate_recommendations()` 方法
   - **问题**：如果embedding生成失败，后续的向量搜索无法执行
   - **后果**：无法使用向量相似度搜索来区分不同的查询
   - **结果**：所有查询都依赖关键词搜索和热门商品排序

### 3. **多路召回策略不完整**
   - **位置**：`multi_path_recommend()` 方法
   - **问题**：当向量搜索失败时，没有捕捉异常，直接导致整个推荐流程失败
   - **后果**：关键词搜索和分类搜索无法作为备选方案执行

## 修复方案

### 1. 改进 `understand_query()` 方法

**修改内容：**
- ✅ 添加JSON解析的多层容错机制
  - 首先尝试直接解析
  - 如果失败，使用正则表达式提取JSON块
  - 如果仍失败，调用备选关键词提取方法
  
- ✅ 降低LLM温度参数（temperature=0.3）以获得更一致的输出
  
- ✅ 添加新方法 `_extract_keywords_fallback()` 用于直接从查询中提取关键词
  - 按中文标点符号和空格分割
  - 过滤掉过短的词汇（<2字符）

```python
# 新增容错逻辑
try:
    data = json.loads(response)
except json.JSONDecodeError:
    # 备选方案：正则提取
    json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group())
```

### 2. 改进 `generate_recommendations()` 方法

**修改内容：**
- ✅ 添加embedding生成的完整容错链
  - 先尝试使用理解后的 intent 生成embedding
  - 失败后，尝试使用原始查询
  - 仍失败，则返回空embedding但继续执行（不中断）

- ✅ 添加检查，确保非空embedding才进行向量搜索

- ✅ 当所有路径都返回0结果时，调用热门商品作为最后备选

```python
# 新增容错链
try:
    query_embedding = ollama_client.embed_text(text_to_embed)
except Exception as e:
    logger.warning(f"First embedding failed, trying original query...")
    try:
        query_embedding = ollama_client.embed_text(user_query)
    except:
        logger.warning("All embedding attempts failed")
        query_embedding = []
```

### 3. 改进 `multi_path_recommend()` 方法

**修改内容：**
- ✅ 检查embedding是否有效再执行向量搜索
- ✅ 向量搜索异常不中断整个流程，继续执行其他路径
- ✅ 改进日志记录，清晰显示每个路径的执行情况

```python
# 新增检查
if query_embedding:  # 仅在embedding非空时执行
    try:
        vector_results = self.search_similar_items(...)
    except Exception as e:
        logger.warning(f"Vector search failed: {e}")
        vector_results = []
```

## 修复效果预期

### 修复前的问题
```
查询：我需要一台电脑
推荐：Echo Dot、Fire TV Stick、Disney+... (都是其他电子产品)
```

### 修复后的预期效果
```
查询1：我需要一台电脑
→ Intent: "用户寻求购买一台电脑"
→ Keywords: ["电脑", "笔记本", ...]
→ Embedding: ✓ 成功生成
→ 向量搜索: ✓ 返回相关电脑产品
→ 推荐: 笔记本电脑、台式电脑等

查询2：推荐一个音箱
→ Intent: "用户寻求购买音箱"
→ Keywords: ["音箱", ...]
→ Embedding: ✓ 成功生成
→ 向量搜索: ✓ 返回相关音箱产品
→ 推荐: 智能音箱、无线音箱等
```

## 验证步骤

运行测试脚本验证修复：
```bash
cd /home/lucas/ucsc/yi
python test_recommendation_fix.py
```

该脚本会测试多个不同的查询，验证：
1. ✓ Query understanding (意图识别和关键词提取)
2. ✓ Embedding generation (向量生成)
3. ✓ Recommendation generation (推荐生成)

## 文件修改清单

- `/home/lucas/ucsc/yi/backend/recommendation_engine.py`
  - `understand_query()` - 改进JSON解析和容错
  - `_extract_keywords_fallback()` - 新增备选关键词提取
  - `generate_recommendations()` - 改进embedding容错链
  - `multi_path_recommend()` - 改进向量搜索错误处理

## 后续改进建议

1. **缓存Embedding结果**：避免重复计算相同查询的embedding
2. **添加查询去重**：检测相似的查询，复用embedding结果
3. **优化向量搜索参数**：根据实际数据调整 `topk` 和 `topn`
4. **监控推荐质量**：追踪用户点击率，反馈给推荐算法
5. **A/B测试**：对比不同的意图理解策略效果
