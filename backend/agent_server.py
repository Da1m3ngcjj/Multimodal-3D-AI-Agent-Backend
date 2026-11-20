from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import re
import json
import os

# 引入工具
from agent_tools.image_searcher import search_and_download_image
from agent_tools.model_generator import generate_3d_model  

app = FastAPI(title="AR Agent 服务")

print("正在启动服务并加载模型...")
embedding_model = SentenceTransformer(r'E:\AI\AgentProject\bge-small-zh-v1.5')
client_db = chromadb.PersistentClient(path=r"E:\AI\AgentProject\backend\chroma_db")
collection = client_db.get_collection(name="ar_manual")
llm = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")

class ChatRequest(BaseModel):
    message: str

# ================= 定义工具 =================
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_and_download_image",
            "description": "当用户要求找图片、下载图片、需要视觉参考时调用此工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "图片搜索关键词，最好用英文"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_3d_model",
            # 【修改点】这里加了“必须先找图”的强限制，这是解决你问题的关键！
            "description": "当用户要求生成 3D 模型、建模型、导入 Unity 时调用此工具。注意：调用此工具前，必须且优先调用 search_and_download_image 获取参考图。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "要生成的模型名称"}
                },
                "required": ["keyword"]
            }
        }
    }
]

@app.post("/chat")
def chat_with_rag(request: ChatRequest):
    question = request.message
    
    # ================= 1. 意图路由（让大模型自己决定用不用工具） =================
    route_response = llm.chat.completions.create(
        model="qwen3:8b",
        messages=[{"role": "user", "content": question + " /no_think"}],
        tools=tools,
        tool_choice="auto"
    )
    
    message = route_response.choices[0].message
    
    if message.tool_calls:
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            keyword = args.get("keyword")
            
            # 1. 搜图任务
            if tool_call.function.name == "search_and_download_image":
                print(f"🤖 Agent 决定执行搜图任务: {keyword}")
                img_path = search_and_download_image(keyword)
                if img_path:
                    # 直接返回图片，前端拿到后会自动触发后续的建模剧本
                    return {"reply": f"已经为你找到相关参考图了！|PATH|{img_path}", "action": "download_image"}
                    
            # 2. 建模型任务（如果大模型直接跳过搜图调用了这个）
            elif tool_call.function.name == "generate_3d_model":
                print(f"🔮 Agent 决定生成 3D 模型: {keyword}")
                generate_3d_model(keyword) 
                return {"reply": f"✅ {keyword}的 3D 模型已生成并导入场景！", "action": "generate_3d", "model_name": keyword}

    # ================= 2. RAG 知识库流程 =================
    print("🧠 Agent 决定走 RAG 知识库检索流程")
    
    greeting_words = ["你好", "你是谁", "hello", "hi", "在吗", "谢谢", "再见"]
    is_chitchat = len(question) <= 4 or any(word in question.lower() for word in greeting_words)
    
    if is_chitchat:
        context = "（用户正在寒暄，无需参考文档，请直接友好回复）"
    else:
        query_vector = embedding_model.encode(question).tolist()
        results = collection.query(query_embeddings=[query_vector], n_results=3)
        context = "\n\n".join(results['documents'][0])
    
    prompt = f"""你是一个智能、友好的 AR 助手。
请先判断用户的输入类型：
- 如果用户是在打招呼或闲聊，请直接以纯文本自然、友好地回答。
- 如果用户是在询问专业知识或设备操作，请严格根据下面提供的【文档片段】来回答。
- 如果【文档片段】中找不到答案，请以自然的口吻回答：“抱歉，我的资料库里暂时没有记录关于这个问题的信息，建议您查阅其他手册或联系人工客服。”

绝对不要使用任何 Markdown 符号（如 **、#、- 等）。
请将回答控制在 100 字以内，保持简短精炼。

【文档片段】：
{context}

【用户问题】：
{question}
/no_think
"""
    
    response = llm.chat.completions.create(
        model="qwen3:8b",
        messages=[{"role": "user", "content": prompt + " /no_think"}]
    )
    
    reply = response.choices[0].message.content
    clean_reply = re.sub(r'[*#_`~>]', '', reply)
    
    return {"reply": clean_reply, "action": "chat"}