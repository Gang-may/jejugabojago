# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Jeju Active Senior — 인기스팟추천", layout="wide")
st.title("🧭 제주 액티브 시니어 인기 스팟 추천 (2023–2025)")

DATA_FILE = "jeju_seogwi_with_coords.csv"  


# 1) 데이터 로드 & 정규화 함수

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    # 필수 컬럼 존재 확인
    needed = [
        "장소명", "위도", "경도",
        "50대 남성 비율","60대 남성 비율","70대 이상 남성 비율",
        "50대 여성 비율","60대 여성 비율","70대 이상 여성 비율"
    ]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        st.error(f"필수 컬럼 누락: {missing}")
        st.stop()


    month_num = None
    if "월" in df.columns:
        
        s = df["월"].astype(str).str.strip()
        
        m1 = pd.to_datetime(s, format="%Y%m", errors="coerce")
       
        m2 = pd.to_datetime(s, errors="coerce")
        
        m3 = pd.to_numeric(s, errors="coerce")
        month_num = (
            m1.dt.month.fillna(m2.dt.month).fillna(m3).astype("Int64")
        )
    elif "Ta Ym" in df.columns:
        s = df["Ta Ym"].astype(str).str.strip()
        month_num = pd.to_datetime(s, format="%Y%m", errors="coerce").dt.month.astype("Int64")
    else:
        # 연/월이 따로 있을 수도 있음
        if {"연도","월번호"}.issubset(df.columns):
            month_num = pd.to_numeric(df["월번호"], errors="coerce").astype("Int64")

    if month_num is None:
        st.error("월 정보를 찾을 수 없습니다. (예: '월' 또는 'Ta Ym' 필요)")
        st.stop()

    df["month_num"] = month_num

    # 연도 컬럼 보정
    if "연도" not in df.columns:
        # YYYYMM 형태에서 연도 추출 시도
        if "Ta Ym" in df.columns:
            df["연도"] = pd.to_datetime(df["Ta Ym"].astype(str), format="%Y%m", errors="coerce").dt.year
        else:
            df["연도"] = np.nan
    df["연도"] = pd.to_numeric(df["연도"], errors="coerce")

    # 액티브 시니어(50대 이상) 남/여 별도 평균
    df["남성_액티브시니어"] = df[["50대 남성 비율","60대 남성 비율","70대 이상 남성 비율"]].mean(axis=1)
    df["여성_액티브시니어"] = df[["50대 여성 비율","60대 여성 비율","70대 이상 여성 비율"]].mean(axis=1)

    # 좌표 숫자화 & 제주 권역 보정
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")
    df = df.dropna(subset=["위도","경도"])
    df = df[(33.0 < df["위도"]) & (df["위도"] < 34.2) & (125.9 < df["경도"]) & (df["경도"] < 127.2)]

    # 기간: 2023~2025만 사용 (있으면 필터)
    if df["연도"].notna().any():
        df = df[(df["연도"] >= 2023) & (df["연도"] <= 2025)]

    return df

df = load_data(DATA_FILE)


# 2) 사이드바 

with st.sidebar.expander("🌟 인기스팟추천", expanded=True):
    # 월 후보(데이터에 존재하는 월만)
    month_options = sorted([int(m) for m in df["month_num"].dropna().unique()])
    month_labels = [f"{m:02d}월" for m in month_options]
    month_map = dict(zip(month_labels, month_options))
    sel_month_label = st.selectbox("월 선택", month_labels, index=month_labels.index(f"{max(month_options):02d}월"))

    gender = st.radio("성별 선택", ["남성", "여성"], horizontal=True)


# 3) 필터 적용 & TOP20 산출 (월 + 성별), 월은 연도 무시하고 3개년의 같은 '월'을 평균

sel_month = month_map[sel_month_label]
col_ratio = "남성_액티브시니어" if gender == "남성" else "여성_액티브시니어"

dfm = df[df["month_num"] == sel_month].copy()

# 관광지별 평균(동일 장소의 여러 관측치 -> 평균)
top = (dfm.groupby(["장소명","위도","경도"], as_index=False)[col_ratio]
          .mean()
          .sort_values(col_ratio, ascending=False)
          .head(20))


# 4) 지도(핀만 표시) + 툴팁/팝업
m = folium.Map(location=[33.38, 126.55], zoom_start=10, tiles="CartoDB positron", control_scale=True)

for _, r in top.iterrows():
    name = r["장소명"]
    val = float(r[col_ratio])  # 비율(%)로 들어왔다고 가정
    popup = f"<b>{name}</b><br/>{gender} 50대 이상 방문비율(최근3개년 {sel_month_label} 평균): {val:.2f}%"
    tooltip = f"{name} — {val:.2f}%"
    folium.Marker(
        location=[float(r["위도"]), float(r["경도"])],
        tooltip=tooltip,
        popup=folium.Popup(popup, max_width=360)
    ).add_to(m)

st.subheader(f"📍 {sel_month_label} · {gender} 기준 — 인기스팟 TOP 20")
st_folium(m, width=1100, height=720)

# 하단 표(확인용)
st.dataframe(
    top.rename(columns={col_ratio: f"{gender} 50대+ 방문비율(%)"})
       .style.format({f"{gender} 50대+ 방문비율(%)": "{:.2f}"})
)
