import os
import openai

# API 키 설정
''' os.environ["OPENAI_API_KEY"] = ""
openai.api_key = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = "API key is expired." ''' 

# 채팅 완료 요청
chat_completion = openai.ChatCompletion.create(
    model="gpt-4",  # 올바른 모델 이름 사용
    messages=[
        {
            "role": "system",
            "content": "입력받은 문장을 일본어로 번역해줘",
        },
        {
            "role": "user",
            "content": "너에 대해서 설명해줘",
        }
    ]
)

# 결과 출력
result = chat_completion['choices'][0]['message']['content']
print(result)