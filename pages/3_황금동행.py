import streamlit as st
import pandas as pd
import os
import datetime
import navigation
import urllib.parse

# --- [수정됨] (항목 2) ---
st.set_page_config(page_title="GOLDEN JEJU | 황금 단체투어", layout="wide", initial_sidebar_state="collapsed") # 이름 수정
navigation.apply_theme()
navigation.show_header(current_page="pages/3_황금동행.py")
# --- ---

data_folder_name = '데이터'
data_path = data_folder_name
final_themes_file = os.path.join(data_path, 'golden_compass_final_themes.csv')

image1_path = "image1.jpg"
image2_path = "image2.jpg"

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        df['날짜'] = pd.to_datetime(df['날짜'])
        return df.set_index('날짜')
    except Exception as e:
        return pd.DataFrame()

def show_tour_page():
    # --- [수정됨] (항목 2) ---
    st.title("🚌 황금 단체투어 (소셜 투어)") # 이름 수정
    st.caption("개인도 신청 가능한 단체 투어! 데이터로 검증된 쾌적한 날, 비슷한 연령대의 새로운 사람들과 함께 떠나보세요.")
    # --- ---
    
    df_themes = load_data(final_themes_file)
    if df_themes.empty:
        st.warning("테마 데이터 파일을 찾을 수 없습니다.")
        return

    try:
        data_march = df_themes.loc[datetime.datetime(2026, 3, 1)]
        wellness_score = data_march['웰니스 쾌적도']
        bus_rate = data_march['전세버스 가동률']
    except KeyError:
        wellness_score = 0.35 
        bus_rate = 22.0
    try:
        data_april = df_themes.loc[datetime.datetime(2026, 4, 1)]
        golf_score = data_april['골프 쾌적도']
    except KeyError:
        golf_score = -0.15

    st.subheader("🚌 현재 모집중인 GOLDEN J 소셜 투어")
    
    tab1, tab2 = st.tabs(["[3월] 🧘 힐링 & 명상 투어 (모집중)", "[4월] ⛳ '오름' 트레킹 & 골프 투어 (모집중)"])
    with tab1:
        st.markdown("#### [데모 상품] 3월의 힐링 & 명상 투어")
        st.info(f"**데이터 근거:** 3월 웰니스 쾌적도: {wellness_score:.3f} (매우 한산), 전세버스 가동률 {bus_rate:.1f}% (유휴 자원)")
        
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists(image1_path):
                st.image(image1_path, caption="3월의 힐링 투어", width=300)
            else:
                st.warning(f"'{image1_path}' 파일을 찾을 수 없습니다. (경로: C:\공모전\image1.jpg)")
                st.image("https://placehold.co/300x200/F26B21/FFFFFF?text=힐링+투어", caption="힐링 투어 예시")
        with col2:
            st.markdown("- **일시:** 2026년 3월 18일 (수) 09:00 - 17:00\n"
                        "- **테마:** 웰니스, 힐링, 명상 (비슷한 연령대 매칭)\n"
                        "- **대상:** 'GOLDEN J' 50-70대 회원 (개인 신청 환영)\n"
                        "- **교통:** '황금 단체투어' 전세버스 (편안한 좌석)\n" # 이름 수정
                        "- **가격:** 1인 89,000원 (중식/다과 포함)")
            
            with st.expander("상세 일정 (클릭하여 위치 확인)"):
                st.write("- 09:00 집결 (제주공항 / 제주시청)")
                st.write("- 10:30 사려니숲길 웰니스 산책")
                st.link_button("📍 '사려니숲길' 위치 보기", f"https://map.naver.com/v5/search/{urllib.parse.quote('사려니숲길')}")
                st.write("- 12:30 로컬 채식 뷔페 (데모: 채식마루)")
                st.link_button("📍 '제주 채식마루' 위치 보기", f"https://map.naver.com/v5/search/{urllib.parse.quote('제주 채식마루')}")
                st.write("- 14:00 명상 센터 방문 (데모: 제주 명상 수련원)")
                st.link_button("📍 '제주 명상 수련원' 위치 보기", f"https://map.naver.com/v5/search/{urllib.parse.quote('제주 명상 수련원')}")
                st.write("- 17:00 투어 종료")

        with st.form("tour_form_1"):
            st.markdown("---")
            st.markdown("#### [3월 힐링 투어] 신청하기 (데모)")
            participants = st.selectbox("신청 인원", [1, 2, 3, 4], key="p1")
            st.markdown("**참가자 정보 입력** (연령대 매칭에 활용됩니다)")
            for i in range(participants):
                c1, c2 = st.columns(2)
                with c1: st.text_input(f"참가자 {i+1} 성함", key=f"n1_{i}")
                with c2: st.date_input(f"참가자 {i+1} 생년월일", value=datetime.date(1960, 1, 1), key=f"b1_{i}")
            if st.form_submit_button("신청하기 (데모)", type="primary"):
                st.success(f"총 {participants}명 투어 신청이 완료되었습니다! (데모)")
                st.balloons()
    with tab2:
        st.markdown("#### [데모 상품] 4월의 '오름' 트레킹 & 골프 투어")
        st.info(f"**데이터 근거:** 4월 골프 쾌적도: {golf_score:.3f} (가성비 최고), '오름' 키워드 검색량 증가")
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists(image2_path):
                st.image(image2_path, caption="4월의 오름 & 골프 투어", width=300)
            else:
                st.warning(f"'{image2_path}' 파일을 찾을 수 없습니다. (경로: C:\공모전\image2.jpg)")
                st.image("https://placehold.co/300x200/006400/FFFFFF?text=골프+투어", caption="골프 투어 예시")
        with col2:
            st.markdown("- **일시:** 2026년 4월 15일 (수) 09:00 - 17:00\n"
                        "- **테마:** 골프, 레저, 오름 (연령대 매칭)\n"
                        "- **대상:** 'GOLDEN J' 50-70대 회원 (개인 신청 환영)\n"
                        "- **교통:** '황금 단체투어' 전세버스\n" # 이름 수정
                        "- **가격:** 1인 159,000원 (중식/라운딩 비용 별도)")
            
            with st.expander("상세 일정 (클릭하여 위치 확인)"):
                st.write("- 09:00 집결 (제주공항 / 서귀포)")
                st.write("- 10:00 따라비오름 트레킹")
                st.link_button("📍 '따라비오름' 위치 보기", f"https://map.naver.com/v5/search/{urllib.parse.quote('따라비오름')}")
                st.write("- 12:00 인근 맛집 (데모: 가시식당)")
                st.link_button("📍 '가시식당' 위치 보기", f"https://map.naver.com/v5/search/{urllib.parse.quote('가시식당')}")
                st.write("- 14:00 인근 골프장 9홀 라운딩 (데모: 더클래식 골프앤리조트)")
                st.link_button("📍 '더클래식 골프앤리조트' 위치 보기", f"https://map.naver.com/v5/search/{urllib.parse.quote('더클래식 골프앤리조트')}")
                st.write("- 17:00 투어 종료")

        with st.form("tour_form_2"):
            st.markdown("---")
            st.markdown("#### [4월 골프 투어] 신청하기 (데모)")
            participants = st.selectbox("신청 인원", [1, 2, 3, 4], key="p2")
            st.markdown("**참가자 정보 입력** (연령대 매칭에 활용됩니다)")
            for i in range(participants):
                c1, c2 = st.columns(2)
                with c1: st.text_input(f"참가자 {i+1} 성함", key=f"n2_{i}")
                with c2: st.date_input(f"참가자 {i+1} 생년월일", value=datetime.date(1960, 1, 1), key=f"b2_{i}")
            if st.form_submit_button("신청하기 (데모)", type="primary"):
                st.success(f"총 {participants}명 투어 신청이 완료되었습니다! (데모)")
                st.balloons()

if __name__ == "__main__":
    show_tour_page()