"""Quick start guide for the recommendation system"""

# 🚀 快速入门指南

## 1️⃣ 环境准备 (5 分钟)

### 启动必要的服务

**终端 1 - 启动 PostgreSQL**
```bash
# 确保 PostgreSQL 正在运行，数据库和 schema 已创建
psql -U postgres -c "CREATE DATABASE recsys;" 2>/dev/null || true
psql -U postgres -d recsys -f db/ddl/yddl.ddl
```

**终端 2 - 启动 Ollama**
```bash
ollama serve
```

**终端 3 - 在另一个窗口加载模型**
```bash
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

### 安装 Python 依赖
```bash
pip install -r requirements.txt
```

## 2️⃣ 系统健康检查 (2 分钟)

```bash
python health_check.py
```

预期输出：
```
✓ PostgreSQL - OK
✓ Ollama - OK
✓ Python Packages - OK
```

## 3️⃣ 加载数据 (取决于数据量)

### 查看统计信息
```bash
python db_utils.py
```

### 加载 Amazon 数据
```bash
python backend/load_data.py
```

这个过程可能需要 **数小时**，取决于你的数据量。进度会实时显示。

## 4️⃣ 启动系统

### 选项 A: 使用自动化脚本
```bash
chmod +x start_services.sh
./start_services.sh
```

### 选项 B: 手动启动

**终端 A - 后端**
```bash
python -m backend.main
```

**终端 B - 前端**
```bash
python -m frontend.main
```

## 5️⃣ 打开浏览器

访问: **http://0.0.0.0:8001**

## 🧪 测试推荐功能

在网页界面中试试这些查询：

1. **"我想要一个轻便的无线充电宝"**
2. **"高性能游戏笔记本，价格在 8000 以内"**
3. **"什么运动鞋比较舒服，用于日常穿着"**
4. **"我需要一个学生用的平板电脑"**

---

## 🔧 故障排除

### 问题 1: "连接到 PostgreSQL 失败"

检查数据库配置：
```bash
psql -U postgres -d recsys -c "SELECT 1"
```

如果失败，创建数据库：
```bash
createdb -U postgres recsys
psql -U postgres -d recsys -f db/ddl/yddl.ddl
```

### 问题 2: "连接到 Ollama 失败"

检查 Ollama 是否运行：
```bash
curl http://0.0.0.0:11434/api/tags
```

如果失败，启动 Ollama：
```bash
ollama serve
```

### 问题 3: "模型不存在"

拉取模型：
```bash
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

### 问题 4: "推荐结果为空"

确保数据已加载：
```bash
python db_utils.py
# 检查 "items" 和 "embeddings" 数量
```

如果为 0，运行数据加载脚本：
```bash
python backend/load_data.py
```

---

## 📊 API 快速测试

### 使用 curl 测试推荐接口

```bash
curl -X POST "http://0.0.0.0:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我想要一个好用的鼠标",
    "user_id": "test_user"
  }'
```

### 在浏览器中查看 API 文档

访问: **http://0.0.0.0:8000/docs**

---

## 📁 关键文件位置

- 后端主程序: `backend/main.py`
- 推荐引擎: `backend/recommendation_engine.py`
- 前端界面: `frontend/index.html`
- 配置文件: `.env`
- 数据加载: `backend/load_data.py`
- 数据库工具: `db_utils.py`

---

## ⏱️ 预期时间

| 步骤 | 时间 |
|------|------|
| 环境准备 | 5 分钟 |
| 健康检查 | 2 分钟 |
| 数据加载 | 1-8 小时 (取决于数据量) |
| 启动服务 | 1 分钟 |
| **总计** | **1-8 小时** |

---

## 💡 提示

1. **第一次运行**会比较慢，因为需要加载大量数据和生成 embedding
2. **Ollama 生成 embedding** 是最耗时的步骤
3. **向量索引**会自动创建，无需手动干预
4. 你可以在数据加载完成后立即开始使用系统

---

## 📞 需要帮助？

1. 检查日志文件: `logs/backend.log` 和 `logs/frontend.log`
2. 查看完整文档: `README.md`
3. 运行健康检查: `python health_check.py`

---

**准备好开始了吗？** 👉 [按照上面的步骤开始！](#1️⃣-环境准备-5-分钟)
