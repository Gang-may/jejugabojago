import streamlit as st
import pandas as pd
import pydeck as pdk
import navigation
import os
import urllib.parse

st.set_page_config(page_title="GOLDEN JEJU | 스마트 추천맵", layout="wide", initial_sidebar_state="collapsed") 
navigation.apply_theme()
navigation.show_header(current_page="pages/8_스마트추천맵.py")

DATA_FILE_PATH = os.path.join("데이터", "jeju_places_mean.xlsx")

# --- [수정됨] (항목 3) ---
# "https.raw..." -> "https://raw..."
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
# --- ---

ICON_MAPPING = {
    "marker": {"x": 0, "y": 0, "width": 128, "height": 128, "mask": True}
}

@st.cache_data
def load_map_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"데이터 파일 '{file_path}'를 찾을 수 없습니다.")
        st.error("'데이터' 폴더에 'jeju_places_mean.xlsx' 파일이 있는지 확인해주세요.")
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path)
        
        df.columns = df.columns.str.strip()
        
        if '위도' in df.columns and '경도' in df.columns:
             df = df.rename(columns={'위도': 'lat', '경도': 'lon'})
        elif 'y' in df.columns and 'x' in df.columns:
             df = df.rename(columns={'y': 'lat', 'x': 'lon'})

        df.dropna(subset=['lat', 'lon'], inplace=True)
        
        df['naver_map_url'] = df['장소명'].apply(
            lambda x: f"https://map.naver.com/v5/search/{urllib.parse.quote(x)}"
        )
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        st.warning("Excel 파일을 읽으려면 'openpyxl' 라이브러리가 필요할 수 있습니다. (pip install openpyxl)")
        return pd.DataFrame()

df = load_map_data(DATA_FILE_PATH)

if 'itinerary_basket' not in st.session_state:
    st.session_state.itinerary_basket = []

if not df.empty:
    st.title("🗺️ GOLDEN JEJU 스마트 추천맵")
    st.caption("필터를 선택하여 연령/성별 선호 관광지를 확인하고, 랭킹과 지도를 통해 위치를 찾아보세요.")
    
    filter_options = {
        "ActiveSenior (60대+) 추천": "ActiveSenior_Score",
        "70대 이상 여성": "70대 이상 여성 비율",
        "70대 이상 남성": "70대 이상 남성 비율",
        "60대 여성": "60대 여성 비율",
        "60대 남성": "60대 남성 비율",
        "50대 여성": "50대 여성 비율",
        "50대 남성": "50대 남성 비율",
        "40대 여성": "40대 여성 비율",
        "40대 남성": "40대 남성 비율",
        "30대 여성": "30대 여성 비율",
        "30대 남성": "30대 남성 비율",
        "20대 여성": "20대 여성 비율",
        "20대 남성": "20대 남성 비율",
        "10대 이하 여성": "10대 이하 여성 비율",
        "10대 이하 남성": "10대 이하 남성 비율"
    }
    
    available_options = [key for key in filter_options.keys() if filter_options[key] in df.columns]
    
    selected_label = st.selectbox(
        "분석 기준 선택:",
        options=available_options
    )
    
    sort_by_col = filter_options[selected_label]
    
    df_sorted = df.sort_values(by=sort_by_col, ascending=False).reset_index(drop=True)
    df_sorted['랭킹'] = df_sorted.index + 1
    
    max_score = df_sorted[sort_by_col].max()
    if max_score > 0:
        df_sorted['icon_size'] = 20 + (df_sorted[sort_by_col] / max_score) * 40
    else:
        df_sorted['icon_size'] = 20
        
    df_sorted['icon_name'] = 'marker'
        
    if 'selected_place_index' not in st.session_state:
        st.session_state.selected_place_index = None

    col2, col1 = st.columns([2, 1])

    with col1:
        st.subheader(f"🏆 {selected_label} Top 20")

        if st.button("전체 Top 20 지도 보기", use_container_width=True):
            st.session_state.selected_place_index = None
            st.rerun()

        st.markdown("---")
        
        with st.container(height=600):
            for i, row in df_sorted.head(20).iterrows():
                
                btn_cols = st.columns([3, 1])
                with btn_cols[0]:
                    if st.button(f"**{row['랭킹']}위.** {row['장소명']}", key=f"rank_{i}", use_container_width=True):
                        st.session_state.selected_place_index = i
                        st.rerun()
                with btn_cols[1]:
                    if st.button("찜하기", key=f"add_{i}", use_container_width=True):
                        place_name = row['장소명']
                        if place_name not in [item['name'] for item in st.session_state.itinerary_basket]:
                            new_item = {
                                'name': place_name,
                                'lat': row['lat'],
                                'lon': row['lon'],
                                'source': 'map' 
                            }
                            st.session_state.itinerary_basket.append(new_item)
                            st.toast(f"'{place_name}'을(를) 찜했습니다! (나만의 여행일정 연동)")
                        else:
                            st.toast(f"'{place_name}'은(는) 이미 찜한 장소입니다.")

    with col2:
        st.subheader("📍 위치별 분포 지도")
        
        map_data = df_sorted.head(20)
        zoom_level = 9
        center_lat = df_sorted['lat'].mean()
        center_lon = df_sorted['lon'].mean()
        
        if st.session_state.selected_place_index is not None:
            try:
                selected_row = df_sorted.iloc[st.session_state.selected_place_index]
                center_lat = selected_row['lat']
                center_lon = selected_row['lon']
                zoom_level = 13
                map_data = pd.DataFrame([selected_row])
                
                st.info(f"**{selected_row['장소명']}** 위치를 보고 있습니다.")
                st.link_button("🔗 네이버 지도로 상세정보 보기", selected_row['naver_map_url'], use_container_width=True, type="primary")
                
            except IndexError:
                st.session_state.selected_place_index = None
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
        <b>{{장소명}}</b> ({{중분류명}})<br/>
        {selected_label}: {{{sort_by_col}}}<br/>
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
    st.error("데이터 지도를 표시할 수 없습니다. '데이터' 폴더에 'jeju_places_mean.xlsx' 파일이 올바른지 확인해주세요.")