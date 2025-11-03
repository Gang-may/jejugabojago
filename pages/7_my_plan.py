import streamlit as st
import navigation
import datetime
import pandas as pd
import os
import numpy as np
import requests
import urllib.parse
import pydeck as pdk 

# --- 지도 관련 상수 ---
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
ICON_MAPPING = {
    "marker": {"x": 0, "y": 0, "width": 128, "height": 128, "mask": True}
}

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


st.set_page_config(page_title="GOLDEN JEJU | 나만의 여행 일정", layout="wide", initial_sidebar_state="collapsed")
navigation.apply_theme()
navigation.show_header(current_page="pages/7_나만의_여행일정.py")

KAKAO_API_KEY = "bf3481d1f6e13e299cc42b118357ace8" # API 키는 원본 유지
GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
DIRECTIONS_URL = "https://apis-navi.kakao.com/v1/directions" 

@st.cache_data
def get_geocode_kakao(address):
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    try:
        response = requests.get(GEOCODE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['documents']:
            lat = float(data['documents'][0]['y'])
            lon = float(data['documents'][0]['x'])
            return (lat, lon)
        else:
            raise Exception(f"'{address}'에 대한 검색 결과가 없습니다.")
    except Exception as e:
        return (np.nan, np.nan) 

@st.cache_data
def get_driving_distance_kakao(start_lon, start_lat, goal_lon, goal_lat):
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "origin": f"{start_lon},{start_lat}",
        "destination": f"{goal_lon},{goal_lat}",
        "summary": "true"
    }
    try:
        response = requests.get(DIRECTIONS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['routes']:
            summary = data['routes'][0]['summary']
            distance_km = summary['distance'] / 1000.0
            duration_min = summary['duration'] / 60.0
            return (distance_km, duration_min)
        else:
            raise Exception("경로를 찾을 수 없습니다.")
    except Exception as e:
        raise Exception(f"Kakao Directions Error: {e}")

if 'my_itinerary' not in st.session_state:
    st.session_state.my_itinerary = {}

if 'itinerary_basket' not in st.session_state:
    st.session_state.itinerary_basket = []

# --- [수정] Session State를 사용하여 현재 활성화된 탭 인덱스 저장 ---
if 'active_day_index' not in st.session_state:
    st.session_state.active_day_index = 0

def add_schedule(date_str, time, place_name, memo, source="manual"):
    lat, lon = get_geocode_kakao(place_name)
    
    new_schedule = {
        "time": time.strftime("%H:%M"), 
        "place": place_name, 
        "memo": memo,
        "lat": lat,
        "lon": lon,
        "source": source 
    }
    
    if date_str not in st.session_state.my_itinerary:
        st.session_state.my_itinerary[date_str] = []
    
    st.session_state.my_itinerary[date_str].append(new_schedule)
    st.session_state.my_itinerary[date_str].sort(key=lambda x: x['time'])
    
    if source == "manual":
        st.success(f"{date_str} {time.strftime('%H:%M')} '{place_name}' 일정이 추가되었습니다.")

def delete_schedule(date_str, schedule_index):
    try:
        del st.session_state.my_itinerary[date_str][schedule_index]
        if not st.session_state.my_itinerary[date_str]:
            del st.session_state.my_itinerary[date_str]
    except (KeyError, IndexError):
        st.error("일정 삭제 중 오류가 발생했습니다.")

def remove_from_basket(place_name):
    st.session_state.itinerary_basket = [
        item for item in st.session_state.itinerary_basket if item['name'] != place_name
    ]

def update_schedule_time(date_str, index, session_key):
    try:
        new_time_obj = st.session_state[session_key]
        new_time_str = new_time_obj.strftime("%H:%M")
        
        st.session_state.my_itinerary[date_str][index]['time'] = new_time_str
        
        st.session_state.my_itinerary[date_str].sort(key=lambda x: x['time'])
        st.rerun() 
    except (KeyError, IndexError):
        st.error("시간 업데이트 중 오류가 발생했습니다.")

def set_active_day(index):
    st.session_state.active_day_index = index

def handle_course_selection(date_str, day_key):
    selected_course = st.session_state[day_key]
    
    if date_str in st.session_state.my_itinerary:
        st.session_state.my_itinerary[date_str] = [
            s for s in st.session_state.my_itinerary[date_str] if s.get('source') != 'auto'
        ]

    if selected_course == "코스 선택 안함":
        st.toast(f"{date_str}의 자동 코스를 비웠습니다.")
        return 

    places_to_add = st.session_state.generated_courses[selected_course]

    start_time = datetime.time(9, 0)
    for i, place_name in enumerate(places_to_add):
        current_time = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(minutes=90*i)).time()
        add_schedule(date_str, current_time, place_name, memo="자동 생성 코스", source="auto")
    
    st.toast(f"{date_str}에 '{selected_course}' 일정이 자동 추가되었습니다!", icon="🗓️")

