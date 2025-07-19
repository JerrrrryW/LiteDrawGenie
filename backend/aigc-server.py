# server.py (最终修正版)

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from io import BytesIO
import base64
import os

app = Flask(__name__)
CORS(app)

# --- Google AI Studio API 配置 ---
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY 环境变量未设置！")

client = genai.Client(api_key=API_KEY)

@app.route('/generate-image', methods=['POST'])
def generate_image_handler():
    json_data = request.get_json()
    if not json_data or 'prompt' not in json_data:
        return jsonify({'error': '请求失败，请在 JSON body 中提供 "prompt" 字段'}), 400

    contents = json_data['prompt']
    print(f"收到请求，prompt: {contents}")

    try:
        # --- 关键修正点 ---
        # 模型要求必须同时接收 TEXT 和 IMAGE
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
              response_modalities=['TEXT', 'IMAGE']  # <-- 改回这里
            )
        )

        # 遍历返回的部分，找到图片数据
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                # 检查 part 是否包含图片数据
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    image_bytes = part.inline_data.data
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    print("图片生成成功，以 Base64 格式返回。")
                    return jsonify({
                        'prompt': contents,
                        'image_base64': base64_image
                    })

        # 如果循环结束都没有找到图片，返回错误
        return jsonify({'error': 'API 返回结果中未找到图片'}), 500

    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({'error': f'服务器内部错误: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)