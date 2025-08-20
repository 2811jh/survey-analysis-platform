import os
os.environ["LOKY_PICKLER"] = "pickle"
os.environ["JOBLIB_START_METHOD"] = "loky"
import pandas as pd
import jieba
import re
import warnings
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning, module="joblib")

# ================== 功能模块 ==================

# 1. 变量识别模块
def load_data(file_path, text_var, other_vars):
    df = pd.read_excel(file_path)
    return df[[text_var] + other_vars].copy()

# 2. 文本清洗模块
def clean_text(df, text_var, invalid_words=['无', ' ']):
    df[text_var] = df[text_var].str.strip()
    cond = df[text_var].isin(invalid_words) | df[text_var].isna()
    return df[~cond].reset_index(drop=True)

# 3. 标签匹配模块（核心修改）
def manual_tagging(text, tag_keywords, 
                  negation_words={"不", "没", "未", "无", "非", "勿"},
                  max_context=3):
    """
    增强版标签匹配逻辑：
    1. 分句处理避免跨句误判
    2. 整句级否定检测
    3. 关键词上下文否定检测
    """
    matched_tags = set()
    matched_keywords = set()
    
    # 分句处理（支持中文标点）
    sentences = re.split(r'[,.，。！？；\n]', text)
    
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # 整句否定检测
        if any(nw in sent for nw in negation_words):
            continue
            
        # 遍历所有标签和关键词
        for tag, keywords in tag_keywords.items():
            for kw in keywords:
                kw_pos = sent.find(kw)
                if kw_pos == -1:
                    continue
                
                # 上下文否定检测
                context_start = max(0, kw_pos - max_context)
                context_end = min(len(sent), kw_pos + len(kw) + max_context)
                context = sent[context_start:context_end]
                
                if not any(nw in context for nw in negation_words):
                    matched_tags.add(tag)
                    matched_keywords.add(kw)
    
    return ", ".join(matched_tags), ", ".join(matched_keywords)
    
# 4. 词云分析模块
def generate_wordcloud(texts, stopwords, save_path=None, font_path='simhei.ttf'):
    # 新增文本预处理
    def preprocess(text):
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', str(text))
        # 精确分词
        return [word for word in jieba.lcut(text) 
                if len(word) > 1 and word not in stopwords]
    
    # 合并所有文本并预处理
    all_words = []
    for text in texts:
        all_words.extend(preprocess(text))
    
    # 手动统计词频
    word_freq = Counter(all_words)
    
    # 过滤低频词
    min_freq = 2  # 可调节参数
    filtered_freq = {k:v for k,v in word_freq.items() if v >= min_freq}
    
    # 如果没有有效词频，创建默认词云
    if not filtered_freq:
        filtered_freq = {'暂无数据': 1}
    
    # 生成词云
    try:
        wc = WordCloud(
            font_path=font_path,
            background_color='white',
            width=1600,
            height=1200,
            max_words=40,
            colormap='viridis'
        )
    except:
        # 如果字体文件不存在，使用默认设置
        wc = WordCloud(
            background_color='white',
            width=1600,
            height=1200,
            max_words=40,
            colormap='viridis'
        )
    
    wc.generate_from_frequencies(filtered_freq)
    
    # 绘图设置
    plt.figure(figsize=(16, 12))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

# 5. 文本聚类模块
def text_clustering(texts, n_clusters=10, max_samples=20):
    # 确保有足够的文本进行聚类
    n_clusters = min(n_clusters, len(texts))
    
    tfidf = TfidfVectorizer(max_features=500)
    X = tfidf.fit_transform(texts)
    
    kmeans = KMeans(
        n_clusters=n_clusters,
        n_init=10,
        random_state=42,
        init='k-means++'
    )
    
    clusters = kmeans.fit_predict(X)
    
    results = []
    for cluster_id in range(n_clusters):
        cluster_texts = [t for t, c in zip(texts, clusters) if c == cluster_id]
        results.append({
            "cluster": cluster_id,
            "count": len(cluster_texts),
            "examples": cluster_texts[:max_samples]
        })
    return pd.DataFrame(results), clusters

# 6. 结果输出模块
def export_results(df, cluster_df, output_path):
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name='分析结果', index=False)
        cluster_df.to_excel(writer, sheet_name='聚类统计', index=False)

# 默认标签关键词配置
DEFAULT_TAG_KEYWORDS = {
    # 核心玩法
    "核心玩法": [
        r"(?:非常|超级|特别|极其|十分|好)好玩", "生存", "创造", "红石", "指令", "合成表", "附魔", "村民交易",
        "下界传送门", "末地船", "刷怪塔", "生电", "挖矿", "建筑",
        "冒险", "探索", "起床战争", "空岛生存", "PVP", "跑酷"
    ],
    
    # 社交与联机
    "社交联机": [
        "设计", "联机","好友", "服务器", "租赁服", "联机大厅", "多人游戏", "社交",
        "组队", "语音", "聊天", "领地", "经济系统", "小游戏",
        "RPG", "起床战争", "玩家素质", "举报系统"
    ],
    
    # 性能与优化
    "性能体验": [
        "卡顿", "闪退", "加载慢", "掉帧", "内存不足", "FPS",
        "渲染错误", "崩溃报告", "发热", "网络延迟", "掉线",
        "按键冲突", "触控优化", "横屏适配", "竖屏操作"
    ],
    
    # 内容更新
    "版本特性": [
        "1.20", "考古系统", "樱花木", "骆驼", "悦灵", "幽匿系列",
        "红树林", "Trails & Tales", "试炼大厅", "紫水晶",
        "考古", "风铃", "惊变100天", "魔法指令"
    ],
    
    # 模组生态
    "模组组件": [
        "模组","组件","MOD","mod","光影", "材质包", "数据包", "JEI", "Optifine", 
        "连锁挖矿", "惊变", "魔法", "枪械", "机甲",
        "家具", "科技模组", "神奇宝贝", "暮色森林",
        "等价交换", "工业时代", "匠魂"
    ],
    
    # 商业化
    "商业化": [
        "钻石", "绿宝石", "皮肤", "会员", "抽奖", "充值",
        "付费模组", "免费试玩", "福利活动", "礼包",
        "4D皮肤", "传奇皮肤", "坐骑", "特效"
    ]
}

# 默认否定词
DEFAULT_NEGATION_WORDS = {
    # 基础否定
    "不", "没", "未", "无", "非", "勿", "无需", "别", "莫",
    # 语义否定
    "不再", "不会", "不需要", "不应该", "不存在", "未遇到",
    # 转折关联词
    "但是", "然而", "其实", "实际上", "尽管",
    # 方言/口语变体
    "冇", "唔", "冇得", "罢了"
}