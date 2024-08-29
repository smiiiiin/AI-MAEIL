import os
import streamlit as st
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import openai
from concurrent.futures import ThreadPoolExecutor

# OpenAI API Key setting
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Gmail API Setting 
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
creds = None

# Gmail API Authentification
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

service = build('gmail', 'v1', credentials=creds)

# Streamlit 페이지 구성
st.title('매일비서')

# 사용자 입력 받기
user_query = st.text_input("검색할 이메일의 키워드를 입력하세요:")

def get_email_body(msg):
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
    return ""

def summarize_text(text):
    # Divide the text within the maximum token length and summarizing
    max_tokens = 1500
    chunks = [text[i:i+max_tokens] for i in range(0, len(text), max_tokens)]
    summaries = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(openai.ChatCompletion.create,
                                   model="gpt-3.5-turbo",
                                   messages=[
                                       {"role": "system", "content": "You are a helpful assistant."},
                                       {"role": "user", "content": f"다음 텍스트의 주요 내용을 요약해 주세요: {chunk}"}
                                   ]) for chunk in chunks]
        for future in futures:
            response = future.result()
            summaries.append(response['choices'][0]['message']['content'].strip())
    return " ".join(summaries)

if st.button("이메일 검색 및 요약"):
    if user_query:
        try:
            # Search emails using the Gmail API
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
                        futures.append(executor.submit(summarize_text, email_body))
                    for future in futures:
                        summaries.append(future.result())

                # Combine individual summaries to create a final summary
                final_summary = summarize_text(" ".join(summaries))

                # output result
                st.subheader("요약 결과")
                st.write(final_summary)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.error("키워드를 입력해주세요.")
