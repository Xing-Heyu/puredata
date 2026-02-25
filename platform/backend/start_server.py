#!/usr/bin/env python3
"""启动服务器"""
import os
import sys
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    subprocess.run([sys.executable, "simple_main.py"])
