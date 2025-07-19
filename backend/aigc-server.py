# server.py (最终修正版 - 已添加文本生成接口)

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
# 确保你已经在环境中设置了 GEMINI_API_KEY
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY 环境变量未设置！")

# 初始化客户端
# genai.configure(api_key=API_KEY) # 老版本的配置方式
# model = genai.GenerativeModel('gemini-1.5-flash')
client = genai.Client(api_key=API_KEY) # 新版本的客户端初始化方式，保持不变

# --- 接口1: 生成图片 ---
@app.route('/generate-image', methods=['POST'])
def generate_image_handler():
    json_data = request.get_json()
    if not json_data or 'prompt' not in json_data:
        return jsonify({'error': '请求失败，请在 JSON body 中提供 "prompt" 字段'}), 400

    prompt = json_data['prompt']
    print(f"收到图片生成请求，prompt: {prompt}")

    try:
        # 使用专门用于生成图片的模型
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
              response_modalities=['TEXT', 'IMAGE']
            )
        )

        # 遍历返回的部分，找到图片数据
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    image_bytes = part.inline_data.data
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    print("图片生成成功，以 Base64 格式返回。")
                    return jsonify({
                        'prompt': prompt,
                        'image_base64': base64_image
                    })

        # 如果循环结束都没有找到图片，返回错误
        print("API 返回结果中未找到图片数据。")
        return jsonify({'error': 'API 返回结果中未找到图片'}), 500

    except Exception as e:
        print(f"图片生成时发生错误: {e}")
        return jsonify({'error': f'服务器内部错误: {e}'}), 500

# --- 接口2: 生成文字 (新增) ---
@app.route('/generate-text', methods=['POST'])
def generate_text_handler():
    json_data = request.get_json()
    if not json_data or 'prompt' not in json_data:
        return jsonify({'error': '请求失败，请在 JSON body 中提供 "prompt" 字段'}), 400

    prompt = json_data['prompt']
    print(f"收到文本生成请求，prompt: {prompt}")

    try:
        # 使用强大的文本模型，如 gemini-1.5-flash
        # 注意：这里的模型名称与生成图片所用的不同
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # 这是一个高效的文本模型
            contents=prompt
        )
        
        # 直接从 response.text 获取文本回复
        text_response = response.text
        print("文本生成成功。")

        return jsonify({
            'prompt': prompt,
            'text_response': text_response
        })

    except Exception as e:
        print(f"文本生成时发生错误: {e}")
        return jsonify({'error': f'服务器内部错误: {e}'}), 500


if __name__ == '__main__':
    # 启动服务器，监听在 5001 端口
    app.run(host='0.0.0.0', port=5001)