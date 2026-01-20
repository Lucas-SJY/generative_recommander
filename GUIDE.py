"""
📖 Amazon 推荐系统 - 文档导航指南

开始使用系统? 按下列顺序阅读文档:
"""

DOCUMENTATION_GUIDE = {
    "🚀 立即开始 (5 分钟)": {
        "QUICKSTART.md": "快速开始指南 - 5 步启动系统",
        "DELIVERY_NOTES.txt": "项目交付说明 - 快速概览",
    },
    
    "📚 完整学习 (1-2 小时)": {
        "README.md": "系统完整说明 - API 文档、功能介绍",
        "INSTALLATION_GUIDE.md": "部署安装指南 - 详细部署步骤",
        "ARCHITECTURE.md": "架构与实现 - 系统设计、技术细节",
    },
    
    "🔍 深入理解 (2-4 小时)": {
        "PROJECT_SUMMARY.py": "项目总结 - 功能、性能、工作流",
        "FINAL_SUMMARY.py": "最终总结 - 项目统计、完成情况",
        "PROJECT_COMPLETION_REPORT.md": "完成报告 - 交付统计、质量保证",
    },
    
    "✅ 验证与测试": {
        "CHECKLIST.py": "完成清单 - 所有组件检查",
        "运行命令": {
            "python health_check.py": "系统健康检查",
            "python db_utils.py": "数据库统计",
            "python dev_test.py": "功能测试",
        }
    },
}

# 快速参考
QUICK_REFERENCE = {
    "🌐 访问地址": {
        "前端": "http://0.0.0.0:8001",
        "后端 API": "http://0.0.0.0:8000",
        "API 文档": "http://0.0.0.0:8000/docs",
    },
    
    "⚙️ 启动命令": {
        "一键启动": "python run.py",
        "后端": "python -m backend.main",
        "前端": "python -m frontend.main",
    },
    
    "🧪 测试命令": {
        "系统检查": "python health_check.py",
        "数据库统计": "python db_utils.py",
        "推荐测试": "python dev_test.py '我想要一个好的鼠标'",
    },
}

GETTING_STARTED = """
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   🎯 快速开始 3 步骤                                       │
│                                                             │
│   1️⃣ 安装依赖                                             │
│      $ pip install -r requirements.txt                    │
│                                                             │
│   2️⃣ 启动系统                                             │
│      $ python run.py                                      │
│                                                             │
│   3️⃣ 打开浏览器                                           │
│      http://0.0.0.0:8001                               │
│                                                             │
│   ✅ 完成! 开始输入查询吧                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""

FILES_OVERVIEW = """
📁 项目文件结构

核心代码 (28 行代码)
├── backend/           (9 个 Python 模块)
│   ├── main.py       - FastAPI 应用
│   ├── models.py     - 数据库模型
│   ├── ollama_client.py - LLM 集成
│   ├── recommendation_engine.py - 推荐引擎
│   └── ... (5 个更多文件)
│
├── frontend/         (2 个文件)
│   ├── main.py       - 前端服务器
│   └── index.html    - Web 界面
│
└── 工具脚本 (7 个)
    ├── run.py        - 一键启动
    ├── health_check.py - 系统检查
    ├── dev_test.py   - 功能测试
    └── ... (4 个更多)

文档和配置 (8 个文件)
├── README.md                    - 完整说明
├── QUICKSTART.md                - 快速开始
├── ARCHITECTURE.md              - 架构详解
├── INSTALLATION_GUIDE.md        - 部署指南
├── PROJECT_COMPLETION_REPORT.md - 完成报告
├── .env                         - 配置
├── requirements.txt             - 依赖
└── db/ddl/yddl.ddl             - 数据库 DDL
"""

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📖 Amazon 推荐系统 - 文档导航")
    print("="*70 + "\n")
    
    # 显示快速开始
    print(GETTING_STARTED)
    
    # 显示快速参考
    print("\n⚡ 快速参考\n" + "-"*70)
    for category, items in QUICK_REFERENCE.items():
        print(f"\n{category}")
        if isinstance(items, dict):
            for key, value in items.items():
                if isinstance(value, dict):
                    for cmd, desc in value.items():
                        print(f"  {cmd:30s} - {desc}")
                else:
                    print(f"  {key:30s} {value}")
    
    # 显示文档导航
    print("\n\n📚 文档导航\n" + "-"*70)
    for category, docs in DOCUMENTATION_GUIDE.items():
        print(f"\n{category}")
        if isinstance(docs, dict):
            for doc, desc in docs.items():
                if isinstance(desc, dict):
                    for cmd, explanation in desc.items():
                        print(f"  {cmd:30s} - {explanation}")
                else:
                    print(f"  📄 {doc:28s} - {desc}")
    
    # 显示文件结构
    print("\n" + FILES_OVERVIEW)
    
    # 常见问题
    print("\n\n❓ 常见问题\n" + "-"*70)
    print("""
Q: 系统很慢怎么办?
A: 这是正常的，第一次查询需要生成向量。后续查询会更快。

Q: 推荐结果为空?
A: 需要先加载数据: python backend/load_data.py

Q: 数据加载要多久?
A: 取决于数据量，通常 1-8 小时

Q: 能否自定义推荐数量?
A: 可以，在 .env 中修改 RETRIEVE_TOPK 和 RETURN_TOPN

Q: 如何修改推荐策略?
A: 编辑 backend/recommendation_engine.py

更多问题见: README.md 或 INSTALLATION_GUIDE.md
    """)
    
    # 总结
    print("\n" + "="*70)
    print("✨ 项目已 100% 完成，所有文件已准备就绪")
    print("="*70)
    print("\n👉 建议先阅读: QUICKSTART.md")
    print("\n祝使用愉快! 🚀\n")
