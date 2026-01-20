# 🚀 Amazon 推荐系统 - 完整使用指南

## 目录
1. [系统要求](#系统要求)
2. [完整部署步骤](#完整部署步骤)
3. [验证安装](#验证安装)
4. [使用示例](#使用示例)
5. [常见问题](#常见问题)

---

## 系统要求

### 硬件要求
- **CPU**: 4+ 核心 (推荐 8+)
- **RAM**: 8GB 最低 (推荐 16GB+)
- **存储**: 50GB+ (取决于数据量)
- **GPU** (可选): NVIDIA GPU 可加速 Ollama

### 软件要求
- Python 3.9+
- PostgreSQL 14+ (需要 pgvector)
- Ollama (本地 LLM 推理)

---

## 完整部署步骤

### ✅ 步骤 1: 安装基础软件 (15 分钟)

#### 1.1 安装 PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# macOS
brew install postgresql
brew services start postgresql

# Windows
# 从 https://www.postgresql.org/download/windows 下载安装
```

#### 1.2 创建数据库和用户
```bash
sudo -u postgres psql

-- 在 psql 中执行
CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
CREATE DATABASE recsys;
\c recsys

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

\q
```

#### 1.3 安装 Ollama
```bash
# 从 https://ollama.ai 下载并安装 Ollama

# 然后在终端中运行
ollama serve
```

#### 1.4 拉取模型 (在另一个终端)
```bash
# 拉取 Qwen 模型 (约 9GB，需要 20-30 分钟)
ollama pull qwen2.5:14b

# 拉取 Embedding 模型 (约 274MB，需要 1-2 分钟)
ollama pull nomic-embed-text

# 验证模型
ollama list
```

### ✅ 步骤 2: 初始化项目 (5 分钟)

```bash
# 进入项目目录
cd /home/lucas/ucsc/yi

# 创建 Python 虚拟环境 (可选但推荐)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装 Python 依赖
pip install -r requirements.txt
```

### ✅ 步骤 3: 初始化数据库 (5 分钟)

```bash
# 应用 DDL 脚本
psql -U postgres -d recsys -f db/ddl/yddl.ddl

# 或者使用 Python (自动处理扩展)
python backend/load_data.py
```

### ✅ 步骤 4: 加载数据 (1-8 小时)

```bash
# 这个步骤会:
# 1. 从 dataset/raw/meta_categories 读取商品数据
# 2. 使用 Ollama 生成向量表示
# 3. 存储到 PostgreSQL + pgvector

python backend/load_data.py

# 进度会实时显示
# 可以按 Ctrl+C 中断，下次运行会继续
```

### ✅ 步骤 5: 验证安装 (2 分钟)

```bash
# 运行系统检查
python health_check.py

# 查看数据库统计
python db_utils.py

# 预期输出:
# ✓ PostgreSQL - OK
# ✓ Ollama - OK
# ✓ Python Packages - OK
```

### ✅ 步骤 6: 启动系统 (1 分钟)

#### 方式 A: 自动启动 (推荐)
```bash
python run.py

# 输出:
# 🚀 启动后端 API 服务 (8000)...
# ✅ 后端已启动
# 🌐 启动前端服务 (8001)...
# ✅ 前端已启动
# 按 Ctrl+C 停止服务
```

#### 方式 B: 手动启动

**终端 A:**
```bash
python -m backend.main
# 后端运行在 http://0.0.0.0:8000
```

**终端 B:**
```bash
python -m frontend.main
# 前端运行在 http://0.0.0.0:8001
```

### ✅ 步骤 7: 打开浏览器

访问: **http://0.0.0.0:8001**

---

## 验证安装

### 1. 检查后端

```bash
# 打开浏览器或使用 curl
curl http://0.0.0.0:8000/health

# 预期响应:
# {"status": "healthy", "timestamp": "..."}
```

### 2. 检查 API 文档

```
http://0.0.0.0:8000/docs
```

应该看到 Swagger 文档界面。

### 3. 测试推荐功能

```bash
curl -X POST "http://0.0.0.0:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我想要一个轻便的无线充电宝",
    "user_id": "test_user"
  }'

# 应该返回推荐列表
```

### 4. 测试前端界面

```
打开 http://0.0.0.0:8001
在输入框中输入: "我想要一个好的鼠标"
点击"发送"按钮
应该看到推荐结果
```

---

## 使用示例

### 示例 1: 简单查询

**输入:**
```
我想要一个轻便的无线充电宝
```

**系统处理:**
1. LLM 理解意图: "寻找轻便易携带的无线充电宝"
2. Embedding: 转换为 768 维向量
3. 搜索: 在 pgvector 中找到最相似的商品
4. 返回: 8 个最相关的推荐

**预期结果:**
```
推荐 1: Anker 20000mAh 无线充电宝
        品牌: Anker | 分类: 电源配件
        ¥129.99 | ★ 4.5 (5000)
        匹配度: 94%

推荐 2: Baseus 30W 无线充电宝
        品牌: Baseus | 分类: 电源配件
        ¥179.99 | ★ 4.3 (3000)
        匹配度: 92%

... (共 8 个推荐)
```

### 示例 2: 多轮对话

**对话 1:**
```
用户: 我需要一个高性能游戏本

助手: 我为您推荐了几款高性能游戏本...
(显示 8 个推荐)
```

**对话 2:**
```
用户: 价格要在 8000 以内

助手: 我更新了推荐，这些都是价格实惠的高性能本...
(显示更新后的推荐)
```

**对话 3:**
```
用户: 屏幕最好是 RTX 4070 的

助手: 这些都配备了 RTX 4070 显卡...
(显示筛选后的推荐)
```

---

## 常见问题

### Q1: PostgreSQL 连接失败

**错误信息:**
```
Error: could not translate host name "0.0.0.0" to address
```

**解决方案:**
```bash
# 1. 检查 PostgreSQL 是否运行
sudo systemctl status postgresql

# 2. 检查 .env 中的连接字符串
# DATABASE_URL 应该是:
# postgresql+psycopg://postgres:postgres@127.0.0.1:5432/recsys

# 3. 手动测试连接
psql -U postgres -d recsys -c "SELECT 1"

# 4. 如果还是失败，重启 PostgreSQL
sudo systemctl restart postgresql
```

### Q2: Ollama 模型加载失败

**错误信息:**
```
Error: model not found
```

**解决方案:**
```bash
# 1. 检查 Ollama 是否运行
curl http://0.0.0.0:11434/api/tags

# 2. 如果失败，启动 Ollama
ollama serve

# 3. 在另一个终端拉取模型
ollama pull qwen2.5:14b
ollama pull nomic-embed-text

# 4. 验证模型已加载
ollama list
```

### Q3: 推荐结果为空

**原因:** 数据库中没有数据

**解决方案:**
```bash
# 1. 检查数据库中的数据量
python db_utils.py

# 2. 如果 items 为 0，加载数据
python backend/load_data.py

# 3. 等待数据加载完成 (可能需要 1-8 小时)
# 可以在加载过程中使用系统，但推荐结果会不断改进
```

### Q4: 系统响应很慢

**原因:** 可能是 Ollama 模型生成速度慢

**解决方案:**
```bash
# 1. 检查 Ollama 日志
ollama serve  # 查看输出信息

# 2. 如果有 GPU，确保 Ollama 使用了 GPU
# 检查是否有 CUDA 相关输出

# 3. 优化参数:
# - 减少 RETRIEVE_TOPK (在 .env 中)
# - 减少 RETURN_TOPN (在 .env 中)
# - 减少 LLM 的 temperature (在 ollama_client.py 中)
```

### Q5: 前端无法连接到后端

**错误信息:**
```
Failed to fetch
CORS error
```

**解决方案:**
```bash
# 1. 检查后端是否运行
curl http://0.0.0.0:8000/health

# 2. 检查防火墙
# 确保 8000 和 8001 端口未被阻止

# 3. 检查浏览器控制台
# 打开开发者工具 (F12) → Console
# 查看具体的错误信息

# 4. 确保后端 CORS 配置正确
# 在 backend/main.py 中已经配置了 CORS
```

### Q6: "Items without embeddings" 报告很多

**原因:** 某些商品还没有生成向量

**解决方案:**
```bash
# 1. 继续运行数据加载脚本
python backend/load_data.py

# 2. 该脚本会:
# - 检查没有向量的商品
# - 为它们生成向量
# - 保存到数据库

# 3. 可以多次运行，不会重复处理已有向量的商品
```

### Q7: 磁盘空间不足

**解决方案:**
```bash
# 1. 检查磁盘使用情况
df -h

# 2. 清理 Ollama 缓存 (可选)
ollama prune

# 3. 如果需要，可以只加载部分数据
# 编辑 backend/load_data.py，限制加载的文件数量
```

### Q8: "port already in use"

**错误信息:**
```
OSError: [Errno 48] Address already in use: ('0.0.0.0', 8000)
```

**解决方案:**
```bash
# 方式 1: 杀死占用端口的进程
# Linux/macOS:
lsof -i :8000
kill -9 <PID>

# 方式 2: 使用不同的端口
# 编辑 backend/main.py 和 frontend/main.py
# 改变 port 参数

# 方式 3: 等待一会儿，端口会自动释放
sleep 10
python run.py
```

---

## 性能调优

### 1. 增加推荐准确性

编辑 `.env`:
```env
RETRIEVE_TOPK=100    # 搜索前 100 个 (从 80 增加)
RETURN_TOPN=10       # 返回前 10 个 (从 8 增加)
```

### 2. 加快响应速度

编辑 `.env`:
```env
RETRIEVE_TOPK=50     # 搜索前 50 个 (从 80 减少)
RETURN_TOPN=5        # 返回前 5 个 (从 8 减少)
```

### 3. 优化 LLM 生成

编辑 `backend/ollama_client.py`:
```python
def generate_text(self, prompt: str, ...):
    # 减少 temperature 获得更确定的回答
    "temperature": 0.5,  # 从 0.7 改为 0.5
```

---

## 生产部署检查清单

在部署到生产环境前，确保完成以下步骤:

- [ ] 所有依赖已安装
- [ ] 数据库已初始化
- [ ] 数据已完全加载
- [ ] 系统健康检查通过
- [ ] API 文档可访问
- [ ] 前端界面可加载
- [ ] 推荐功能正常
- [ ] 日志系统就绪
- [ ] 备份方案制定
- [ ] 监控系统部署

---

## 获取帮助

### 查看项目总结
```bash
python PROJECT_SUMMARY.py
```

### 打印完成清单
```bash
python CHECKLIST.py
```

### 查看详细文档
- `README.md` - 完整系统说明
- `QUICKSTART.md` - 快速开始指南
- `ARCHITECTURE.md` - 架构与实现细节

### 联系支持

如有问题:
1. 查看相应的文档
2. 运行 `health_check.py` 检查系统
3. 查看日志文件 (`logs/` 目录)
4. 尝试 `dev_test.py` 进行诊断

---

## 总结

恭喜！您现在拥有一个完整的 Amazon 推荐系统，支持:

✅ 自然语言查询
✅ 智能推荐
✅ 多轮对话
✅ 完整的前后端
✅ 可扩展的架构

祝使用愉快！🎉
