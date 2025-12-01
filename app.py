import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import base64
 
# 1. 환경 변수 로드 (.env 파일이 같은 폴더에 있어야 함)
load_dotenv()
 
st.markdown("<h1>청소년 상담 챗봇 <span style='color: #008080;'>Teeni</span></h1>", unsafe_allow_html=True)

# ===== 사이드바 추가 =====
with st.sidebar:
    st.header("메뉴")
    
    # 대화 초기화 버튼
    if st.button("새 대화 시작"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # 설정 옵션
    st.subheader("설정")
    temperature = st.slider("응답 창의성", 0.0, 1.0, 0.5, 0.1)
    max_tokens = st.number_input("최대 응답 길이", 100, 2000, 700, 100)
    
    st.divider()
    
    # 정보 표시
    st.subheader("ℹ️ 안내")
    st.info("청소년 여러분의 고민을 함께 나눠요!")
    
    # 대화 횟수 표시
    message_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.metric("대화 횟수", message_count)

# ===== 기존 코드 =====
 
# 2. Azure OpenAI 클라이언트 설정
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT")
)
 
# 3. 대화기록(Session State) 초기화
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
 
    # (2) AI 응답 생성 (사이드바 설정값 적용)
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="8ai051-gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=temperature,  # 사이드바 설정값 사용
            max_tokens=max_tokens     # 사이드바 설정값 사용
        )
        assistant_reply = response.choices[0].message.content
        st.markdown(assistant_reply)
 
    # (3) AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})