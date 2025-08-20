import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime

# 安全导入分析模块
try:
    from cross_analysis import process_crosstab
    CROSS_ANALYSIS_AVAILABLE = True
except ImportError:
    CROSS_ANALYSIS_AVAILABLE = False
    st.error("交叉分析模块加载失败")

try:
    from text_analysis import (
        clean_text, manual_tagging, generate_wordcloud, 
        text_clustering, export_results
    )
    TEXT_ANALYSIS_AVAILABLE = True
except ImportError:
    TEXT_ANALYSIS_AVAILABLE = False
    st.error("文本分析模块加载失败")

# 页面配置
st.set_page_config(
    page_title="问卷数据分析平台",
    page_icon="📊",
    layout="wide"
)

# 标题和说明
st.title("📊 问卷数据分析平台")
st.markdown("""
### 功能介绍
- **交叉分析**: 对问卷数据进行交叉统计，支持显著性检验
- **文本分析**: 对开放题进行文本挖掘、词云生成和聚类分析
""")

# 侧边栏选择功能
analysis_type = st.sidebar.selectbox(
    "选择分析类型",
    ["交叉分析", "文本分析"]
)

# 文件上传
uploaded_file = st.sidebar.file_uploader(
    "上传数据文件",
    type=['xlsx', 'xls', 'csv'],
    help="支持Excel文件(.xlsx, .xls)和CSV文件(.csv)"
)

