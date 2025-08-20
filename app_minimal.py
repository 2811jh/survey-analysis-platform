"""最小化测试版本 - 用于排查部署错误"""
import streamlit as st

st.set_page_config(page_title="测试版本", page_icon="🔧")
st.title("🔧 问卷分析平台 - 最小化测试版本")

st.success("✅ Streamlit基础功能正常")

# 测试导入
import_status = []

try:
    import pandas as pd
    import_status.append("✅ pandas导入成功")
except Exception as e:
    import_status.append(f"❌ pandas导入失败: {e}")

try:
    import numpy as np
    import_status.append("✅ numpy导入成功")
except Exception as e:
    import_status.append(f"❌ numpy导入失败: {e}")

try:
    import openpyxl
    import_status.append("✅ openpyxl导入成功")
except Exception as e:
    import_status.append(f"❌ openpyxl导入失败: {e}")

# 显示导入状态
for status in import_status:
    st.write(status)

st.info("如果看到这条消息，说明基础模块工作正常")