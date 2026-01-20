"""Run the system with proper error handling"""
import subprocess
import sys
import os
from pathlib import Path
import time
import signal

def print_header():
    """Print system header"""
    print("\n" + "="*70)
    print(" "*15 + "Amazon Recommendation System")
    print("="*70 + "\n")


def check_prerequisites():
    """Check all prerequisites before starting"""
    print("📋 检查系统先决条件...\n")
    
    checks = {
        "Python 3.9+": lambda: sys.version_info >= (3, 9),
        "PostgreSQL (可访问)": check_postgres,
        "Ollama 服务": check_ollama,
        ".env 文件": lambda: Path(".env").exists(),
        "依赖包": check_packages,
    }
    
    all_passed = True
    for name, check_func in checks.items():
        try:
            if check_func():
                print(f"✅ {name:30s} OK")
            else:
                print(f"❌ {name:30s} FAILED")
                all_passed = False
        except Exception as e:
            print(f"❌ {name:30s} FAILED - {str(e)[:40]}")
            all_passed = False
    
    print()
    return all_passed


def check_postgres():
    """Check PostgreSQL"""
    try:
        from backend.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except:
        return False


def check_ollama():
    """Check Ollama"""
    try:
        import requests
        response = requests.get("http://0.0.0.0:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False


def check_packages():
    """Check Python packages"""
    required = ["sqlalchemy", "fastapi", "pgvector"]
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            return False
    return True


def start_backend():
    """Start backend service"""
    print("🚀 启动后端 API 服务 (8000)...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "backend.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Wait for startup
        print("✅ 后端已启动")
        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None


def start_frontend():
    """Start frontend service"""
    print("🌐 启动前端服务 (8001)...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "frontend.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Wait for startup
        print("✅ 前端已启动")
        return process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None


def print_access_info():
    """Print access information"""
    print("\n" + "="*70)
    print("🎉 系统已启动！请访问以下地址:\n")
    print("  🌐 前端界面:         http://0.0.0.0:8001")
    print("  📚 API 文档:        http://0.0.0.0:8000/docs")
    print("  🔧 API 基础 URL:    http://0.0.0.0:8000\n")
    print("="*70 + "\n")


def main():
    """Main entry point"""
    print_header()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ 系统先决条件检查失败。请检查 README.md 或 QUICKSTART.md\n")
        return 1
    
    print("🔧 启动服务...\n")
    
    # Start services
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    if not backend_process or not frontend_process:
        print("\n❌ 启动失败，请检查日志")
        return 1
    
    print_access_info()
    print("按 Ctrl+C 停止服务\n")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 停止服务...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        time.sleep(1)
        print("✅ 服务已停止")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    sys.exit(main())
