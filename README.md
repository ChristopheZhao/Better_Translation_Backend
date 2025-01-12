# Better Translator Backend

一个高性能的网页翻译服务后端，基于大模型能力构建API翻译，支持多种大模型引擎能力，提供高质量的英文到中文翻译服务。

## 功能特点

- 支持 OpenAI 和文心一言翻译引擎
- 智能分段翻译，保持原文格式
- 高性能异步处理
- RESTful API 接口
- 可配置的翻译引擎参数
- 详细的错误处理和日志记录

## 技术栈

- Python 3.10
- FastAPI
- OpenAI API / 文心一言 API
- aiohttp
- uvicorn

## 安装说明

1. 克隆仓库：
\```bash
git clone https://github.com/ChristopheZhao/Better_Translation_Backend.git
cd better-translator/backend
\```

2. 创建并激活虚拟环境(推荐使用 anaconda)：
\```bash
conda create -n better-translator python=3.10
conda activate better-translator
\```

3. 安装依赖：
\```bash
pip install -r requirements.txt
\```

4. 配置环境变量：
将 `.env.example` 复制为 `.env` 并配置以下参数：
\```plaintext
# 选择翻译引擎: "openai" 或 "ernie"
TRANSLATOR_TYPE=openai

# OpenAI 配置
API_KEY=your_openai_api_key

# 文心一言配置（如果使用）
ERNIE_API_KEY=your_ernie_api_key
ERNIE_SECRET_KEY=your_ernie_secret_key
\```

5. 启动服务：
\```bash
python main.py
\```

服务将在 `http://127.0.0.1:8000` 启动。

## API 文档

### 翻译接口

- 端点：`/translate`
- 方法：POST
- 请求体：
\```json
{
    "text": "要翻译的文本",
    "from_lang": "en",
    "to_lang": "zh"
}
\```
- 响应：
\```json
{
    "translated_text": "翻译后的文本"
}
\```

## 配合前端使用

本服务设计为配合 Chrome 扩展前端使用：

1. 确保后端服务正常运行
2. 安装并配置 Chrome 扩展
3. 扩展会自动连接到本地后端服务
4. 支持页面翻译和选中文本翻译

详细的前端配置说明请参考 [Chrome 扩展文档](https://github.com/ChristopheZhao/Better_Translation_Extension/README.md)。

## 开发说明

- 使用 `black` 进行代码格式化
- 使用 `pytest` 运行测试
- 遵循 PEP 8 编码规范

## 许可证

MIT License