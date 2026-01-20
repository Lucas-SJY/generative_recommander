# 📖 文档索引

快速查找所需文档的完整索引。

## 🎯 按需求查找

### 我是新用户

1. 先读：[QUICK_START.md](QUICK_START.md) ⚡ 5分钟快速上手
2. 再读：[README.md](README.md) 📖 了解系统功能
3. 遇到问题：[SETUP_GUIDE.md](SETUP_GUIDE.md) 🔧 环境配置帮助

### 我要启动服务

**快速方法**：
```bash
conda activate yi
cd /home/lucas/ucsc/yi
bash start_server.sh
```

**详细步骤**：查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的"启动服务"部分

### 我要了解类别检测功能

阅读：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md)

包含内容：
- 工作流程
- 支持的类别
- 使用示例
- 性能优化

### 我要了解问题修复

阅读：[ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md)

包含内容：
- 问题根本原因
- 修复方案
- 技术细节
- 预期效果

### 我遇到了问题

**按顺序尝试**：

1. 运行诊断：
   ```bash
   bash run_diagnosis.sh
   ```

2. 查看 [QUICK_START.md](QUICK_START.md) 的快速排查部分

3. 查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的故障排除部分

4. 查看 [ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md) 获得技术帮助

### 我想要完整的项目概览

阅读：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

包含内容：
- 工作完成清单
- 系统架构
- 技术改进
- 性能指标

### 我想查看项目状态

阅读：[PROJECT_STATUS.md](PROJECT_STATUS.md)

包含内容：
- 完成情况
- 功能验证
- 使用准备
- 后续改进

## 📚 文档完整列表

### 用户文档

| 文档 | 适合人群 | 阅读时间 |
|------|---------|---------|
| [QUICK_START.md](QUICK_START.md) | 所有用户 | 5 分钟 |
| [README.md](README.md) | 新用户 | 10 分钟 |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | 系统管理员 | 15 分钟 |

### 功能文档

| 文档 | 功能 | 阅读时间 |
|------|------|---------|
| [CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) | 类别检测 | 10 分钟 |
| [RECOMMENDATION_FIX_REPORT.md](RECOMMENDATION_FIX_REPORT.md) | 推荐改进 | 8 分钟 |

### 技术文档

| 文档 | 内容 | 阅读时间 |
|------|------|---------|
| [ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md) | 问题分析和修复 | 10 分钟 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 技术总结 | 15 分钟 |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | 项目完成状态 | 5 分钟 |

## 🛠️ 脚本和工具

| 脚本 | 用途 | 运行方式 |
|------|------|---------|
| [start_server.sh](start_server.sh) | 启动后端服务 | `bash start_server.sh` |
| [run_diagnosis.sh](run_diagnosis.sh) | 系统诊断检查 | `bash run_diagnosis.sh` |
| [test_category_detection.py](test_category_detection.py) | 功能测试 | `python test_category_detection.py` |

## 🎯 常见任务速查表

### 任务：启动系统

```bash
conda activate yi
cd /home/lucas/ucsc/yi
bash start_server.sh
```

**查看详情**：[SETUP_GUIDE.md](SETUP_GUIDE.md) → "启动后端服务"

### 任务：检查系统状态

```bash
cd /home/lucas/ucsc/yi
bash run_diagnosis.sh
```

**查看详情**：[QUICK_START.md](QUICK_START.md) → "系统状态检查"

### 任务：测试类别检测

```bash
cd /home/lucas/ucsc/yi
conda activate yi
python test_category_detection.py
```

**查看详情**：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md)

### 任务：查看 API 文档

**查看详情**：[SETUP_GUIDE.md](SETUP_GUIDE.md) → "API 使用示例"

### 任务：理解类别映射

**查看详情**：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "支持的产品类别"

### 任务：解决类别检测不准确

**查看详情**：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "后续改进建议"

### 任务：理解推荐算法

**查看详情**：[RECOMMENDATION_FIX_REPORT.md](RECOMMENDATION_FIX_REPORT.md)

### 任务：了解系统架构

**查看详情**：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → "系统架构"

## 🔑 关键概念查找

### 概念：Category Detection（类别检测）

- 工作原理：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "工作流程"
- 实现方式：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "核心组件"
- 支持的类别：[CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "支持的产品类别"

### 概念：Multi-path Recommendation（多路径推荐）

- 工作流程：[RECOMMENDATION_FIX_REPORT.md](RECOMMENDATION_FIX_REPORT.md)
- 详细说明：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → "系统架构"

### 概念：Keyword Search（关键词搜索）

- 问题分析：[ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md)
- 修复方案：[ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md) → "修复方案"

### 概念：Vector Search（向量搜索）

- 原理：[README.md](README.md) → "系统架构"
- 实现：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → "多路径推荐"

## ❓ FAQ 快速查找

### 问题：为什么推荐结果相同？

**答案**：这是一个已修复的问题。查看 [ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md)

### 问题：支持哪些产品类别？

**答案**：10+ 主要类别。查看 [CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "支持的产品类别"

### 问题：如何添加新的关键词？

**答案**：查看 [CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) → "关键字映射表"

### 问题：类别检测准确率如何？

**答案**：> 95%。查看 [PROJECT_STATUS.md](PROJECT_STATUS.md) → "功能验证报告"

### 问题：系统支持多语言吗？

**答案**：支持中英文混合。查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) → "推荐系统核心功能"

## 📋 文档更新历史

| 日期 | 文档 | 更新 |
|------|------|------|
| 2026-01-18 | 所有 | 初始版本完成 |

## 💡 使用建议

### 初次使用建议

1. ⭐⭐⭐ 必读：[QUICK_START.md](QUICK_START.md)
2. ⭐⭐ 推荐：[README.md](README.md)
3. ⭐ 选读：其他文档

### 深入学习建议

按照以下顺序阅读能更好地理解系统：

1. [README.md](README.md) - 了解总体架构
2. [CATEGORY_DETECTION_GUIDE.md](CATEGORY_DETECTION_GUIDE.md) - 了解核心功能
3. [ROOT_CAUSE_FIX.md](ROOT_CAUSE_FIX.md) - 了解技术细节
4. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 深入技术实现

### 问题排查建议

1. 第一步：运行 `bash run_diagnosis.sh`
2. 第二步：查看诊断输出
3. 第三步：根据问题查看相应文档
4. 第四步：参考故障排除部分

## 🔗 文档关系图

```
README.md (项目概览)
    ├─ QUICK_START.md (快速入门)
    ├─ SETUP_GUIDE.md (环境配置)
    │   ├─ 包含故障排除
    │   └─ 包含 API 示例
    ├─ CATEGORY_DETECTION_GUIDE.md (功能详解)
    │   └─ 说明如何使用类别检测
    └─ PROJECT_SUMMARY.md (技术总结)
       ├─ ROOT_CAUSE_FIX.md (问题分析)
       └─ RECOMMENDATION_FIX_REPORT.md (算法改进)

PROJECT_STATUS.md (项目状态报告)
    └─ 总结所有完成情况
```

---

**建议**：先阅读 [QUICK_START.md](QUICK_START.md)，然后根据需要查找其他文档！

**问题**：运行 `bash run_diagnosis.sh` 获取系统诊断信息。
