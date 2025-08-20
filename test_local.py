#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本地测试脚本 - 验证应用是否可以运行"""

import sys
import os

print("开始测试应用...")

# 测试导入
try:
    print("1. 测试导入streamlit...")
    import streamlit as st
    print("   ✓ streamlit导入成功")
except ImportError as e:
    print(f"   ✗ streamlit导入失败: {e}")
    sys.exit(1)

try:
    print("2. 测试导入pandas...")
    import pandas as pd
    print("   ✓ pandas导入成功")
except ImportError as e:
    print(f"   ✗ pandas导入失败: {e}")
    sys.exit(1)

try:
    print("3. 测试导入numpy...")
    import numpy as np
    print("   ✓ numpy导入成功")
except ImportError as e:
    print(f"   ✗ numpy导入失败: {e}")
    sys.exit(1)

# 测试分析模块
try:
    print("4. 测试导入cross_analysis...")
    from cross_analysis import process_crosstab
    print("   ✓ cross_analysis导入成功")
except ImportError as e:
    print(f"   ✗ cross_analysis导入失败: {e}")
    
try:
    print("5. 测试导入text_analysis...")
    from text_analysis import clean_text, manual_tagging
    print("   ✓ text_analysis导入成功")
except ImportError as e:
    print(f"   ✗ text_analysis导入失败: {e}")

print("\n所有模块测试完成！")
print("\n要运行应用，请执行: streamlit run app.py")