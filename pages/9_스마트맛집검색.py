import streamlit as st
import pandas as pd
import pydeck as pdk
import navigation
import os
import urllib.parse
import numpy as np

st.set_page_config(page_title="GOLDEN JEJU | 스마트 맛집 검색", layout="wide", initial_sidebar_state="collapsed")
navigation.apply_theme()
navigation.show_header(current_page="pages/9_스마트맛집검색.py")

DATA_FILE_PATH = r"C:\공모전\데이터\jeju_places_with_auto_keywords.csv"

# --- [수정됨] (항목 3) ---
# "https.raw..." -> "https://raw..."
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
# --- ---

ICON_MAPPING = {
    "marker": {"x": 0, "y": 0, "width": 128, "height": 128, "mask": True}
}

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"데이터 파일 '{file_path}'를 찾을 수 없습니다.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        df = df.rename(columns={
            'y': 'lat', 
            'x': 'lon', 
            'keywords': 'original_keywords' # 원본 키워드 (표시용)
        })
        
        df.dropna(subset=['lat', 'lon'], inplace=True)
        
        df['place_name'] = df['place_name'].fillna('').astype(str)
        df['category_name'] = df['category_name'].fillna('').astype(str)
        df['original_keywords'] = df['original_keywords'].fillna('').astype(str)

        df['search_blob'] = (
            df['place_name'] + ' ' + 
            df['category_name'].str.replace('>', ' ') + ' ' + 
            df['original_keywords'].str.replace(',', ' ')
        )
        
        df['naver_map_url'] = df['place_name'].apply(
            lambda x: f"https://map.naver.com/v5/search/{urllib.parse.quote(x)}"
        )
        
        return df
    
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        st.exception(e) 
        return pd.DataFrame()

df = load_data(DATA_FILE_PATH)

if 'itinerary_basket' not in st.session_state:
    st.session_state.itinerary_basket = []

if not df.empty:
    st.title("🔎 스마트 맛집 검색")
    st.caption("키워드를 선택해 원하는 맛집을 빠르게 찾아보세요.")
    
    selected_term = st.text_input(
        "검색어로 맛집 찾기:",
        placeholder="예: 흑돼지, 갈치 ..."
    )
    
    df_filtered = df.copy()
    
    if selected_term:
        df_filtered = df_filtered[df_filtered['search_blob'].str.contains(selected_term, na=False)]
    else:
        df_filtered = pd.DataFrame(columns=df.columns)

    df_filtered['icon_size'] = 30
    df_filtered['icon_name'] = 'marker'
        
    if 'selected_place_name' not in st.session_state:
        st.session_state.selected_place_name = None

    col2, col1 = st.columns([2, 1])

    with col1:
        st.subheader(f"🔍 검색 결과: {len(df_filtered)}곳")
        
        if st.button("전체 결과 지도 보기", use_container_width=True):
            st.session_state.selected_place_name = None
            st.rerun()
            
        st.markdown("---")

        with st.container(height=600):
            if df_filtered.empty and selected_term:
                st.warning(f"'{selected_term}'에 대한 검색 결과가 없습니다.")
            elif not selected_term:
                st.info("검색어를 입력하여 맛집 검색을 시작하세요.")
            else:
                for index, row in df_filtered.iterrows():
                    
                    btn_cols = st.columns([3, 1])
                    with btn_cols[0]:
                        if st.button(row['place_name'], key=f"btn_{index}"): 
                            st.session_state.selected_place_name = row['place_name']
                            st.rerun()
                    with btn_cols[1]:
                        if st.button("찜하기", key=f"add_{index}", use_container_width=True): 
                            place_name = row['place_name']
                            if place_name not in [item['name'] for item in st.session_state.itinerary_basket]:
                                new_item = {
                                    'name': place_name,
                                    'lat': row['lat'],
                                    'lon': row['lon'],
                                    'source': 'food' 
                                }
                                st.session_state.itinerary_basket.append(new_item)
                                st.toast(f"'{place_name}'을(를) 찜했습니다! (나만의 여행일정 연동)")
                            else:
                                st.toast(f"'{place_name}'은(는) 이미 찜한 장소입니다.")
                    st.caption(f"키워드: {row['original_keywords']}")
                    st.divider()

    with col2:
        st.subheader("📍 맛집 위치 지도")
        
        map_data = df_filtered
        zoom_level = 9
        center_lat = 33.361667
        center_lon = 126.529167
        
        if st.session_state.selected_place_name is not None:
            try:
                selected_row = df_filtered[df_filtered['place_name'] == st.session_state.selected_place_name].iloc[0]
                center_lat = selected_row['lat']
                center_lon = selected_row['lon']
                zoom_level = 13
                map_data = pd.DataFrame([selected_row])
                
                st.info(f"**{selected_row['place_name']}** 위치를 보고 있습니다.")
                st.link_button("🔗 네이버 지도로 상세정보 보기", selected_row['naver_map_url'], use_container_width=True, type="primary")
                
            except IndexError:
                st.session_state.selected_place_name = None
                st.rerun()

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom_level,
            pitch=45,
        )
        
        icon_layer = pdk.Layer(
            'IconLayer',
            data=map_data,
            icon_atlas=ICON_URL,
            icon_mapping=ICON_MAPPING,
            get_icon='icon_name',
            get_position='[lon, lat]',
            get_size='icon_size',
            size_scale=1,
            get_color='[242, 107, 33, 200]',
            pickable=True,
        )

        tooltip_html = f"""
        <b>{{place_name}}</b><br/>
        키워드: {{original_keywords}}<br/>
        <a href={{naver_map_url}} target="_blank" style="color: white; text-decoration: underline;">네이버 지도에서 보기 ↗</a>
        """

        tooltip = {
            "html": tooltip_html,
            "style": {
                "backgroundColor": "rgba(40, 40, 40, 0.9)",
                "color": "white",
                "fontFamily": "'Noto Sans KR', sans-serif",
                "borderRadius": "5px",
                "padding": "10px"
            }
        }

        r = pdk.Deck(
            layers=[icon_layer], 
            initial_view_state=view_state,
            map_style=pdk.map_styles.LIGHT, 
            tooltip=tooltip
        )
        st.pydeck_chart(r, use_container_width=True)
else:
    st.error(f"맛집 데이터를 표시할 수 없습니다. '{DATA_FILE_PATH}' 파일이 올바른지 확인해주세요.")