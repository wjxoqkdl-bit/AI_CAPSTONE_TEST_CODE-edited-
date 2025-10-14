# app.py

import streamlit as st
from modules.authentication import login_flow, logout_flow
from modules.api_handler import get_ai_response

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 분석 서비스",
    page_icon="✨",  # 아이콘 변경
    layout="wide"
)

# --- 세션 상태(Session State) 초기화 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'history' not in st.session_state:
    st.session_state['history'] = []


# --- 메인 애플리케이션 로직 ---
def main():
    """
    애플리케이션의 메인 로직을 실행합니다.
    로그인 상태에 따라 다른 화면을 보여줍니다.
    """
    if not st.session_state['logged_in']:
        login_flow()
    else:
        # --- 사이드바 구성 ---
        with st.sidebar:
            logout_flow()
            st.markdown("---")
            st.header("📜 분석 기록")

            # [UX 개선] 기록이 없을 때의 안내 문구를 더 친절하게 변경
            if not st.session_state.history:
                st.info("아직 분석 기록이 없네요. 첫 번째 분석을 시작해보세요!")
            else:
                for i, entry in enumerate(st.session_state.history):
                    with st.expander(f"#{len(st.session_state.history) - i}: {entry['prompt'][:30]}..."):
                        st.markdown("##### 📝 핵심 요약")
                        st.write(entry['result']['data']['summary'])
                        st.markdown("##### 🔑 관련 키워드")
                        st.write(", ".join(entry['result']['data']['keywords']))

        # --- 메인 화면 구성 ---
        st.title("✨ AI 기반 분석 서비스")
        st.markdown("안녕하세요! 분석하고 싶은 내용을 아래에 입력하고 AI의 답변을 확인해보세요.")
        st.markdown("---")

        # [레이아웃 개선] st.columns를 사용해 입력창과 버튼을 나란히 배치
        col1, col2 = st.columns([1, 2])  # 4:1 비율로 공간 분할

        with col1:
            prompt = st.text_area(
                label="분석할 내용 입력",  # label을 더 간결하게 변경
                label_visibility="collapsed",  # label을 화면에서 숨김
                height=150,
                placeholder="예: 오늘 회의록을 요약하고 핵심 안건을 뽑아줘."
            )

        with col2:
            # [UX 개선] 버튼을 텍스트 입력창 높이에 맞추고, 문구를 더 자연스럽게 변경
            st.write("")  # 수직 정렬을 위한 빈 공간
            st.write("")
            submit_button = st.button(
                label="🚀 분석 요청하기",
                use_container_width=True
            )

        if submit_button:
            if prompt:
                # [UX 개선] spinner 메시지를 더 구체적이고 친근하게 변경
                with st.spinner('AI가 열심히 생각하고 있어요... 🧐'):
                    response_data = get_ai_response(prompt)

                if response_data and response_data.get("status") == "success":
                    new_entry = {"prompt": prompt, "result": response_data}
                    st.session_state.history.insert(0, new_entry)
                    # 분석 완료 후 페이지를 새로고침하여 입력창을 비우고 결과를 바로 보여줌
                    st.rerun()
                else:
                    # [UX 개선] 오류 메시지를 더 이해하기 쉽게 변경
                    st.error("AI 서버와 연결하는 데 실패했습니다. 잠시 후 다시 시도해주세요.")
            else:
                st.warning("분석할 내용을 입력해주세요.")

        # --- 최신 결과 표시 ---
        # st.rerun() 이후, 가장 최신 기록을 가져와 메인 화면에 표시
        if st.session_state.history:
            latest_result = st.session_state.history[0]['result']
            st.subheader("✨ AI 분석 결과")
            with st.container(border=True):
                data = latest_result.get("data", {})
                st.markdown("#### 📝 핵심 요약")
                st.write(data.get('summary', '요약 정보가 없습니다.'))
                st.markdown("---")
                st.markdown("#### 📄 상세 내용")
                with st.expander("자세히 보기..."):
                    st.markdown(data.get('details', '상세 내용이 없습니다.'))
                st.markdown("---")
                st.markdown("#### 🔑 관련 키워드")
                keywords = data.get('keywords', )
                if keywords:
                    # 키워드를 버튼 대신 텍스트로 표시하여 UI를 더 단순하게 만듦
                    st.write(" &nbsp;·&nbsp; ".join(f"`{kw}`" for kw in keywords))
                else:
                    st.caption("추출된 키워드가 없습니다.")


# --- 스크립트 실행 ---
if __name__ == "__main__":
    main()