import streamlit as st
import pandas as pd
import os
import datetime
from PIL import Image
import urllib.parse
import navigation

st.set_page_config(page_title="GOLDEN JEJU | 맛집 커뮤니티", layout="wide", initial_sidebar_state="collapsed")
navigation.apply_theme()
navigation.show_header(current_page="app.py")

upload_path = "gourmet_uploads"
board_file = os.path.join(upload_path, "gourmet_board.csv")

JEJU_REGIONS = ["지역을 선택하세요", "제주시 연동", "제주시 노형동", "제주시 애월읍", "제주시 구좌읍", "제주시 한림읍", 
                "제주시 조천읍", "서귀포시 중문동", "서귀포시 성산읍", "서귀포시 안덕면", "서귀포시 표선면", "서귀포시 대정읍", "우도면", "기타/직접입력"]

def load_board_data():
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    if not os.path.exists(board_file):
        pd.DataFrame(columns=["timestamp", "nickname", "restaurant_name", "region", "comment", "image_path"]).to_csv(board_file, index=False)
    return pd.read_csv(board_file)

def show_gourmet_page():
    st.title("🍲 맛집 커뮤니티")
    st.caption("시니어들이 직접 인증한 '진짜' 맛집 후기를 공유하는 공간입니다.")
    
    st.subheader("✍️ 나만의 맛집 후기 작성하기")
    with st.form("gourmet_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            nickname = st.text_input("닉네임", max_chars=10, placeholder="제주미식가")
            restaurant_name = st.text_input("맛집 이름", placeholder="OO 흑돼지")
            region = st.selectbox("맛집 지역 (읍면동)", options=JEJU_REGIONS)
            uploaded_image = st.file_uploader("맛집 인증샷", type=['jpg', 'jpeg', 'png'])
        with col2:
            comment = st.text_area("맛집 후기 (일반 텍스트만 가능)", max_chars=300, height=250, placeholder="이 집은...")
        if st.form_submit_button("맛집 후기 등록하기", type="primary"):
            if not all([nickname, restaurant_name, comment, uploaded_image]) or region == "지역을 선택하세요":
                st.error("모든 항목(닉네임, 맛집 이름, 지역, 사진, 후기)을 입력/선택해주세요.")
            else:
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(upload_path, f"{now}_{nickname}{os.path.splitext(uploaded_image.name)[1]}")
                Image.open(uploaded_image).save(image_path)
                new_entry = pd.DataFrame([{"timestamp": now, "nickname": nickname, "restaurant_name": restaurant_name, 
                                           "region": region, "comment": comment, "image_path": image_path}])
                df_board = pd.concat([load_board_data(), new_entry], ignore_index=True)
                df_board.to_csv(board_file, index=False, encoding='utf-8-sig')
                st.success("맛집 후기가 성공적으로 등록되었습니다! (데모)")
                st.rerun()

    st.markdown("---")
    st.subheader("최근 등록된 맛집 후기")
    df_board_sorted = load_board_data().sort_values(by="timestamp", ascending=False)
    if df_board_sorted.empty:
        st.info("아직 등록된 맛집 후기가 없습니다.")
    else:
        for index, row in df_board_sorted.iterrows():
            st.markdown(f"### {row['restaurant_name']} (by. {row['nickname']})")
            c1, c2 = st.columns([1, 2])
            if os.path.exists(row['image_path']):
                with c1: st.image(row['image_path'])
            with c2:
                st.markdown(f"**📍 지역:** {row['region']}")
                st.write(row['comment'])
                search_query = f"{row['region']} {row['restaurant_name']}"
                st.link_button(f"📍 '{search_query}' 지도로 위치 확인하기", f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}", use_container_width=True)
            st.markdown("---")

if __name__ == "__main__":
    show_gourmet_page()