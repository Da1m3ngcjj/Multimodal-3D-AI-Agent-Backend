import time
import subprocess
import os

def generate_3d_model(keyword: str) -> str:
    """
    模拟调用 3D 生成 API 和 Blender 自动化处理的流水线
    """
    print("\n" + "="*60)
    print(f"🔮 [Agent Tool] 接收到 3D 建模任务: {keyword}")
    
    print("⏳ 1. 正在调用云端图生 3D 大模型 (TripoSR) 提取网格...")
    time.sleep(1.5)
    
    print("📦 2. 正在拉取生成的原始高模 (White Mesh)...")
    time.sleep(1.0)
    
    print("🛠️ 3. 正在后台唤起 Blender 进行重拓扑、减面与材质烘焙...")
    
    # ==================== Blender 导演剧本 ====================
    # 注意：请确保你电脑上 Blender 的路径和版本号是对的
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" 
    
    # 你的 .blend 文件存放路径（假设你建了 blender_files 文件夹）
    base_dir = r"E:\AI\AgentProject\backend\agent_tools\blender_files"
    
    # 默认打开刺猬
    blend_file = os.path.join(base_dir, "mock_hedgehog.blend")
    
    # 如果关键词里包含鸟或者 bird，就替换成机械鸟文件
    if "机械鸟" in keyword or "bird" in keyword.lower():
        blend_file = os.path.join(base_dir, "mock_mechbird.blend")
    
    # 真实唤起 Blender（异步执行，不会卡死 Python）
    if os.path.exists(blender_path) and os.path.exists(blend_file):
        try:
            subprocess.Popen([blender_path, blend_file]) 
            print(f"✅ Blender 已成功接管！正在处理: {os.path.basename(blend_file)}")
        except Exception as e:
            print(f"⚠️ Blender 启动失败: {e}")
    else:
        print(f"⚠️ 找不到 Blender 或 文件: {blend_file}")
    # ==========================================================
    
    # 给录屏切屏留出 3 秒的表演时间（看着 Blender 里的模型转）
    time.sleep(3.0) 
    
    print("⚙️ 4. 执行 bpy 脚本: 导出 FBX 至 Unity 资源库...")
    time.sleep(1.0)
    
    print("✅ 5. 流水线执行完毕！模型已成功注入 Unity Resources。")
    print("="*60 + "\n")
    
    # 模拟返回生成的标识符
    return keyword