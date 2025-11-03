import streamlit as st

def apply_theme():
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
        
        body, .stApp {
            font-family: 'Noto+Sans+KR', sans-serif !important;
            background-color: #FFFFFF !important;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        header[data-testid="stHeader"], footer {
            display: none !important;
        }
        
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 3rem !important;
            border: none;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        .main-page-header {
            background-color: #fffbf5 !important;
            padding-top: 3rem; 
            padding-bottom: 2rem;
            text-align: center;
        }
        .main-page-header .logo-text a {
            font-size: 3.5rem !important; 
            margin-bottom: 10px;
            color: #F26B21 !important; 
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 900;
            text-decoration: none;
        }
        .main-page-header .logo-description {
            font-size: 1.4rem !important; 
            color: #555 !important; 
            margin-bottom: 2rem;
            font-family: 'Noto Sans KR', sans-serif;
        }
        .main-page-header [data-testid="stHorizontalBlock"] {
            display: none;
        }

        .golden-header-v12-final {
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: #fffbf5 !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            border-bottom: 1px solid #ffefe2;
            border: none;
        }
        .golden-header-v12-final [data-testid="stHorizontalBlock"] {
             padding-top: 0.5rem;
             padding-bottom: 0.5rem;
             min-height: 100px; 
             align-items: center;
        }
        .golden-header-v12-final [data-testid="stHorizontalBlock"]:first-of-type {
            padding-top: 1rem;
            padding-bottom: 0.5rem;
        }
        .golden-header-v12-final .logo-text a {
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 900;
            font-size: 2.2rem; 
            color: #F26B21;
            text-decoration: none;
            transition: color 0.2s ease;
            display: block;
            text-align: left;
            padding-bottom: 0;
        }
        .golden-header-v12-final .logo-text a:hover {
            color: #d95f1b;
        }
        .golden-header-v12-final .logo-subtitle {
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 1.1rem !important; 
            color: #555;
            margin-top: -8px; 
            margin-bottom: 5px;
        }
        
        div[data-testid="stButton"] > button { 
            background-color: #fff7f2 !important; 
            border: 2px solid #F26B21 !important; 
            padding: 0.4rem 0.6rem !important; 
        }
        
        div[data-testid="stButton"] > button * { 
            font-family: 'Noto Sans KR', sans-serif !important;
            background-color: transparent !important; 
            color: #F26B21 !important; 
            font-size: 1.2rem !important; 
            font-weight: 700 !important; 
        }
        
        div[data-testid="stButton"] > button:hover {
            background-color: #ffe6d9 !important; 
            border: 2px solid #d95f1b !important; 
        }

        div[data-testid="stButton"] > button:hover * {
            background-color: transparent !important;
            color: #d95f1b !important; 
        }
        
        
        .stApp p, .stApp li, .stApp .stMarkdown { 
            font-size: 1rem !important; 
        }
        [data-testid="stCaption"] { 
            font-size: 0.95rem !important; 
        }
        
        [data-testid="stMetricValue"] { 
            font-size: 1.9rem !important; 
        }
        [data-testid="stMetricLabel"] { 
            font-size: 0.9rem !important; 
            color: #555 !important; 
        }
        

        .month-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: center;
            background-color: #f9f9f9;
            min-height: 135px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
        }
        .month-card h5 {
            margin: 0 0 5px 0;
            font-size: 0.95rem; 
            font-weight: 700;
            color: #333;
        }
        .month-card .icon {
            font-size: 2.2rem; 
            line-height: 1.2;
        }
        .month-card .label {
            font-size: 0.9rem; 
            font-weight: 600;
            margin: 0;
            height: 2.6em; 
            display: flex; 
            align-items: center;
            justify-content: center;
            white-space: pre-line; 
        }
        
        .status-매우쾌적 { border-top: 5px solid #007bff; background-color: #e6f7ff; }
        .status-쾌적 { border-top: 5px solid #28a745; background-color: #f0fff4; }
        .status-보통 { border-top: 5px solid #ffc107; background-color: #fffbea; }
        .status-혼잡 { border-top: 5px solid #fd7e14; background-color: #fffaf0; }
        .status-매우혼잡 { border-top: 5px solid #dc3545; background-color: #fff5f5; }
        .status-데이터 없음 { border-top: 5px solid #ccc; background-color: #fafafa; }

        .legend-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-bottom: 1rem;
            padding: 0.5rem 0;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9rem;
        }
        .legend-color-box {
            width: 15px;
            height: 15px;
            border: 1px solid #ccc;
        }
        .legend-blue { background-color: #e6f7ff; border-color: #007bff; }
        .legend-green { background-color: #f0fff4; border-color: #28a745; }
        .legend-yellow { background-color: #fffbea; border-color: #ffc107; }
        .legend-orange { background-color: #fffaf0; border-color: #fd7e14; }
        .legend-red { background-color: #fff5f5; border-color: #dc3545; }
        
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def show_header(current_page: str, subtitle: str = None):
    
    if current_page == "app.py":
        st.markdown('<div class="main-page-header">', unsafe_allow_html=True)
        st.markdown('<div class="logo-text"><a href="/" target="_self">🍊 GOLDEN JEJU</a></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="logo-description">{subtitle}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="golden-header-v12-final">', unsafe_allow_html=True)

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
            render_button("pages/1_쾌적도캘린더.py")
        with link_cols_1[1]:
            render_button("pages/2_숙소필터.py")
        with link_cols_1[2]:
            render_button("pages/3_황금동행.py")
        with link_cols_1[3]:
            render_button("pages/4_황금원패스.py")
        with link_cols_1[4]:
            render_button("pages/5_제주이야기.py")
        
        
        link_cols_2 = st.columns(5)
        with link_cols_2[0]:
            render_button("pages/6_미식게시판.py")
        with link_cols_2[1]:
            render_button("pages/7_나만의_여행일정.py")
        with link_cols_2[2]:
            render_button("pages/8_스마트추천맵.py")
        with link_cols_2[3]:
            render_button("pages/9_스마트맛집검색.py")
        with link_cols_2[4]:
            render_button("pages/10_지역별추천.py")

        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="golden-header-v12-final">', unsafe_allow_html=True)

        logo_cols = st.columns(1)
        with logo_cols[0]:
            st.markdown('<div class="logo-text"><a href="/" target="_self">🍊 GOLDEN JEJU</a></div>', unsafe_allow_html=True)
            if subtitle:
                st.markdown(f'<p class="logo-subtitle">{subtitle}</p>', unsafe_allow_html=True)
        
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
            render_button("pages/1_쾌적도캘린더.py")
        with link_cols_1[1]:
            render_button("pages/2_숙소필터.py")
        with link_cols_1[2]:
            render_button("pages/3_황금동행.py")
        with link_cols_1[3]:
            render_button("pages/4_황금원패스.py")
        with link_cols_1[4]:
            render_button("pages/5_제주이야기.py")
        
        
        link_cols_2 = st.columns(5)
        with link_cols_2[0]:
            render_button("pages/6_미식게시판.py")
        with link_cols_2[1]:
            render_button("pages/7_나만의_여행일정.py")
        with link_cols_2[2]:
            render_button("pages/8_스마트추천맵.py")
        with link_cols_2[3]:
            render_button("pages/9_스마트맛집검색.py")
        with link_cols_2[4]:
            render_button("pages/10_지역별추천.py")

        st.markdown('</div>', unsafe_allow_html=True)