import os
import openai

# API 키 설정 
# os.environ["OPENAI_API_KEY"] = ""
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = "API key is expired." 

# 이미지 생성 요청
response = openai.Image.create(
    model="dall-e-3",
    prompt="대나무 숲의 호랑이",
    n=1,
    size="1024x1024"
)

# 생성된 이미지 URL 가져오기
image_url = response['data'][0]['url']
print(image_url)