if uploaded_file is not None:
    # 根据文件类型读取数据
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            # 尝试不同编码读取CSV
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(uploaded_file, encoding='gbk')
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            # 读取Excel文件
            df = pd.read_excel(uploaded_file)
        
        st.sidebar.success(f"✅ 文件加载成功！共 {len(df)} 条数据，{len(df.columns)} 个字段")
        
        # 显示文件信息
        with st.sidebar.expander("📊 文件信息"):
            st.write(f"**文件名:** {uploaded_file.name}")
            st.write(f"**文件类型:** {file_extension.upper()}")
            st.write(f"**数据行数:** {len(df)}")
            st.write(f"**字段数量:** {len(df.columns)}")
            
    except Exception as e:
        st.sidebar.error(f"❌ 文件读取失败: {str(e)}")
        st.stop()
    
    # 显示列名供选择
    columns = df.columns.tolist()
    
    # 添加数据预览功能
    with st.expander("🔍 数据预览", expanded=False):
        st.subheader("前5行数据")
        st.dataframe(df.head(), use_container_width=True)
        
        st.subheader("数据概览")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总行数", len(df))
        with col2:
            st.metric("总列数", len(df.columns))
        with col3:
            st.metric("缺失值", df.isnull().sum().sum())
        
        # 显示字段列表
        st.subheader("字段列表")
        for i, col in enumerate(df.columns, 1):
            st.write(f"{i}. **{col}** (类型: {df[col].dtype})")
    
    if analysis_type == "交叉分析":
        st.header("📈 交叉分析")
        
        if not CROSS_ANALYSIS_AVAILABLE:
            st.error("交叉分析功能暂时不可用，请稍后重试")
            st.stop()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("行变量配置")
            row_questions = st.multiselect(
                "选择行变量（支持多选）",
                columns,
                help="选择要作为行维度的问题"
            )
        
        with col2:
            st.subheader("列变量配置")
            col_questions = st.multiselect(
                "选择列变量（支持多选）",
                columns,
                help="选择要作为列维度的问题"
            )
        
        # 高级选项
        with st.expander("高级选项"):
            col1, col2, col3 = st.columns(3)
            with col1:
                sig_level = st.selectbox(
                    "显著性水平",
                    [0.05, 0.01, 0.001],
                    index=0
                )
            with col2:
                percent_format = st.text_input(
                    "百分比格式",
                    value="0.00%"
                )
            with col3:
                data_column_width = st.number_input(
                    "数据列宽度",
                    min_value=10,
                    max_value=50,
                    value=20
                )
        
        # 执行分析
        if st.button("开始分析", type="primary"):
            if row_questions and col_questions:
                with st.spinner("正在执行交叉分析..."):
                    try:
                        # 保存上传的文件到临时目录
                        temp_input = "temp_input.xlsx"
                        temp_output = "temp_output.xlsx"
                        df.to_excel(temp_input, index=False)
                        
                        # 执行分析
                        crosstab_df, sig_df = process_crosstab(
                            input_file=temp_input,
                            output_file=temp_output,
                            row_questions=row_questions,
                            col_questions=col_questions,
                            sig_levels=[sig_level],
                            percent_format=percent_format,
                            data_column_width=data_column_width
                        )
                        
                        st.success("分析完成！")
                        
                        # 显示结果
                        st.subheader("交叉统计结果")
                        st.dataframe(crosstab_df.head(50))
                        
                        # 下载按钮
                        with open(temp_output, 'rb') as f:
                            st.download_button(
                                label="📥 下载完整结果",
                                data=f.read(),
                                file_name=f"交叉分析结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        # 清理临时文件
                        os.remove(temp_input)
                        os.remove(temp_output)
                        
                    except Exception as e:
                        st.error(f"分析出错: {str(e)}")
            else:
                st.warning("请选择行变量和列变量")
    
    elif analysis_type == "文本分析":
        st.header("📝 文本分析")
        
        if not TEXT_ANALYSIS_AVAILABLE:
            st.error("文本分析功能暂时不可用，请稍后重试")
            st.stop()
        
        # 选择文本列
        text_column = st.selectbox(
            "选择文本列",
            columns,
            help="选择包含文本内容的列"
        )
        
        # 其他变量
        other_vars = st.multiselect(
            "选择其他变量（可选）",
            [col for col in columns if col != text_column],
            help="选择要保留的其他列"
        )
        
        # 停用词配置
        with st.expander("停用词配置"):
            default_stopwords = ["的", "了", "是", "有些", "因为", "游戏", "世界", 
                               "而且", "非常", "建议", "希望", "什么", "不要"]
            stopwords_text = st.text_area(
                "停用词（每行一个）",
                value="\n".join(default_stopwords),
                height=200
            )
            stopwords = stopwords_text.split("\n")
        
        # 标签配置
        with st.expander("标签关键词配置"):
            st.markdown("配置标签和对应的关键词，用于文本分类")
            
            # 默认标签配置
            default_tags = {
                "核心玩法": ["好玩", "生存", "创造", "红石", "指令"],
                "社交联机": ["联机", "好友", "服务器", "多人游戏"],
                "性能体验": ["卡顿", "闪退", "加载慢", "掉帧"],
                "版本特性": ["更新", "版本", "1.20", "新功能"],
                "模组组件": ["模组", "MOD", "mod", "光影", "材质包"]
            }
            
            # 动态添加标签
            tag_keywords = {}
            for tag, keywords in default_tags.items():
                keywords_str = st.text_input(
                    f"{tag} 关键词（逗号分隔）",
                    value=", ".join(keywords)
                )
                if keywords_str:
                    tag_keywords[tag] = [k.strip() for k in keywords_str.split(",")]
        
        # 聚类参数
        col1, col2 = st.columns(2)
        with col1:
            n_clusters = st.slider(
                "聚类数量",
                min_value=3,
                max_value=20,
                value=10
            )
        with col2:
            max_samples = st.slider(
                "每类显示样本数",
                min_value=5,
                max_value=50,
                value=20
            )
        
        # 执行分析
        if st.button("开始分析", type="primary"):
            with st.spinner("正在执行文本分析..."):
                try:
                    # 数据准备
                    text_df = df[[text_column] + other_vars].copy()
                    
                    # 文本清洗
                    invalid_words = ['无', ' ', '没有', '不知道']
                    clean_df = clean_text(text_df, text_column, invalid_words)
                    
                    st.info(f"清洗后数据量: {len(clean_df)} 条")
                    
                    # 标签匹配
                    if tag_keywords:
                        clean_df[["匹配标签", "匹配关键词"]] = clean_df[text_column].apply(
                            lambda x: pd.Series(manual_tagging(x, tag_keywords))
                        )
                    
                    # 生成词云
                    st.subheader("词云图")
                    wordcloud_path = "temp_wordcloud.png"
                    generate_wordcloud(
                        texts=clean_df[text_column],
                        stopwords=stopwords,
                        save_path=wordcloud_path
                    )
                    
                    # 显示词云
                    if os.path.exists(wordcloud_path):
                        st.image(wordcloud_path, caption="词云分析结果")
                        
                        # 提供词云下载
                        with open(wordcloud_path, "rb") as f:
                            st.download_button(
                                label="📥 下载词云图",
                                data=f.read(),
                                file_name=f"词云图_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                mime="image/png"
                            )
                        os.remove(wordcloud_path)
                    
                    # 文本聚类
                    st.subheader("文本聚类结果")
                    cluster_df, cluster_labels = text_clustering(
                        clean_df[text_column],
                        n_clusters=n_clusters,
                        max_samples=max_samples
                    )
                    clean_df["聚类标签"] = cluster_labels
                    
                    # 显示聚类统计
                    st.dataframe(cluster_df)
                    
                    # 导出结果
                    output_path = "temp_text_analysis.xlsx"
                    export_results(clean_df, cluster_df, output_path)
                    
                    # 下载按钮
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="📥 下载分析结果",
                            data=f.read(),
                            file_name=f"文本分析结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    os.remove(output_path)
                    
                    st.success("文本分析完成！")
                    
                except Exception as e:
                    st.error(f"分析出错: {str(e)}")
                    
else:
    st.info("👈 请在左侧上传Excel文件开始分析")

# 页脚
st.markdown("---")
st.markdown("📊 问卷数据分析平台 v1.0 | 支持交叉分析和文本挖掘")