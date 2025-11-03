import streamlit as st
import pandas as pd
import os
import datetime
import numpy as np
import navigation

st.set_page_config(
    page_title="GOLDEN JEJU | 메인",
    layout="wide",
    initial_sidebar_state="collapsed"
)
navigation.apply_theme()

# --- [수정됨] navigation.show_header() 호출 대신, 모든 것을 직접 구성 ---

# 1. 메인 로고 및 설명 (navigation.py의 CSS 클래스 사용)
st.markdown(
    """
    <div class="main-page-header">
        <div class="logo-text"><a href="/" target="_self">🍊 GOLDEN JEJU</a></div>
        <p class="logo-description">액티브 시니어를 위한 맞춤형 제주 여행 플랫폼입니다.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. 네비게이션 버튼 바 (navigation.py의 로직을 직접 복사)
st.markdown('<div class="golden-header-v12-final">', unsafe_allow_html=True) # 배경색을 위해 클래스 사용

pages = {
    "pages/1_쾌적도캘린더.py": {"label": "📅 관광 쾌적도 캘린더", "path": "pages/1_쾌적도캘린더.py"},
    "pages/2_숙소필터.py": {"label": "🏨 맞춤 숙소 찾기", "path": "pages/2_숙소필터.py"},
    "pages/3_황금동행.py": {"label": "🚌 황금 단체투어", "path": "pages/3_황금동행.py"}, 
    "pages/4_황금원패스.py": {"label": "🎫 황금 올인원 패키지", "path": "pages/4_황금원패스.py"}, 
    "pages/5_제주이야기.py": {"label": "🧘 제주이야기", "path": "pages/5_제주이야기.py"},
    "pages/6_미식게시판.py": {"label": "🍲 맛집 커뮤니티", "path": "pages/6_미식게시판.py"},
    "pages/7_나만의_여행일정.py": {"label": "✍️ 나만의 여행 일정", "path": "pages/7_나만의_여행일정.py"},
    "pages/8_스마트추천맵.py": {"label": "🗺️ 스마트 추천맵", "path": "pages/8_스마트추천맵.py"}, 
    "pages/9_스마트맛집검색.py": {"label": "🔎 스마트 맛집", "path": "pages/9_스마트맛집검색.py"},
    "pages/10_지역별추천.py": {"label": "📍 지역별 추천", "path": "pages/10_지역별추천.py"},
}

def render_button(page_key: str):
    page_info = pages[page_key]
    button_label = page_info["label"]
    button_path = page_info["path"]
    
    button_type = "primary" 
    
    if st.button(button_label, type=button_type, use_container_width=True, key=page_key):
        st.switch_page(button_path)

link_cols_1 = st.columns(5)
with link_cols_1[0]:
    render_button("pages/1_쾌적도캘린더")
with link_cols_1[1]:
    render_button("pages/2_숙소필터")
with link_cols_1[2]:
    render_button("pages/3_황금동행")
with link_cols_1[3]:
    render_button("pages/4_황금원패스")
with link_cols_1[4]:
    render_button("pages/5_제주이야기")


link_cols_2 = st.columns(5)
with link_cols_2[0]:
    render_button("pages/6_미식게시판")
with link_cols_2[1]:
    render_button("pages/7_나만의_여행일정")
with link_cols_2[2]:
    render_button("pages/8_스마트추천맵")
with link_cols_2[3]:
    render_button("pages/9_스마트맛집검색")
with link_cols_2[4]:
    render_button("pages/10_지역별추천")

st.markdown('</div>', unsafe_allow_html=True)
# --- [수정 완료] ---


# --- (데이터 로드 함수들) ---
data_folder_name = '데이터'
data_path = data_folder_name
final_themes_file = os.path.join(data_path, 'golden_compass_final_themes.csv')
foodie_file = os.path.join(data_path, 'golden_compass_foodie_ranking.csv')

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        if '날짜' in df.columns:
            df['날짜'] = pd.to_datetime(df['날짜'])
            df['월_라벨'] = df['날짜'].dt.strftime('%Y년 %m월')
            df['월'] = df['날짜'].dt.month
            labels_5 = ["매우\n쾌적", "쾌적", "보통", "혼잡", "매우\n혼잡"]
            if '관광 포화 지수' in df.columns:
                df['쾌적도 라벨'] = pd.qcut(df['관광 포화 지수'], 5, labels=labels_5, duplicates='drop')
            else:
                df['쾌적도 라벨'] = "N/A"
            if '웰니스 쾌적도' in df.columns:
                df['웰니스 쾌적도'] = df['웰니스 쾌적도'].astype(float)
            if '골프 쾌적도' in df.columns:
                df['골프 쾌적도'] = df['골프 쾌적도'].astype(float)
            if '전세버스 가동률' in df.columns:
                df['전세버스 가동률'] = df['전세버스 가동률'].astype(float)
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()

@st.cache_data
def load_foodie_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"미식 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()
# --- ---


def main_dashboard():
    
    df_full = load_data(final_themes_file)
    df_foodie = load_data(foodie_file)

    if df_full.empty:
        st.error("데이터 파일을 찾을 수 없습니다. '데이터' 폴더를 확인해주세요.")
        return
        
    st.markdown("---")

    # --- "지금, 제주는?" 섹션 ---
    try:
        today = datetime.datetime.today()
        current_date_for_display = datetime.datetime(2025, 11, 1) 
        current_month_label = current_date_for_display.strftime('%Y년 %m월')
        
        current_data = df_full[df_full['월_라벨'] == current_month_label].iloc[0]

        st.subheader(f"🍊 지금, 제주는? ({current_month_label} 기준)")
        
        cols = st.columns(3)
        with cols[0]:
            comfort_label = current_data['쾌적도 라벨']
            st.metric("이달의 쾌적도", f"👍 {comfort_label.replace(chr(10), '')}")
        with cols[1]:
            best_theme = "🧘 웰니스" if current_data['웰니스 쾌적도'] <= current_data['골프 쾌적도'] else "⛳ 골프"
            st.metric("추천 테마", best_theme)
        with cols[2]:
            best_service = "🚌 황금 단체투어" if current_data['전세버스 가동률'] <= 30.0 else "🎫 황금 올인원 패키지"
            st.metric("추천 서비스", best_service)
        
        if best_service == "🚌 황금 단체투어":
            if st.button("➡️ 이달의 추천 '황금 단체투어' 바로가기", type="primary", use_container_width=True):
                st.switch_page("pages/3_황금동행.py")
        else: 
            if st.button("➡️ 이달의 추천 '황금 올인원 패키지' 바로가기", type="primary", use_container_width=True):
                st.switch_page("pages/4_황금원패스.py")
    
    except (IndexError, KeyError) as e:
        st.info(f"현재 월에 대한 추천 데이터를 불러올 수 없습니다. (데이터는 2025년 11월 기준 고정)")

    
    # --- "핵심 서비스" 섹션 (st.container(border=True) 사용) ---
    st.markdown("---")
    st.subheader("🌟 GOLDEN JEJU 주요 서비스")
    
    cols = st.columns(3)
    with cols[0]:
        with st.container(border=True):
            st.markdown("##### 📅 관광 쾌적도 캘린더")
            st.caption("월별 쾌적도 예측 정보를 한눈에 확인하고, 여행 계획에 활용하세요.")
            if st.button("캘린더 보러가기", use_container_width=True, key="main_cal"):
                st.switch_page("pages/1_쾌적도캘린더.py")
    with cols[1]:
        with st.container(border=True):
            st.markdown("##### 🏨 맞춤 숙소 찾기")
            st.caption("선호하는 조건과 쾌적도를 고려한 최적의 숙소를 추천받으세요.")
            if st.button("숙소 찾기", use_container_width=True, key="main_accom"):
                st.switch_page("pages/2_숙소필터.py")
    with cols[2]:
        with st.container(border=True):
            st.markdown("##### 🚌 황금 단체투어")
            st.caption("혼자여도 괜찮아요! 또래 시니어와 함께 떠나는 즐거운 소셜 투어.")
            if st.button("단체 투어 신청", use_container_width=True, key="main_tour"):
                st.switch_page("pages/3_황금동행.py")
    
    cols2 = st.columns(3)
    with cols2[0]:
        with st.container(border=True):
            st.markdown("##### 🎫 황금 올인원 패키지")
            st.caption("숙소+활동+식사까지! 데이터가 추천하는 알찬 올인원 패키지.")
            if st.button("패키지 예약하기", use_container_width=True, key="main_pass"):
                st.switch_page("pages/4_황금원패스.py")
    with cols2[1]:
        with st.container(border=True):
            st.markdown("##### ✍️ 나만의 여행 일정")
            st.caption("찜한 장소로 나만의 코스를 만들거나, 자동으로 코스를 생성해보세요.")
            if st.button("일정 만들기", use_container_width=True, key="main_plan"):
                st.switch_page("pages/7_나만의_여행일정.py")
    with cols2[2]:
        with st.container(border=True):
            st.markdown("##### 📍 지역별 추천")
            st.caption("제주시, 애월, 서귀포 등 주요 지역의 추천 장소를 바로 확인하세요.")
            if st.button("지역별 추천 보기", use_container_width=True, key="main_region"):
                st.switch_page("pages/10_지역별추천.py")


    # --- "월별 상세 지표" 섹션 ---
    st.markdown("---")
    st.subheader("📊 월별 상세 지표 및 추천 서비스")
    st.caption("과거 또는 미래의 '황금시기' 월을 선택하여 상세 지표와 추천 서비스를 확인하세요.")
    
    cols_selector, cols_detail = st.columns([1, 2]) 
    
    with cols_selector:
        month_options = df_full['월_라벨'].unique()[::-1]
        selected_month_label = st.selectbox("분석할 월을 선택하세요:", month_options, label_visibility="collapsed")

        selected_data = df_full[df_full['월_라벨'] == selected_month_label].iloc[0]
        selected_month_int = selected_data['월']

        st.markdown(f"#### **{selected_month_label}** 상세 정보")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("🚗 렌터카 가동률", f"{selected_data['렌터카 가동률']:.1f} %")
            st.caption("가동률이 낮을수록 렌트가 저렴할 수 있습니다.")
        with c2:
            st.metric("🚌 전세버스 가동률", f"{selected_data['전세버스 가동률']:.1f} %")
            st.caption("가동률이 낮을수록 단체 관광객이 적습니다.")
            
    with cols_detail:
        st.markdown(f"**🍲 {selected_month_int}월 시니어 미식 Top 5**")
        if df_foodie.empty:
            st.info("미식 데이터가 없습니다.")
        else:
            top5_foodie = df_foodie[df_foodie['월'] == selected_month_int].sort_values(by='점수', ascending=False).head(5)
            if top5_foodie.empty:
                st.info(f"{selected_month_int}월은 집계된 시니어 추천 미식 키워드가 없습니다.")
            else:
                top5_foodie['랭킹'] = np.arange(1, len(top5_foodie) + 1)
                st.dataframe(top5_foodie[['랭킹', '키워드', '점수']], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main_dashboard()