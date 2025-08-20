# 📊 问卷数据分析平台

一个基于Streamlit的在线问卷数据分析工具，支持交叉分析和文本挖掘。

## 🚀 功能特性

### 交叉分析
- ✅ 支持单选题和多选题交叉统计
- ✅ 自动生成频数和百分比
- ✅ 显著性检验（卡方检验和费舍尔精确检验）
- ✅ 美观的Excel输出格式
- ✅ 数据条可视化

### 文本分析
- ✅ 文本清洗和预处理
- ✅ 自动标签匹配和分类
- ✅ 词云图生成
- ✅ 文本聚类分析
- ✅ 否定词检测

## 🔧 快速开始

### 在线使用
访问：[您的Streamlit应用链接]

### 本地部署
```bash
# 克隆项目
git clone https://github.com/yourusername/survey-analysis-platform.git
cd survey-analysis-platform

# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 📝 使用说明

### 1. 交叉分析
1. 上传Excel文件
2. 选择分析类型为"交叉分析"
3. 配置行变量和列变量
4. 设置高级选项（可选）
5. 点击"开始分析"
6. 下载结果文件

### 2. 文本分析
1. 上传Excel文件
2. 选择分析类型为"文本分析"
3. 选择文本列
4. 配置停用词和标签关键词
5. 设置聚类参数
6. 点击"开始分析"
7. 查看词云图和下载结果

## 📁 项目结构
```
survey-analysis-platform/
├── app.py                 # Streamlit主应用
├── cross_analysis.py      # 交叉分析模块
├── text_analysis.py       # 文本分析模块
├── requirements.txt       # 依赖包
├── README.md             # 说明文档
└── .gitignore           # Git忽略文件
```

## 📋 依赖包
- streamlit - Web应用框架
- pandas - 数据处理
- numpy - 数值计算
- openpyxl - Excel文件处理
- scipy - 统计检验
- scikit-learn - 机器学习
- jieba - 中文分词
- wordcloud - 词云生成
- matplotlib - 图表绘制

## 🤝 贡献
欢迎提交Issue和Pull Request！

## 📄 许可证
MIT License