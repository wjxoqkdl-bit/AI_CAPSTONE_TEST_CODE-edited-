# modules/authentication.py

import streamlit as st

# --- 사용자 정보 ---
# 회의에서 논의된 대로(09:43), 간단하게 두 명의 사용자 정보를 하드코딩합니다.
# 실제 프로젝트에서는 데이터베이스를 사용하는 것이 안전합니다.
VALID_CREDENTIALS = {
    "user1": "pass1",
    "user2": "pass2"
}


# --- 로그인 UI 및 인증 처리 함수 ---
def login_flow():
    """
    로그인 화면을 표시하고 사용자의 입력을 받아 인증을 처리합니다.
    인증에 성공하면 st.session_state에 로그인 상태를 기록합니다.
    """
    st.header("로그인")

    # 사용자로부터 아이디와 비밀번호를 입력받는 필드를 생성합니다.
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    # '로그인' 버튼을 생성합니다. 이 버튼이 클릭되면 아래의 코드가 실행됩니다.
    if st.button("로그인"):
        # 입력된 아이디와 비밀번호가 미리 정의해둔 정보와 일치하는지 확인합니다.
        if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
            # 인증 성공 시, Streamlit의 세션 상태(session_state)에 로그인 정보를 저장합니다.
            # st.session_state는 사용자가 앱과 상호작용하는 동안 데이터를 유지해주는 특별한 공간입니다.
            st.session_state['logged_in'] = True
            st.session_state['username'] = username

            # 로그인 성공 메시지를 화면에 잠시 보여줍니다.
            st.success(f"{username}님, 환영합니다!")

            # st.rerun()을 호출하여 스크립트를 즉시 재실행합니다.
            # 이렇게 하면 로그인 상태가 True로 바뀌었으므로 메인 화면으로 전환됩니다.
            st.rerun()
        else:
            # 인증 실패 시, 에러 메시지를 보여줍니다.
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")


# --- 로그아웃 처리 함수 ---
def logout_flow():
    """
    사이드바에 로그아웃 버튼을 표시하고, 클릭 시 세션 상태를 초기화합니다.
    """
    st.sidebar.write(f"로그인된 사용자: **{st.session_state['username']}**")
    if st.sidebar.button("로그아웃"):
        # 로그아웃 시, 세션 상태의 모든 관련 정보를 초기화합니다.
        st.session_state['logged_in'] = False
        st.session_state['username'] = None

        # 검색 기록도 초기화해주는 것이 좋습니다. (향후 추가될 기능)
        if 'history' in st.session_state:
            st.session_state['history'] = []

        # 페이지를 새로고침하여 로그인 화면으로 돌아갑니다.
        st.rerun()