import streamlit as st
import pandas as pd
import os
import datetime
import navigation # [수정] navigation 임포트

st.set_page_config(
    page_title="GOLDEN JEJU | 관광 쾌적도 캘린더",
    layout="wide",
    initial_sidebar_state="collapsed"
)
navigation.apply_theme()
# --- [수정] ---
# current_page를 새 파일 경로로 지정
navigation.show_header(current_page="pages/1_쾌적도캘린더.py") 
# --- ---

# --- (기존 app.py의 데이터 로드 함수들) ---
data_folder_name = '데이터'
data_path = data_folder_name
final_themes_file = os.path.join(data_path, 'golden_compass_final_themes.csv')

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['월_라벨'] = df['날짜'].dt.strftime('%Y년 %m월')
        df['월'] = df['날짜'].dt.month
        df['월_str'] = df['날짜'].dt.strftime('%m월')
        df['년'] = df['날짜'].dt.year

        labels_5 = ["매우\n쾌적", "쾌적", "보통", "혼잡", "매우\n혼잡"]

        if '관광 포화 지수' in df.columns:
            df['쾌적도 라벨'] = pd.qcut(df['관광 포화 지수'], 5, labels=labels_5, duplicates='drop')
        else:
            df['쾌적도 라벨'] = "N/A"
        if '웰니스 쾌적도' in df.columns:
            df['웰니스 라벨'] = pd.qcut(df['웰니스 쾌적도'], 5, labels=labels_5, duplicates='drop')
        else:
            df['웰니스 라벨'] = "N/A"
        if '골프 쾌적도' in df.columns:
            df['골프 라벨'] = pd.qcut(df['골프 쾌적도'], 5, labels=labels_5, duplicates='drop')
        else:
            df['골프 라벨'] = "N/A"
        return df.sort_values(by='날짜')
    except Exception as e:
        return pd.DataFrame()

# --- (기존 app.py의 캘린더 그리기 함수) ---
def draw_monthly_cards(df, year, label_col):
    st.markdown(f"#### {year}년")
    
    status_map = {
        "매우\n쾌적": "🥰", 
        "쾌적": "😊",
        "보통": "😐",
        "혼잡": "😟",
        "매우\n혼잡": "🥵", 
        "N/A": "❓"
    }

    df_year = df[df['년'] == year]
    cols = st.columns(12)
    
    for month in range(1, 13):
        with cols[month-1]:
            month_data = df_year[df_year['월'] == month]
            
            if not month_data.empty:
                label = month_data[label_col].iloc[0]
                icon = status_map.get(label, "❓")
                css_class = f"status-{label.replace(chr(10), '')}" 
            else:
                label = "데이터 없음"
                icon = "➖"
                css_class = "status-데이터-없음"

            st.markdown(f"""
            <div class="month-card {css_class}">
                <h5>{month}월</h5>
                <div class="icon">{icon}</div>
                <p class="label">{label}</p>
            </div>
            """, unsafe_allow_html=True)
# --- ---

def calendar_page():
    
    df_full = load_data(final_themes_file)

    if df_full.empty:
        st.warning("데이터 파일을 찾을 수 없습니다. '데이터' 폴더를 확인해주세요.")
        return
        
    df_future = df_full[df_full['날짜'] >= datetime.datetime(2025, 1, 1)].copy()
    df_past = df_full[df_full['날짜'] < datetime.datetime(2025, 1, 1)].copy()

    # --- (기존 app.py의 메인 영역 내용) ---
    st.subheader("📅 관광 쾌적도 캘린더 (예측)")
    st.caption("아이콘과 색상으로 월별 쾌적도를 한눈에 확인하세요.")

    with st.container(border=True):
        st.markdown("##### 💡 쾌적도 지수란?")
        st.markdown(
            """
            쾌적도 지수는 과거의 **'관광 포화 지수'** 데이터를 통계적으로 분석하여 5개의 동일한 비율(각 20%)로 나눈 값(5분위수)입니다. \n
            이를 통해 사용자는 해당 월의 관광 쾌적도가 과거 데이터 대비 상위 몇 % 수준인지 직관적으로 파악할 수 있습니다.
            """
        )
        st.markdown(
            """
            <div class="legend-container">
                <div class="legend-item"><div class="legend-color-box legend-blue"></div><b>매우쾌적</b> (상위 0-20%)</div>
                <div class="legend-item"><div class="legend-color-box legend-green"></div><b>쾌적</b> (상위 20-40%)</div>
                <div class="legend-item"><div class="legend-color-box legend-yellow"></div><b>보통</b> (상위 40-60%)</div>
                <div class="legend-item"><div class="legend-color-box legend-orange"></div><b>혼잡</b> (상위 60-80%)</div>
                <div class="legend-item"><div class="legend-color-box legend-red"></div><b>매우혼잡</b> (상위 80-100%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    tab1, tab2, tab3 = st.tabs([
        "📈 전체 쾌적도 (기본)",
        "🧘 웰니스 쾌적도",
        "⛳ 골프 쾌적도"
    ])
    with tab1:
        draw_monthly_cards(df_future, 2025, '쾌적도 라벨')
        draw_monthly_cards(df_future, 2026, '쾌적도 라벨')
    with tab2:
        st.info("💡 **웰니스 쾌적도란?** \n\n과거 데이터(방문자 수, 검색량 등)를 기반으로 명상, 스파, 힐링, 산책 등 '웰니스' 활동에 얼마나 쾌적한지를 나타내는 예측 지수입니다.")
        draw_monthly_cards(df_future, 2025, '웰니스 라벨')
        draw_monthly_cards(df_future, 2026, '웰니스 라벨')
    with tab3:
        st.info("💡 **골프 쾌적도란?** \n\n과거 데이터(골프장 방문자 수, 날씨, 이용 요금 등)를 기반으로 골프 활동에 얼마나 쾌적한지를 나타내는 예측 지수입니다.")
        draw_monthly_cards(df_future, 2025, '골프 라벨')
        draw_monthly_cards(df_future, 2026, '골프 라벨')

    st.markdown("---")
    
    with st.expander("지난 쾌적도 캘린더 보기 (2023-2024 과거 데이터)"):
        st.info("과거 캘린더 비교용 데이터는 '전체 쾌적도' 지수만 제공합니다.")
        st.subheader("과거 쾌적도 캘린더 (비교용)")
        tab_past1, tab_past2 = st.tabs(["2023년", "2024년"])
        with tab_past1:
            draw_monthly_cards(df_past, 2023, '쾌적도 라벨')
        with tab_past2:
            draw_monthly_cards(df_past, 2024, '쾌적도 라벨')
    # --- ---

if __name__ == "__main__":
    calendar_page() # 함수 이름 변경