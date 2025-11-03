import streamlit as st
import pandas as pd
import os
import navigation
import urllib.parse
import requests

st.set_page_config(page_title="GOLDEN JEJU | 맞춤 숙소 찾기", layout="wide", initial_sidebar_state="collapsed")
# --- [수정됨] ---
navigation.apply_theme()
navigation.show_header(current_page="pages/2_숙소필터.py")
# --- ---

# --- 1. KAKAO API 설정 ---
KAKAO_API_KEY = "bf3481d1f6e13e299cc42b118357ace8"
GEOCODE_URL = "https.dapi.kakao.com/v2/local/search/keyword.json"

# --- 2. API 호출 함수 (주소 반환용) ---
@st.cache_data
def get_address_kakao(place_name):
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": f"제주 {place_name}"}
    try:
        response = requests.get(GEOCODE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['documents']:
            doc = data['documents'][0]
            return doc.get('address_name', doc.get('road_address_name', '주소 정보 없음'))
    except Exception as e:
        print(f"Kakao Geocoding Error for {place_name}: {e}")
    return "주소 정보를 불러올 수 없습니다."

# --- 3. 데이터 로드 ---
data_folder_name = '데이터'
data_path = data_folder_name
accom_file = os.path.join(data_path, 'golden_compass_accommodation_clean.csv')

@st.cache_data
def load_accom_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        return pd.DataFrame()

# --- 4. UI ---
def show_accom_page():
    st.title("🏨 맞춤 숙소 찾기")
    st.caption("액티브 시니어에게 중요한 '편의성'을 기준으로 숙소를 필터링합니다.")
    
    df_accom = load_accom_data(accom_file)
    if df_accom.empty:
        st.warning("숙소 데이터 파일을 찾을 수 없습니다.")
        # return # [수정] 데이터가 없어도 필터는 보이도록 주석 처리

    st.markdown("---")
    
    # --- [수정됨] (항목 2) ---
    st.markdown("**(1) 숙소 위치 선택**")
    selected_location = st.radio(
        "숙소 위치",
        ["제주도 전체", "제주시", "서귀포시"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**(2) 숙소 유형 (다중 선택)**")
        selected_types = st.multiselect(
            "숙소 유형",
            ["호텔", "모텔", "펜션", "풀빌라", "글램핑", "캠핑", "기타"],
            placeholder="원하는 숙소 유형을 선택하세요.",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("**(3) 시설/서비스 (다중 선택)**")
        selected_amenities = st.multiselect(
            "시설/서비스",
            ["주차 가능", "반려동물 동반", "스파", "객실 금연", "OTT 제공"],
            placeholder="원하는 시설/서비스를 선택하세요.",
            label_visibility="collapsed"
        )
    
    st.markdown("**(4) 등급 선택 (0=등급없음)**")
    rating_range = st.slider("등급", min_value=0, max_value=5, value=(0, 5), label_visibility="collapsed")
    
    st.markdown("**(5) 시니어 편의 옵션 (다중 선택)**")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        chk_breakfast = st.checkbox("조식 제공 (O)", value=False)
    with col2:
        chk_accessible = st.checkbox("편의시설 보유 (O)", value=False)
    with col3:
        chk_pet = st.checkbox("애완동물 동반 (O)", value=False) # (항목 2의 '반려동물'과 중복되지만, 기존 코드 유지)
    with col4:
        chk_late_checkin = st.checkbox("LATE 체크인 (O)", value=False)
    with col5:
        chk_shuttle = st.checkbox("셔틀버스 운행 (O)", value=False)
    # --- ---
        
    st.markdown("---")

    # (데이터 필터링 로직은 요청대로 비워둡니다)
    # df_accom = ... (위에서 선택한 selected_location, selected_types, selected_amenities 등으로 필터링)

    filtered_accom = df_accom[(df_accom['등급'] >= rating_range[0]) & (df_accom['등급'] <= rating_range[1])]
    
    if chk_breakfast:
        filtered_accom = filtered_accom[filtered_accom['조식제공여부'] == 'O']
    if chk_accessible:
        filtered_accom = filtered_accom[filtered_accom['장애인전용객실여부'] == 'O']
    if chk_pet:
        filtered_accom = filtered_accom[filtered_accom['애완동물동반허용여부'] == 'O']
    if chk_late_checkin:
        filtered_accom = filtered_accom[filtered_accom['LATE체크인여부'] == 'O']
    if chk_shuttle:
        filtered_accom = filtered_accom[filtered_accom['셔틀버스운행여부'] == 'O']
            
    st.markdown(f"**총 {len(filtered_accom)}개의 숙소가 검색되었습니다.**")
    st.markdown("---")

    with st.container(height=600):
        if filtered_accom.empty:
            st.info("선택한 조건에 맞는 숙소가 없습니다.")
        else:
            for index, row in filtered_accom.iterrows():
                with st.container():
                    cols = st.columns([3, 1])
                    with cols[0]:
                        if row['등급'] > 0:
                            st.markdown(f"#### {row['콘텐츠명']} ({row['등급']}성급)")
                        else:
                            st.markdown(f"#### {row['콘텐츠명']}")
                        
                        # --- API로 주소 가져오기 ---
                        address = get_address_kakao(row['콘텐츠명'])
                        st.caption(f"📍 {address}")
                        # --- ---
                        
                        amenities = []
                        if row.get('조식제공여부') == 'O': amenities.append("🍳 조식")
                        if row.get('장애인전용객실여부') == 'O': amenities.append("♿ 편의시설")
                        if row.get('LATE체크인여부') == 'O': amenities.append("🌙 LATE 체크인")
                        if row.get('셔틀버스운행여부') == 'O': amenities.append("🚌 셔틀")
                        if row.get('애완동물동반허용여부') == 'O': amenities.append("🐾 펫 동반")
                        
                        if amenities:
                            st.write(" | ".join(amenities))
                        else:
                            st.caption("편의시설 정보 없음")
                    
                    with cols[1]:
                        search_query = urllib.parse.quote(f"제주 {row['콘텐츠명']}")
                        map_link = f"https.map.naver.com/v5/search/{search_query}"
                        st.link_button("🔗 네이버 지도로 보기", map_link, use_container_width=True, type="primary")
                
                st.divider()

if __name__ == "__main__":
    show_accom_page()