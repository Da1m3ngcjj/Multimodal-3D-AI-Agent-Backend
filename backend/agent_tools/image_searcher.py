import requests
import os
import re
import webbrowser  # 导入浏览器控制模块
from datetime import datetime
from urllib.parse import quote
import html

def search_and_download_image(keyword: str) -> str:
    print(f"🔍 正在搜索图片: {keyword}")
    try:
        # 1. 视觉欺骗：让电脑真的在浏览器里打开必应搜图（录屏效果拉满）
        search_url = f"https://cn.bing.com/images/search?q={quote(keyword)}"
        print(f"🌐 正在为你打开浏览器进行全网搜索...")
        webbrowser.open(search_url) 
        
        # 2. 后台悄悄用代码去抓取图片链接
        api_url = f"https://www.bing.com/images/async?q={quote(keyword)}&first=1&count=10"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        response = requests.get(api_url, headers=headers, timeout=10)
        matches = re.findall(r'murl&quot;:&quot;(.*?)&quot;', response.text)
        if not matches:
            matches = re.findall(r'"murl":"(.*?)"', response.text)

        save_dir = r"E:\AI\AgentProject\backend\agent_tools\downloaded_images"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"search_{datetime.now().strftime('%H%M%S')}.jpg")

        # 3. 尝试下载
        for raw_url in matches:
            image_url = html.unescape(raw_url)
            try:
                img_response = requests.get(image_url, headers=headers, timeout=5)
                img_response.raise_for_status()
                with open(save_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"✅ 图片已成功保存至: {save_path}")
                return save_path
            except Exception:
                continue

        return "❌ 所有链接都下载失败了"
    except Exception as e:
        print(f"❌ 搜图流程失败: {e}")
        return ""