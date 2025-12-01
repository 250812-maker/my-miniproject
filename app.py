import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

import base64
 
# 1. 환경 변수 로드 (.env 파일이 같은 폴더에 있어야 함)
load_dotenv()
 
st.markdown("<h1>청소년 상담 챗봇 '<span style='color: #008080;'>Teeni</span>'</h1>", unsafe_allow_html=True)
 
# 2. Azure OpenAI 클라이언트 설정
# (실제 값은 .env 파일이나 여기에 직접 입력하세요)
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT")
)
 
# 3. 대화기록(Session State) 초기화 - 이게 없으면 새로고침 때마다 대화가 날아갑니다!
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# 4. 화면에 기존 대화 내용 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
# 5. 사용자 입력 받기
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # (1) 사용자 메시지 화면에 표시 & 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
 
    # (2) AI 응답 생성 (스트리밍 방식 아님, 단순 호출 예시)
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="8ai051-gpt-4o-mini", # 사용하시는 배포명(Deployment Name)으로 수정 필요!
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )
        assistant_reply = response.choices[0].message.content
        st.markdown(assistant_reply)
 
    # (3) AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# 완성

# mini project 벡터 검색 추가한 RAG 샘플코드

import os
import base64
from openai import AzureOpenAI

endpoint = os.getenv("ENDPOINT_URL", "https://8ai051-openai-t2.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "8ai051-gpt-4o-mini")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "EkO0eRjPTP4LEnpTFL34RbaZcILtwqcMjscI2CSBOZN8fD1nMAdOJQQJ99BKACHYHv6XJ3w3AAABACOGCROH")


search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://8ai051-aisearch2.search.windows.net")
search_key = os.getenv("SEARCH_KEY", "v1CWWb65IEG6QCMunFaSga57IG7vM0139EE49ij0XLAzSeDP53Bt")
search_index = os.getenv("SEARCH_INDEX_NAME", "rag-miniproject")


# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

# IMAGE_PATH = "YOUR_IMAGE_PATH"
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

# Prepare the chat prompt
chat_prompt = [
    {"role": "system", "content": "너는 청소년 정책 연구원이다."},
    {"role": "user", "content": "청소년들이 많이 하는 고민은?"},
]

# Include speech result if speech is enabled
messages = chat_prompt

# Generate the completion
completion = client.chat.completions.create(
    model=deployment,
    messages=messages,
    max_tokens=700,
    temperature=0.5,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False,
    extra_body={
      "data_sources": [{
          "type": "azure_search",
          "parameters": {
            "endpoint": f"{search_endpoint}",
            "index_name": "rag-miniproject",
            "semantic_configuration": "default",
            "query_type": "vector_semantic_hybrid",
            "fields_mapping": {},
            "in_scope": True,
            # "role_information": "너는 청소년 정책 연구원이다.",
            "filter": None,
            "strictness": 3,
            "top_n_documents": 5,
            "authentication": {
              "type": "api_key",
              "key": f"{search_key}"
            },
            "embedding_dependency": {
              "type": "deployment_name",
              "deployment_name": "text-embedding-ada-002"
            }
          }
        }]
    }
)

print(completion.choices[0].message.context['citations'])
    