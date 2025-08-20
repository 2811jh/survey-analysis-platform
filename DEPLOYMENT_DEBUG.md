# 🔍 Streamlit Cloud 部署调试指南

## 1. 检查部署状态

### 登录Streamlit Cloud
1. 访问 https://share.streamlit.io/
2. 使用GitHub账号登录
3. 找到你的应用 `survey-analysis-platform`

### 查看部署日志
1. 点击应用名称旁的 "⚙️ Manage app"
2. 选择 "Logs" 标签
3. 查看最新的错误信息

## 2. 常见错误和解决方案

### 错误1: ModuleNotFoundError
**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
检查requirements.txt是否包含所有必要的包

### 错误2: ImportError
**症状**: `ImportError: cannot import name 'xxx' from 'yyy'`

**解决方案**:
可能是代码中的导入语句有问题

### 错误3: SyntaxError
**症状**: `SyntaxError: invalid syntax`

**解决方案**:
代码中有语法错误，需要修复

### 错误4: Memory Error
**症状**: 应用崩溃或无响应

**解决方案**:
优化内存使用，减少数据加载

## 3. 紧急修复步骤

如果主应用无法运行，可以：

### 选项A: 使用简化版本
1. 将 `app_simple.py` 重命名为 `app.py`
2. 推送到GitHub
3. 等待重新部署

### 选项B: 回滚到之前的版本
```bash
# 查看提交历史
git log --oneline

# 回滚到之前的版本（例如CSV支持版本）
git reset --hard 60bc931

# 强制推送
git push --force
```

## 4. 本地测试命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py

# 或运行简化版
streamlit run app_simple.py
```

## 5. 获取帮助

请告诉我以下信息：
1. Streamlit Cloud的具体错误信息
2. Logs中显示的错误类型
3. 应用的URL地址

有了这些信息，我可以快速定位并修复问题！