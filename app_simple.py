import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="问卷数据分析平台", page_icon="📊", layout="wide")

st.title("📊 问卷数据分析平台 - 调试版本")

st.info("正在测试基础功能...")

# 测试文件上传
uploaded_file = st.file_uploader("上传Excel或CSV文件", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # 判断文件类型
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"文件加载成功！共 {len(df)} 条数据")
        
        # 显示数据预览
        st.subheader("数据预览")
        st.dataframe(df.head())
        
        # 显示列名
        st.subheader("列名列表")
        for col in df.columns:
            st.write(f"- {col}")
            
    except Exception as e:
        st.error(f"文件读取错误: {e}")

st.info("如果看到这条消息，说明基础功能正常")