import os
import streamlit as st
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import openai
from concurrent.futures import ThreadPoolExecutor

# OpenAI API 키 설정
openai.api_key = st.secrets['API_KEY']

# Gmail API 설정
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_email_body(msg):
    try:
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if 'parts' in part:
                    for sub_part in part['parts']:
                        if sub_part['mimeType'] == 'text/plain':
                            return base64.urlsafe_b64decode(sub_part['body']['data']).decode('utf-8')
                        elif sub_part['mimeType'] == 'text/html':
                            return base64.urlsafe_b64decode(sub_part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            return base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
    except Exception as e:
        st.error(f"이메일 본문을 가져오는 중 오류 발생: {e}")
    return ""

def get_email_subject(msg):
    try:
        headers = msg['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                return header['value']
    except Exception as e:
        st.error(f"이메일 제목을 가져오는 중 오류 발생: {e}")
    return "제목 없음"

def summarize_text(text):
    max_chunk_size = 3000  # You can adjust the chunk size based on token limits
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    summaries = []
    
    for chunk in chunks:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"다음 텍스트를 한 줄로 요약해 주세요: {chunk}"}
            ]
        )
        summaries.append(response['choices'][0]['message']['content'].strip())
    
    final_summary = " ".join(summaries)
    return final_summary

# Streamlit 페이지 구성
st.title('매일비서')

# 사용자 입력 받기
user_query = st.text_input("검색할 이메일의 키워드를 입력하세요:")

if st.button("이메일 검색 및 요약"):
    if user_query:
        try:
            # Gmail API를 사용하여 이메일 검색
            service = authenticate_gmail()
            results = service.users().messages().list(userId='me', q=user_query).execute()
            messages = results.get('messages', [])

            if not messages:
                st.write("검색된 이메일이 없습니다.")
            else:
                summaries = []
                with ThreadPoolExecutor() as executor:
                    futures = []
                    for msg in messages:
                        msg = service.users().messages().get(userId='me', id=msg['id']).execute()
                        email_body = get_email_body(msg)
                        email_subject = get_email_subject(msg)
                        futures.append(executor.submit(summarize_text, email_body))
                        summaries.append((email_subject, futures[-1]))

                    for i, (subject, future) in enumerate(summaries):
                        summary = future.result()
                        st.write(f"### 이메일 {i + 1}: {subject}")
                        st.write(summary)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.error("키워드를 입력해주세요.")

