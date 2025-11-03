import streamlit as st
import pandas as pd
import os
import datetime
from PIL import Image
import navigation
import numpy as np

st.set_page_config(page_title="GOLDEN JEJU | 제주이야기", layout="wide", initial_sidebar_state="collapsed")
navigation.apply_theme()
navigation.show_header(current_page="app.py")

# --- 데이터 파일 설정 (게시물용, 댓글용) ---
upload_path = "community_uploads"
posts_file_path = os.path.join(upload_path, "community_posts.csv")
comments_file_path = os.path.join(upload_path, "community_comments.csv")

# --- 폴더 및 파일 관리 ---
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

def load_data(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return df
    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return df

def save_post(nickname, title, content, image_path):
    df_posts = load_data(posts_file_path, ["post_id", "timestamp", "nickname", "title", "content", "image_path"])
    
    post_id = f"post_{int(datetime.datetime.now().timestamp())}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_post = pd.DataFrame([{
        "post_id": post_id,
        "timestamp": timestamp,
        "nickname": nickname,
        "title": title,
        "content": content,
        "image_path": image_path
    }])
    
    df_posts = pd.concat([df_posts, new_post], ignore_index=True)
    df_posts.to_csv(posts_file_path, index=False, encoding='utf-8-sig')
    st.success("게시물이 성공적으로 등록되었습니다!")

def save_comment(post_id, nickname, comment_text):
    df_comments = load_data(comments_file_path, ["comment_id", "post_id", "timestamp", "nickname", "comment_text"])
    
    comment_id = f"comment_{int(datetime.datetime.now().timestamp())}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_comment = pd.DataFrame([{
        "comment_id": comment_id,
        "post_id": post_id,
        "timestamp": timestamp,
        "nickname": nickname,
        "comment_text": comment_text
    }])
    
    df_comments = pd.concat([df_comments, new_comment], ignore_index=True)
    df_comments.to_csv(comments_file_path, index=False, encoding='utf-8-sig')
    st.toast("댓글이 등록되었습니다.")

# --- 세션 상태 초기화 (페이지 뷰 전환용) ---
if 'view_post_id' not in st.session_state:
    st.session_state.view_post_id = None

# --- 데이터 로드 ---
df_posts = load_data(posts_file_path, ["post_id", "timestamp", "nickname", "title", "content", "image_path"])
df_comments = load_data(comments_file_path, ["comment_id", "post_id", "timestamp", "nickname", "comment_text"])


# --- UI ---
st.title("🍊 제주이야기 (자유 커뮤니티)")
st.caption("맛집, 풍경, 숙소, 꿀팁 등 제주 여행의 모든 경험을 자유롭게 나눠주세요.")


# --- 뷰 전환 로직 ---
if st.session_state.view_post_id is None:
    
    # --- [1] 목록 뷰 (List View) ---
    
    st.subheader("✍️ 새 이야기 작성하기")
    with st.form("new_post_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            nickname = st.text_input("닉네임", max_chars=10, placeholder="제주여행자")
            uploaded_image = st.file_uploader("사진 첨부 (선택)", type=['jpg', 'jpeg', 'png'])
        with col2:
            title = st.text_input("제목", max_chars=50, placeholder="예: 숨겨진 월정리 포토 스팟 공유!")
            content = st.text_area("내용", max_chars=500, height=150, placeholder="여행 후기를 자유롭게 작성해주세요.")
        
        submitted = st.form_submit_button("게시물 등록하기", type="primary", use_container_width=True)
        
        if submitted:
            if not all([nickname, title, content]):
                st.error("닉네임, 제목, 내용을 모두 입력해야 합니다.")
            else:
                image_path = None
                if uploaded_image:
                    try:
                        img = Image.open(uploaded_image)
                        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_extension = os.path.splitext(uploaded_image.name)[1]
                        image_filename = f"{now}_{nickname}{file_extension}"
                        image_path = os.path.join(upload_path, image_filename)
                        img.save(image_path)
                    except Exception as e:
                        st.error(f"파일 업로드 중 오류 발생: {e}")
                        image_path = None
                
                save_post(nickname, title, content, image_path)
                st.rerun()

    st.markdown("---")
    st.subheader("💬 최근 올라온 제주이야기")

    if df_posts.empty:
        st.info("아직 작성된 게시물이 없습니다. 첫 번째 이야기를 공유해주세요!")
    else:
        for index, row in df_posts.sort_values(by="timestamp", ascending=False).iterrows():
            post_id = row['post_id']
            
            with st.container():
                col_img, col_content = st.columns([1, 3])
                
                with col_img:
                    if pd.notna(row['image_path']) and row['image_path'] and os.path.exists(row['image_path']):
                        st.image(row['image_path'], width=150)
                    else:
                        st.markdown("<div style='height: 150px; width: 150px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 8px;'><span style='color: #888; font-size: 0.9rem;'>텍스트 전용</span></div>", unsafe_allow_html=True)
                
                with col_content:
                    st.markdown(f"### {row['title']}")
                    st.caption(f"작성자: {row['nickname']} | 작성일: {row['timestamp']}")
                    st.write(row['content'][:120] + "...")
                    
                    comment_count = len(df_comments[df_comments['post_id'] == post_id])
                    
                    if st.button(f"➡️ 전체글 보기 (댓글 {comment_count}개)", key=f"view_{post_id}"):
                        st.session_state.view_post_id = post_id
                        st.rerun()
                
                st.divider()

else:
    
    # --- [2] 상세 뷰 (Detail View) ---
    
    post_id = st.session_state.view_post_id
    try:
        selected_post = df_posts[df_posts['post_id'] == post_id].iloc[0]
    except IndexError:
        st.error("게시물을 찾을 수 없습니다. 목록으로 돌아갑니다.")
        st.session_state.view_post_id = None
        st.rerun()

    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.view_post_id = None
        st.rerun()

    st.markdown(f"# {selected_post['title']}")
    st.caption(f"작성자: {selected_post['nickname']} | 작성일: {selected_post['timestamp']}")
    st.markdown("---")
    
    if pd.notna(selected_post['image_path']) and selected_post['image_path'] and os.path.exists(selected_post['image_path']):
        st.image(selected_post['image_path'])
    
    st.write(selected_post['content'])
    
    st.markdown("---")
    st.markdown("##### 💬 댓글")
    
    post_comments = df_comments[df_comments['post_id'] == post_id].sort_values(by="timestamp")
    if post_comments.empty:
        st.info("아직 댓글이 없습니다. 첫 댓글을 남겨주세요.")
    else:
        for c_index, c_row in post_comments.iterrows():
            st.markdown(f"**{c_row['nickname']}** ({c_row['timestamp']})\n\n{c_row['comment_text']}")
            st.divider()
    
    with st.form(key=f"comment_form_{post_id}", clear_on_submit=True):
        comment_nickname = st.text_input("닉네임", max_chars=10, key=f"nick_{post_id}")
        comment_text = st.text_input("댓글 작성", placeholder="따뜻한 댓글을 남겨주세요.", key=f"text_{post_id}")
        
        if st.form_submit_button("댓글 등록"):
            if comment_nickname and comment_text:
                save_comment(post_id, comment_nickname, comment_text)
                st.rerun()
            else:
                st.warning("닉네임과 댓글 내용을 모두 입력해주세요.")