import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
import time

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
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主题色配置 */
    :root {
        --primary-color: #1E88E5;
        --secondary-color: #43A047;
        --accent-color: #FB8C00;
        --background-color: #F5F7FA;
    }
    
    /* 优化整体布局 */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* 美化标题 */
    h1 {
        background: linear-gradient(120deg, #1E88E5, #43A047);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        text-align: center;
        padding: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 美化卡片容器 */
    .stExpander {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.9);
        margin: 1rem 0;
    }
    
    /* 美化按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5, #43A047);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.6);
    }
    
    /* 美化侧边栏 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1E88E5 0%, #43A047 100%);
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0f2f6 100%);
        border-right: 2px solid #e0e0e0;
    }
    
    /* 美化文件上传器 */
    .stFileUploader {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 2px dashed #1E88E5;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #43A047;
        background: #f0f9ff;
    }
    
    /* 美化选择框 */
    .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    /* 美化多选框 */
    .stMultiSelect > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    /* 优化表格样式 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* 美化指标卡片 */
    [data-testid="metric-container"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1E88E5;
    }
    
    /* 添加加载动画 */
    .stSpinner > div {
        border-color: #1E88E5 !important;
    }
    
    /* 美化成功消息 */
    .stSuccess {
        background: linear-gradient(135deg, #43A047, #66BB6A);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 600;
    }
    
    /* 美化错误消息 */
    .stError {
        background: linear-gradient(135deg, #EF5350, #E53935);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 600;
    }
    
    /* 动画效果 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# 优化的标题和说明
st.markdown("""
<div style="background: white; border-radius: 20px; padding: 2rem; margin: -2rem -2rem 2rem -2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
    <h1 style="margin: 0;">📊 问卷数据分析平台</h1>
    <p style="text-align: center; color: #666; font-size: 1.2rem; margin-top: 1rem;">
        专业的问卷数据处理与分析工具
    </p>
</div>
""", unsafe_allow_html=True)

# 功能介绍卡片
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E88E5, #42A5F5); color: white; padding: 1.5rem; border-radius: 15px; height: 150px;">
        <h3>📈 交叉分析</h3>
        <p>• 支持单选题和多选题交叉统计<br>
        • 自动计算显著性检验<br>
        • 生成专业的Excel报告</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #43A047, #66BB6A); color: white; padding: 1.5rem; border-radius: 15px; height: 150px;">
        <h3>📝 文本分析</h3>
        <p>• 智能文本挖掘和分类<br>
        • 生成美观的词云图<br>
        • 自动聚类分析</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 性能优化：缓存数据读取函数
@st.cache_data(show_spinner=False)
def load_data(file, file_type):
    """缓存文件读取，避免重复加载"""
    if file_type == 'csv':
        try:
            return pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return pd.read_csv(file, encoding='gbk')
            except UnicodeDecodeError:
                return pd.read_csv(file, encoding='latin-1')
    else:
        return pd.read_excel(file)

# 性能优化：缓存交叉分析结果
@st.cache_data(show_spinner=False)
def cached_crosstab(df_hash, row_questions, col_questions, sig_level, percent_format, data_column_width):
    """缓存交叉分析结果"""
    temp_input = f"temp_input_{df_hash}.xlsx"
    temp_output = f"temp_output_{df_hash}.xlsx"
    
    # 这里需要重新创建DataFrame，因为cache不能直接存储DataFrame
    # 实际使用时会从缓存的数据重新创建
    return None, None  # 占位符，实际实现在下面

# 侧边栏选择功能
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #1E88E5, #43A047); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <h3 style="margin: 0; text-align: center;">⚙️ 控制面板</h3>
</div>
""", unsafe_allow_html=True)

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
    # 根据文件类型读取数据（使用缓存）
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # 显示加载动画
        with st.spinner('🔄 正在加载数据...'):
            df = load_data(uploaded_file, file_extension)
            time.sleep(0.5)  # 给用户一个视觉反馈
        
        # 成功提示带动画
        success_placeholder = st.sidebar.empty()
        success_placeholder.success(f"✅ 文件加载成功！共 {len(df)} 条数据，{len(df.columns)} 个字段")
        
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
        
        # 执行分析（带美化按钮）
        if st.button("🚀 开始分析", type="primary", use_container_width=True):
            if row_questions and col_questions:
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 分步执行，显示进度
                    status_text.text("📊 正在准备数据...")
                    progress_bar.progress(20)
                    time.sleep(0.5)
                    
                    # 保存上传的文件到临时目录
                    temp_input = "temp_input.xlsx"
                    temp_output = "temp_output.xlsx"
                    df.to_excel(temp_input, index=False)
                    
                    status_text.text("⚙️ 正在执行交叉分析...")
                    progress_bar.progress(60)
                    
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
                    
                    status_text.text("📈 正在生成结果...")
                    progress_bar.progress(90)
                    time.sleep(0.5)
                    
                    # 完成进度条
                    status_text.text("✅ 分析完成！")
                    progress_bar.progress(100)
                    time.sleep(1)
                    
                    # 清除进度条
                    progress_bar.empty()
                    status_text.empty()
                    
                    # 成功消息
                    st.balloons()  # 添加庆祝动画
                    st.success("🎉 交叉分析完成！")
                    
                    # 显示结果
                    st.subheader("📊 交叉统计结果")
                    with st.container():
                        st.dataframe(crosstab_df.head(50), use_container_width=True)
                    
                    # 下载按钮（美化）
                    with open(temp_output, 'rb') as f:
                        st.download_button(
                            label="📥 下载完整结果",
                            data=f.read(),
                            file_name=f"交叉分析结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    # 清理临时文件
                    os.remove(temp_input)
                    os.remove(temp_output)
                        
                except Exception as e:
                    st.error(f"❌ 分析出错: {str(e)}")
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
        if st.button("🚀 开始文本分析", type="primary", use_container_width=True):
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