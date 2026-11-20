import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# ================= 1. 配置参数 =================
# 把这里改成文件夹路径！程序会自动扫描里面所有的 PDF 和 TXT
DOC_DIR = r"E:\AI\AgentProject\data\documents" 
DB_PATH = r"E:\AI\AgentProject\backend\chroma_db"  # 本地数据库存放的文件夹
MODEL_PATH = r'E:\AI\AgentProject\bge-small-zh-v1.5' # 本地向量模型路径

# ================= 2. 批量读取文档 =================
print("正在扫描文件夹中的文档...")
text = ""

if not os.path.exists(DOC_DIR):
    print(f"❌ 找不到文件夹: {DOC_DIR}，请检查路径！")
    exit()

for filename in os.listdir(DOC_DIR):
    file_path = os.path.join(DOC_DIR, filename)
    
    # 读取 PDF
    if filename.lower().endswith(".pdf"):
        print(f"📖 正在读取 PDF: {filename}")
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                extract_text = page.extract_text()
                if extract_text:
                    text += extract_text + "\n"
        except Exception as e:
            print(f"⚠️ 读取 {filename} 失败: {e}")
            
    # 读取 TXT
    elif filename.lower().endswith(".txt"):
        print(f"📖 正在读取 TXT: {filename}")
        with open(file_path, "r", encoding="utf-8") as f:
            text += f.read() + "\n"

if len(text.strip()) == 0:
    print("❌ 文件夹里没有读取到任何有效文字，请检查文档内容。")
    exit()

print(f"✅ 所有文档读取完毕，总计 {len(text)} 个字符。")

# ================= 3. 文档切片 =================
print("正在切分文档...")
# 把长文档切成小段（每段500字，重叠50字，防止上下文断裂）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = text_splitter.split_text(text)
print(f"文档被切分成了 {len(chunks)} 段。")

# ================= 4. 加载向量模型 & 存入数据库 =================
print("正在加载本地向量模型...")
embedding_model = SentenceTransformer(MODEL_PATH)

print("正在将数据写入向量数据库...")
client = chromadb.PersistentClient(path=DB_PATH)

# 每次运行先清空旧数据，防止重复
try:
    client.delete_collection(name="ar_manual")
except:
    pass

collection = client.create_collection(name="ar_manual")

# 把切好的文本转成向量，并存入数据库
valid_count = 0
for i, chunk in enumerate(chunks):
    # 【关键修复】过滤掉空字符串、纯空格、以及损坏的 Unicode
    if not chunk or not chunk.strip():
        continue
    
    # 清理掉无法编码的字符（防止 lone surrogate 报错）
    try:
        chunk.encode('utf-8')
    except UnicodeEncodeError:
        chunk = chunk.encode('utf-8', errors='ignore').decode('utf-8')
    
    if not chunk.strip():
        continue

    vector = embedding_model.encode(chunk).tolist()
    collection.add(
        embeddings=[vector],
        documents=[chunk],
        ids=[str(valid_count)]
    )
    valid_count += 1

print(f"✅ 实际入库了 {valid_count} 段有效内容（已过滤空段落）。")

print("✅ RAG 知识库构建完成！可以开始提问了。")