def visualize_itinerary(schedule_list, map_container):
    if not schedule_list:
        with map_container:
            st.subheader(f"🗺️ Day 경로 시각화")
            st.caption("타임라인에 있는 장소들을 순서대로 연결합니다. (좌표 없는 장소는 제외)")
            st.info("지도에 표시할 장소가 없습니다.")
        return
        
    df_map = pd.DataFrame([s for s in schedule_list if pd.notna(s['lat']) and pd.notna(s['lon'])])
    
    if df_map.empty:
        with map_container:
            st.subheader(f"🗺️ Day 경로 시각화")
            st.caption("타임라인에 있는 장소들을 순서대로 연결합니다. (좌표 없는 장소는 제외)")
            st.info("지도에 표시할 유효한 좌표가 없습니다.")
        return

    df_map = df_map.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    df_map['place_index'] = np.arange(len(df_map))
    df_map['time'] = [s['time'] for s in schedule_list if pd.notna(s['lat']) and pd.notna(s['lon'])]
    df_map['place'] = [s['place'] for s in schedule_list if pd.notna(s['lat']) and pd.notna(s['lon'])]
    
    df_map['icon_name'] = 'marker'
    df_map['icon_size'] = 30
    df_map['color'] = 255 

    paths = []
    for i in range(len(df_map) - 1):
        paths.append({
            'source': [df_map.iloc[i]['longitude'], df_map.iloc[i]['latitude']],
            'target': [df_map.iloc[i+1]['longitude'], df_map.iloc[i+1]['latitude']],
            'index': i + 1
        })
    df_paths = pd.DataFrame(paths)
    
    line_layer = pdk.Layer(
        'LineLayer',
        data=df_paths,
        get_source_position='source',
        get_target_position='target',
        get_color='[242, 107, 33, 200]',
        get_width=5,
        pickable=True
    )
    
    icon_layer = pdk.Layer(
        'IconLayer',
        data=df_map,
        get_icon='icon_name',
        get_position='[longitude, latitude]',
        get_size='icon_size',
        size_scale=1,
        get_color='[242, 107, 33, 200]', 
        icon_atlas=ICON_URL,
        icon_mapping=ICON_MAPPING,
        pickable=True,
    )
    
    center_lat = df_map['latitude'].mean()
    center_lon = df_map['longitude'].mean()
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10, 
        pitch=45,
    )
    
    tooltip_html = """
    <b>{place}</b> ({place_index}번째 장소)<br/>
    시간: {time}
    """
    
    r = pdk.Deck(
        layers=[line_layer, icon_layer],
        initial_view_state=view_state,
        map_style=pdk.map_styles.LIGHT,
        tooltip={
            "html": tooltip_html,
            "style": {
                "backgroundColor": "rgba(40, 40, 40, 0.9)",
                "color": "white",
                "fontFamily": "'Noto Sans KR', sans-serif",
                "borderRadius": "5px",
                "padding": "10px"
            }
        }
    )
    
    with map_container:
        st.subheader(f"🗺️ Day 경로 시각화")
        st.caption("타임라인에 있는 장소들을 순서대로 연결합니다. (좌표 없는 장소는 제외)")
        st.pydeck_chart(r, use_container_width=True)


st.title("✍️ 나만의 여행 일정")
st.caption("'GOLDEN JEJU' 추천 캘린더와 연동되는 나만의 여행 플래너입니다.")
st.markdown("---")


st.header("1. 여행 정보 (필수)")
col1, col2 = st.columns(2)
with col1:
    st.text_input("여행 일정 이름", "나의 2026년 제주 힐링 여행")
with col2:
    today = datetime.date.today()
    selected_dates = st.date_input("여행 날짜 선택 (시작일 ~ 종료일)",
        value=(today, today + datetime.timedelta(days=2)),
        min_value=today,
        max_value=datetime.date(2030, 12, 31))

