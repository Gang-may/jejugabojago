import streamlit as st
import pandas as pd
import os
import datetime
import numpy as np
import navigation
import requests
import urllib.parse

# --- [수정됨] (항목 2) ---
st.set_page_config(page_title="GOLDEN JEJU | 황금 올인원 패키지", layout="wide", initial_sidebar_state="collapsed") # 이름 수정
navigation.apply_theme()
navigation.show_header(current_page="pages/4_황금원패스.py")
# --- ---

# --- 1. KAKAO API 설정 ---
KAKAO_API_KEY = "bf3481d1f6e13e299cc42b118357ace8"
GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

# --- 2. API 호출 함수 (주소 반환용) ---
@st.cache_data
def get_place_info_kakao(place_name):
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": f"제주 {place_name}"}
    try:
        response = requests.get(GEOCODE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['documents']:
            doc = data['documents'][0]
            address = doc.get('address_name', doc.get('road_address_name', '주소 정보 없음'))
            naver_link = f"https://map.naver.com/v5/search/{urllib.parse.quote(f'제주 {place_name}')}"
            return address, naver_link
    except Exception as e:
        print(f"Kakao Geocoding Error for {place_name}: {e}")
    
    # 실패 시 기본값 반환
    naver_link = f"https://map.naver.com/v5/search/{urllib.parse.quote(f'제주 {place_name}')}"
    return "주소 정보를 불러올 수 없습니다.", naver_link

# --- 3. 데이터 로드 ---
data_folder_name = '데이터'
data_path = data_folder_name
final_themes_file = os.path.join(data_path, 'golden_compass_final_themes.csv')
accom_file = os.path.join(data_path, 'golden_compass_accommodation_clean.csv')
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
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 4. UI ---
def show_pass_page():
    # --- [수정됨] (항목 2) ---
    st.title("🎫 황금 올인원 패키지 (시그니처 패키지)") # 이름 수정
    st.caption("모든 데이터를 종합하여, 'GOLDEN JEJU'가 제안하는 최적의 큐레이션 패키지입니다.")
    # --- ---
    
    df_themes = load_data(final_themes_file)
    df_accom = load_data(accom_file)
    df_foodie = load_data(foodie_file)
    
    if df_themes.empty or df_accom.empty or df_foodie.empty:
        st.warning("데이터 로드 중 오류가 발생했습니다. '데이터' 폴더를 확인하세요.")
        return

    if 'booking_step' not in st.session_state:
        st.session_state.booking_step = "details"

    def go_to_payment(): st.session_state.booking_step = "payment"
    def go_to_complete(): st.session_state.booking_step = "complete"
    def reset_flow():
        st.session_state.booking_step = "details"
        for key in ['user_name', 'user_phone', 'payment_method', 'booking_type']:
            if key in st.session_state: del st.session_state[key]

    if st.session_state.booking_step == "details":
        st.markdown("---")
        st.markdown("#### [1] 패키지 여행 시작일 선택")
        st.caption("오늘 이후 날짜만 선택 가능합니다. 날짜를 선택하면 해당 '월'의 데이터로 패키지가 자동 구성됩니다.")
        
        today = datetime.date.today()
        selected_date = st.date_input("시작일을 선택하세요 (달력):", 
                                      value=today, 
                                      min_value=today, 
                                      max_value=datetime.date(2026, 12, 31), 
                                      label_visibility="collapsed")
        
        selected_month = selected_date.month
        selected_month_label = selected_date.strftime('%Y년 %m월')
        
        try:
            selected_data = df_themes[df_themes['월_라벨'] == selected_month_label].iloc[0]
        except (IndexError, KeyError):
            st.error(f"{selected_month_label}의 데이터가 없습니다. CSV 파일을 확인하세요.")
            return

        top5_foodie = df_foodie[df_foodie['월'] == selected_month].sort_values(by='점수', ascending=False).head(5)
        foodie_theme_top1 = top5_foodie.iloc[0]['키워드'] if not top5_foodie.empty else "추천 미식"

        # --- 계절별 테마 로직 (숙소/활동 예시 추가) ---
        if selected_month in [3, 4, 5]:
            main_theme = "🧘 웰니스 & 힐링"
            sample_hotel = "제주신라호텔"
            theme_activity = "프리미엄 명상 클래스 (1회)"
            theme_food = f"이달의 미식 테마, '{foodie_theme_top1}' 저녁 식사 (1회)"
        elif selected_month in [6, 7, 8]:
            main_theme = "🌊 해양 & 레저"
            sample_hotel = "롯데호텔 제주"
            theme_activity = "프라이빗 요트 투어 (1회)"
            theme_food = f"이달의 미식 테마, '{foodie_theme_top1}' 저녁 식사 (1회)"
        elif selected_month in [9, 10, 11]:
            main_theme = "⛳ 골프 & 미식"
            sample_hotel = "핀크스 포도호텔"
            theme_activity = "A-Class 골프장 18홀 라운딩 (1회)"
            theme_food = f"이달의 미식 테마, '{foodie_theme_top1}' 저녁 식사 (1회)"
        else: # 12, 1, 2월
            main_theme = "❄️ 휴식 & 실내"
            sample_hotel = "그랜드 하얏트 제주"
            theme_activity = "5성급 호텔 스파 이용권 (1회)"
            theme_food = f"'{foodie_theme_top1}' 테마 호텔 디너 뷔페 (1회)"

        st.subheader(f"데이터가 추천하는 {selected_month_label}의 **'{main_theme}'** 패키지")
        st.markdown("---")

        st.markdown("#### [2] 패키지 구성 요소 (WHAT)")
        
        col_accom, col_activity = st.columns(2)

        with col_accom:
            st.markdown(f"##### 🏨 숙소 (예시: {sample_hotel})")
            
            # --- API로 주소 가져오기 ---
            address, naver_link = get_place_info_kakao(sample_hotel)
            st.caption(f"📍 {address}")
            st.link_button("🔗 숙소 위치/정보 보기", naver_link, use_container_width=True)
            # --- ---
            st.write("- 조식 뷔페 2인 포함")
            st.write("- LATE 체크인 (23:00) 보장")

        with col_activity:
            st.markdown(f"##### {main_theme} (테마)")
            st.write(f"- {theme_activity}")
            st.write(f"- {theme_food}")
            st.write("- 공항 ↔ 호텔 픽업/샌딩 서비스")
        
        st.markdown("---")
        st.markdown("#### [3] 패키지 예약")
        with st.form("booking_form"):
            form_col1, form_col2 = st.columns(2)
            total_price = 299000
            with form_col1:
                st.markdown("**숙소 예약 유형**")
                st.info(f"데이터 기반 추천 숙소 (기본가: {total_price:,.0f}원)")
                booking_type = "데이터 기반 추천 숙소"
                
                st.markdown("**결제 수단**")
                payment_method = st.radio("결제 수단", ["Toss", "카카오페이", "네이버페이", "신용카드", "무통장입금"], horizontal=True, label_visibility="collapsed")
            with form_col2:
                st.markdown("**예약자 정보**")
                user_name = st.text_input("예약자 성함")
                user_phone = st.text_input("전화번호 ('-' 제외)")
                st.markdown(f"**최종 결제 금액:**")
                st.subheader(f"{total_price:,.0f} 원")
            
            # --- [수정됨] (항목 2) ---
            if st.form_submit_button(f"'{selected_month_label}' 올인원 패키지 결제하기 (데모)", type="primary", use_container_width=True): # 이름 수정
                if not user_name or not user_phone:
                    st.error("예약자 정보를 입력해주세요.")
                else:
                    st.session_state.update({"user_name": user_name, "user_phone": user_phone, "payment_method": payment_method, 
                                             "booking_type": booking_type, "total_price": total_price, "selected_date": selected_date})
                    go_to_payment()
                    st.rerun()

    elif st.session_state.booking_step == "payment":
        st.subheader(f"'{st.session_state.payment_method}' 결제 진행 (데모)")
        st.info(f"**{st.session_state.user_name}**님, 아래 결제 정보를 확인하세요.\n"
                f"- **여행 시작일:** {st.session_state.selected_date.strftime('%Y년 %m월 %d일')}\n"
                f"- **선택 유형:** {st.session_state.booking_type}\n"
                f"- **최종 결제 금액:** {st.session_state.total_price:,.0f} 원")
        st.warning("이 화면은 실제 결제창이 아닌, 'GOLDEN JEJU' 플랫폼의 결제 흐름을 보여주기 위한 데모입니다.")
        col_pay, col_cancel = st.columns(2)
        with col_pay: st.button("최종 결제 완료 (데모)", type="primary", on_click=go_to_complete, use_container_width=True)
        with col_cancel: st.button("취소하고 돌아가기", on_click=reset_flow, use_container_width=True)

    elif st.session_state.booking_step == "complete":
        st.success(f"**{st.session_state.user_name}님의 예약이 완료되었습니다!**\n\n"
                   f"- **예약 상품:** {st.session_state.selected_date.strftime('%Y년 %m월')} 시그니처 패키지\n"
                   f"- **결제 금액:** {st.session_state.total_price:,.0f} 원 ({st.session_state.payment_method})\n"
                   f"- 예약 내역은 {st.session_state.user_phone}로 전송되었습니다. (데모)")
        st.balloons()
        # --- [수정됨] (항목 2) ---
        st.button("새로운 올인원 패키지 예약하기", on_click=reset_flow, use_container_width=True) # 이름 수정

if __name__ == "__main__":
    show_pass_page()