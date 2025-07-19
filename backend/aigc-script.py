from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os

# Google AI Studio API 配置
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDelxvGq533ceRHS71I8JHx0dfqk6WU12E')

# 创建客户端
client = genai.Client(api_key=API_KEY)

contents = ('Hi, can you create a 3d rendered image of a pig '
            'with wings and a top hat flying over a happy '
            'futuristic scifi city with lots of greenery?')

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
          response_modalities=['TEXT', 'IMAGE']
        )
    )

    for part in response.candidates[0].content.parts:
      if part.text is not None:
        print(part.text)
      elif part.inline_data is not None:
        image = Image.open(BytesIO((part.inline_data.data)))
        image.save('gemini-native-image.png')
        print("图像已保存为: gemini-native-image.png")
        image.show()
        
except Exception as e:
    print(f"错误: {e}")