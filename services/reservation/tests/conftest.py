"""pytest 配置 — 将 src 目录加入 Python 搜索路径"""
import sys
from pathlib import Path

# 将 services/reservation 目录（即 tests/ 的父目录）加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
