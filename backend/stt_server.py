from fastapi import FastAPI, File, UploadFile
import shutil
import os
from funasr import AutoModel

app = FastAPI(title="STT 语音识别服务")

print("正在加载 FunASR 语音识别模型...")
# 使用 Fun-ASR-Nano，中文识别效果最好
model = AutoModel(
    model="FunAudioLLM/Fun-ASR-Nano-2512",
    hub="ms",
    device="cpu",  # <--- 只改这一处！
    # dtype="float16", # CPU 跑不需要这个，删掉或注释掉都行
    trust_remote_code=True,
    vad_model="fsmn-vad", 
    vad_kwargs={"max_single_segment_time": 30000}
)
print("✅ FunASR 模型加载完毕！")

@app.post("/voice_to_text")
async def voice_to_text(file: UploadFile = File(...)):
    temp_file = "temp_input.wav"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # FunASR 识别
        result = model.generate(input=temp_file, batch_size=1)
        text = result[0]["text"] if result else ""
        return {"text": text.strip()}
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)