if selected_dates and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    num_days = (end_date - start_date).days + 1

    st.markdown("---")
    st.header("2. 자동 코스 생성 (Beta)")

    with st.container(border=True):
        col_basket, col_auto_course = st.columns(2)

        with col_basket:
            st.subheader("🛒 찜한 장소 목록")
            st.caption("'스마트 추천맵(🗺️)'과 '스마트 맛집(🍲)'에서 찜한 장소입니다. (클릭 시 제거)")
            
            basket_items = st.session_state.itinerary_basket
            if not basket_items:
                st.info("💡 찜한 장소가 없습니다. '스마트 추천맵'과 '스마트 맛집'에서 장소를 찜해보세요!")
            else:
                with st.container(height=400): 
                    cols_layout = st.columns(2) 
                    for i, item in enumerate(basket_items):
                        col_index = i % 2
                        item_label = f"🗺️ {item['name']}" if item['source'] == 'map' else f"🍲 {item['name']}"
                        
                        if cols_layout[col_index].button(f"❌ {item_label}", key=f"basket_{i}", use_container_width=True, help="클릭하여 목록에서 제거"):
                            remove_from_basket(item['name'])
                            st.rerun()

        with col_auto_course:
            st.subheader("🤖 위치 기반 코스 생성")
            
            if not SKLEARN_AVAILABLE:
                st.error("자동 코스 생성 기능을 사용하려면 'scikit-learn' 라이브러리가 필요합니다.")
                st.code("pip install scikit-learn", language="bash")
            elif not basket_items:
                st.warning("먼저 찜한 장소 목록에 1개 이상의 장소를 추가해주세요.")
            elif num_days > len(basket_items):
                st.warning(f"여행 일수({num_days}일)가 찜한 장소 수({len(basket_items)}개)보다 많습니다. 장소를 더 추가해주세요.")
            else:
                st.info(f"'{num_days}일' 일정, 총 {len(basket_items)}개의 찜한 장소를 기반으로 자동 코스를 제안합니다.")
                
                if st.button("🗺️ 자동 코스 생성하기", type="primary", use_container_width=True):
                    locations_df = pd.DataFrame(basket_items)
                    coordinates = locations_df[['lat', 'lon']].values
                    
                    kmeans = KMeans(n_clusters=num_days, random_state=42, n_init=10)
                    locations_df['cluster'] = kmeans.fit_predict(coordinates)
                    
                    st.session_state.generated_courses = {}
                    
                    for i in range(num_days):
                        cluster_places = locations_df[locations_df['cluster'] == i]
                        course_name = f"추천 코스 {i+1}"
                        st.session_state.generated_courses[course_name] = cluster_places['name'].tolist()

            if 'generated_courses' in st.session_state:
                st.markdown("---")
                st.subheader("🗓️ 생성된 코스를 날짜에 배정하세요")
                
                st.warning("코스를 선택하면 '3. 상세 일정 플래너'에 **자동으로 추가**됩니다. (기존 자동 추가 항목은 덮어씀)")
                
                generated_courses = st.session_state.generated_courses
                course_options = list(generated_courses.keys())
                
                st.markdown("##### 📄 생성된 추천 코스 목록")
                with st.container(border=True, height=200): 
                    for course_name, places in generated_courses.items():
                        st.markdown(f"**{course_name}** (총 {len(places)}곳)")
                        st.write(" → ".join(places))
                        st.caption("---")
                
                for i in range(num_days):
                    current_date = start_date + datetime.timedelta(days=i)
                    current_date_str = current_date.isoformat()
                    day_label = f"Day {i+1} ({current_date.strftime('%m/%d')})"
                    
                    day_key = f"course_day_{i}"
                    st.selectbox(
                        f"**{day_label}**에 배정할 코스를 선택하세요:",
                        options=["코스 선택 안함"] + course_options,
                        key=day_key,
                        on_change=handle_course_selection, 
                        kwargs={'date_str': current_date_str, 'day_key': day_key} 
                    )

    st.markdown("---")
    st.header("3. 상세 일정 플래너 (수동)")
    
    # --- [수정] 지도 동기화 로직 시작 (버튼 기반 탭 전환) ---
    
    col_timeline, col_map = st.columns([1, 1])
    
    # 지도 영역 플레이스홀더 (Right Column)
    map_container_placeholder = col_map.container()
    
    with col_timeline:
        st.markdown('<div style="display: flex; gap: 5px; margin-bottom: 20px;">', unsafe_allow_html=True)
        
        tab_labels = [f"Day {i+1} ({ (start_date + datetime.timedelta(days=i)).strftime('%m/%d') })" for i in range(num_days)]
        
        # 버튼 스타일을 조정하기 위해 컬럼 분리
        day_cols = st.columns(num_days)
        
        for i, label in enumerate(tab_labels):
            # 활성화된 탭의 스타일 지정: 현재 active_day_index와 일치하면 primary (주황색 테두리)
            button_style = "primary" if i == st.session_state.active_day_index else "secondary"
            
            with day_cols[i]:
                # 버튼 클릭 시 set_active_day 콜백 호출하여 인덱스 업데이트
                if st.button(label, key=f"day_btn_{i}", type=button_style, use_container_width=True):
                    set_active_day(i)
                    st.rerun() 

        st.markdown('</div>', unsafe_allow_html=True)
    
    # 4. 활성화된 Day의 내용 렌더링
    active_day_index = st.session_state.active_day_index
    
    # 현재 활성화된 탭의 날짜 계산
    current_date = start_date + datetime.timedelta(days=active_day_index)
    current_date_str = current_date.isoformat()
    
    with col_timeline:
        # 이 영역 전체가 활성화된 탭의 내용입니다.
        i = active_day_index # [수정] active_tab_index 대신 active_day_index 사용
        
        st.subheader(f"Day {i+1} : {current_date.strftime('%Y년 %m월 %d일 (%A)')}")
        
        st.markdown(
            """
            <style>
            [data-testid="stHorizontalBlock"] > div > div > div {
                padding-top: 2px !important;
                padding-bottom: 2px !important;
            }
            [data-testid="stTimeInput"] > div > input {
                height: 30px !important; 
                line-height: 30px !important;
            }
            [data-testid="stButton"] button {
                margin-top: 0px !important;
                margin-bottom: 0px !important;
                padding: 0px 5px !important;
            }
            </style>
            """, unsafe_allow_html=True
        )
        
        # 수동 추가 폼
        with st.form(key=f"form_day_{i}", clear_on_submit=True):
            st.markdown("**새 일정 추가하기**")
            
            form_cols = st.columns([1, 2, 2])
            new_time = form_cols[0].time_input("시간", value=datetime.time(9, 0), key=f"t_{i}")
            new_place = form_cols[1].text_input("장소 (직접 입력)", 
                                              key=f"p_custom_{i}", 
                                              placeholder="예: 제주국제공항, 성산일출봉, 숙소/맛집 이름")
            
            new_memo = form_cols[2].text_input("간단 메모", placeholder="예: 입장료 5,000원", key=f"m_{i}")
            
            if st.form_submit_button("➕ 일정 추가", type="primary", use_container_width=True):
                if not new_place:
                    st.warning("장소를 입력해주세요.")
                else:
                    add_schedule(current_date_str, new_time, new_place, new_memo, source="manual")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("**타임라인**")
        
        if current_date_str not in st.session_state.my_itinerary or not st.session_state.my_itinerary[current_date_str]:
            st.info("아직 추가된 일정이 없습니다. 새 일정을 추가해보세요.")
            schedule_list = []
        else:
            schedule_list = st.session_state.my_itinerary[current_date_str]
            
            for idx, schedule in enumerate(schedule_list):
                schedule_cols = st.columns([1, 3, 2, 1])
                
                time_key = f"time_edit_{current_date_str}_{idx}"
                current_time_obj = datetime.datetime.strptime(schedule['time'], "%H:%M").time()
                
                schedule_cols[0].time_input(
                    "시간", 
                    value=current_time_obj, 
                    key=time_key,
                    label_visibility="collapsed",
                    on_change=update_schedule_time, 
                    kwargs={'date_str': current_date_str, 'index': idx, 'session_key': time_key}
                )
                
                place_label = f"**📍 {schedule['place']}**"
                if schedule.get('source') == 'auto':
                    place_label += " 🤖"
                    
                schedule_cols[1].markdown(place_label)
                schedule_cols[2].caption(f"📝 {schedule['memo'] if schedule['memo'] else ' '}")
                
                if schedule_cols[3].button("삭제", key=f"del_{current_date_str}_{idx}", use_container_width=True):
                    delete_schedule(current_date_str, idx)
                    st.rerun()
                
                if idx > 0:
                    prev_schedule = schedule_list[idx-1]
                    
                    if pd.notna(prev_schedule['lat']) and pd.notna(schedule['lat']):
                        try:
                            distance_km, duration_min = get_driving_distance_kakao(
                                prev_schedule['lon'], prev_schedule['lat'],
                                schedule['lon'], schedule['lat']
                            )
                            st.info(f"🚗 {prev_schedule['place']}에서 약 **{distance_km:.1f} km** (예상 {duration_min:.0f} 분)")
                        except Exception as e:
                            st.warning(f"🚗 {prev_schedule['place']}에서 경로 탐색에 실패했습니다. (API 오류)")
                    else:
                        st.info(f"🚗 (이전 장소 또는 현재 장소의 좌표를 찾을 수 없어 거리 계산이 불가능합니다.)")
                
                st.divider()

    # 5. 지도 렌더링 (활성화된 Day의 내용으로 map_container_placeholder를 덮어씁니다)
    visualize_itinerary(schedule_list, map_container_placeholder)
        
else:
    st.info("여행 시작일과 종료일을 선택하여 2일 이상의 일정을 만들어주세요.")