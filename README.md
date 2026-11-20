# Multimodal-3D-AI-Agent-Backend

## 🎬 项目演示视频
[点击这里观看 1 分钟 Demo 演示](https://b23.tv/gsq9z14)

## 💡 项目简介
本项目是一个完全本地部署的多模态 AI 交互应用后端。采用 Python 微服务架构，支持语音识别（STT）、RAG 知识库检索、大模型意图路由（Agent）、语音合成（TTS）以及外部工具自动化调度（爬虫 + Blender）。

## 🏗️ 技术架构
- **大脑微服务 (8000)**: FastAPI + Ollama (Qwen3-8B) + ChromaDB (RAG) + 工具调用
- **嘴巴微服务 (8001)**: WIndexTTS (极速语音合成)
- **耳朵微服务 (8002)**: FunASR (带 VAD 过滤的语音识别)
- **外部工具**: 自动爬虫搜图 + 唤起本地 Blender 处理 3D 资产

## ⚙️ 运行说明
请参考 `.gitignore` 及代码中的依赖，自行下载大模型权重并配置本地环境。

## 🚀 本地部署步骤
1. 克隆仓库
```bash
git clone https://github.com/Da1m3ngcjj/Multimodal-3D-AI-Agent-Backend
2. 依赖后端仓库
git clone https://github.com/Da1m3ngcjj/Multimodal-3D-AI-Agent-Frontend

