from fastapi import FastAPI
from pydantic import BaseModel
import os
# 【极其关键】强制 PyTorch 不要占用额外的显存缓存
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["CUDA_VISIBLE_DEVICES"] = "0" 

import time
import uuid
import re 
from fastapi.staticfiles import StaticFiles
from indextts.infer_v2_5 import IndexTTS2

app = FastAPI(title="TTS 服务")

os.makedirs("temp_audio", exist_ok=True)
app.mount("/audio", StaticFiles(directory="temp_audio"), name="audio")

print("正在加载 IndexTTS2...")
TTS_MODEL_DIR = r"E:\AI\AgentProject\index-tts\checkpoints"
PROMPT_AUDIO_PATH = r"E:\AI\AgentProject\index-tts\ReferenceAudio\TestAudio.wav"

tts = IndexTTS2(cfg_path=os.path.join(TTS_MODEL_DIR, "config.yaml"), model_dir=TTS_MODEL_DIR, use_bf16=True)
print("✅ TTS 加载完毕！")

class TTSRequest(BaseModel):
    text: str

@app.post("/generate_voice")
def generate_voice(request: TTSRequest):
    try:
        clean_text = re.sub(r'[*#_`~>]', '', request.text)
        
        # 【优化版清理逻辑】直接清理 temp_audio 下的所有旧 .wav 文件
        # 因为前端只要请求了，下载后就不需要这个临时文件了
        for f in os.listdir("temp_audio"):
            f_path = os.path.join("temp_audio", f)
            if os.path.isfile(f_path) and f.endswith(".wav"):
                try:
                    os.remove(f_path)
                except:
                    pass # 防止文件正在被下载时被强删

        file_name = f"{uuid.uuid4().hex}.wav"
        file_path = os.path.join("temp_audio", file_name)
        
        tts.infer(spk_audio_prompt=PROMPT_AUDIO_PATH, text=clean_text, output_path=file_path, lang="zh")
        return {"audio_url": f"http://127.0.0.1:8001/audio/{file_name}"}
    except Exception as e:
        return {"error": str(e)}