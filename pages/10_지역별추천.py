import streamlit as st
import pandas as pd
import os
import navigation
import urllib.parse
import requests 

st.set_page_config(page_title="GOLDEN JEJU | 지역별 추천", layout="wide", initial_sidebar_state="collapsed")
navigation.apply_theme()
navigation.show_header(current_page="pages/10_지역별추천.py")

# --- 카카오 API 키 및 URL 정의 ---
KAKAO_API_KEY = "bf3481d1f6e13e299cc42b118357ace8"
GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

# --- 1. 카카오 API 호출 함수 (캐시 적용) ---
@st.cache_data
def search_kakao_places(query, size=5):
    """
    Kakao 키워드 검색 API를 호출하여 장소 목록(상위 5개)을 반환합니다.
    """
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query, "size": size}
    try:
        response = requests.get(GEOCODE_URL, headers=headers, params=params)
        response.raise_for_status() 
        data = response.json()
        return data.get('documents', []) 
    except Exception as e:
        # API 키 할당량이 초과되었을 수도 있습니다.
        st.error(f"Kakao API 호출 중 오류 (쿼리: {query}): {e}")
        st.warning("API 키가 유효한지 또는 일일/월간 API 요청 할당량을 초과하지 않았는지 확인하세요.")
        return []

# --- 2. 찜하기 세션 초기화 ---
if 'itinerary_basket' not in st.session_state:
    st.session_state.itinerary_basket = []

# --- 3. 찜하기 로직 함수 ---
def add_to_basket(place_name, lat, lon, source_type):
    if place_name not in [item['name'] for item in st.session_state.itinerary_basket]:
        new_item = {
            'name': place_name,
            'lat': lat,
            'lon': lon,
            'source': source_type 
        }
        st.session_state.itinerary_basket.append(new_item)
        st.toast(f"'{place_name}'을(를) 찜했습니다! (나만의 여행일정 연동)")
    else:
        st.toast(f"'{place_name}'은(는) 이미 찜한 장소입니다.")

# --- 4. [수정] 장소/맛집 리스트 표시 함수 (API 기반) ---
# [수정] 'api_query_suffix' 인자 추가
def display_places(filter_keyword, source_type, title, emoji, no_data_msg, api_query_suffix):
    """
    API를 호출하고, 결과를 st.container(border=True) 내에 표시합니다.
    """
    st.subheader(f"{emoji} {title}")
    
    # --- [수정] ---
    # 1. API 검색어 생성 (예: "애월 관광지", "제주시 맛집")
    # "추천" 단어 제거
    query = f"{filter_keyword} {api_query_suffix}" 
    # --- ---
    
    # 2. API 호출
    places_list = search_kakao_places(query, size=5)
    
    # 3. 디자인 - 고정 높이 컨테이너
    with st.container(height=400):
        if not places_list:
            st.info(no_data_msg) # 'no_data_msg'도 검색어에 맞게 수정됨
            return

        for i, place in enumerate(places_list):
            place_name = place.get('place_name', '이름 없음')
            lat = float(place.get('y', 0)) 
            lon = float(place.get('x', 0)) 
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{place_name}**")
                st.caption(place.get('road_address_name', place.get('address_name', '')))
                
                naver_link = f"https://map.naver.com/v5/search/{urllib.parse.quote(place_name)}"
                st.link_button("🔗 네이버 지도로 보기", naver_link)
            
            with col2:
                st.button("찜하기", key=f"add_{source_type}_{filter_keyword}_{i}", 
                          on_click=add_to_basket, 
                          args=(place_name, lat, lon, source_type),
                          use_container_width=True)
            st.divider()

# --- 5. [수정] 메인 UI (데이터 로드 로직 제거) ---
st.title("📍 지역별 추천") # "Live API" 문구 제거
st.caption("제주의 주요 지역을 선택하고, 카카오 API가 엄선한 추천 관광지와 맛집을 확인하세요.")
st.info("이 페이지는 '스마트 추천맵'(사용자 필터링)과 달리, **지역별**로 엄선된 장소를 바로 보여주는 **큐레이션 페이지**입니다.")
st.markdown("---")

# 주요 지역 정의
regions = {
    "제주시(도심)": "제주시",
    "애월읍": "애월",
    "한림읍": "한림",
    "서귀포시(도심)": "서귀포시",
    "성산읍": "성산",
    "중문": "중문"
}

tabs = st.tabs(list(regions.keys()))

if not KAKAO_API_KEY:
    st.error("Kakao API 키가 설정되지 않았습니다. (API KEY가 코드에 하드코딩 되어있는지 확인하세요)")
else:
    for i, tab in enumerate(tabs):
        region_name = list(regions.keys())[i] # 탭 이름
        region_keyword = regions[region_name] # 검색 키워드
        
        with tab:
            st.header(f"🍊 {region_name} 추천 TOP 5")
            
            col_attr, col_food = st.columns(2)
            
            with col_attr:
                with st.container(border=True):
                    # [수정] api_query_suffix="관광지", no_data_msg 수정
                    display_places(
                        filter_keyword=region_keyword,
                        source_type="map",
                        title="추천 관광지", 
                        emoji="🗺️",
                        api_query_suffix="관광지", # "추천" 제거
                        no_data_msg=f"'{region_keyword} 관광지'를 찾을 수 없습니다."
                    )

            with col_food:
                with st.container(border=True):
                    # [수정] api_query_suffix="맛집", no_data_msg 수정
                    display_places(
                        filter_keyword=region_keyword,
                        source_type="food",
                        title="추천 맛집", 
                        emoji="🍲",
                        api_query_suffix="맛집", # "추천" 제거
                        no_data_msg=f"'{region_keyword} 맛집'을 찾을 수 없습니다."
                    )