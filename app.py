import streamlit as st
import pandas as pd
import os

# 파일 경로 설정 (동일 폴더 내 CSV 파일)
FILE_PATH = "public_institutions_executive_salary_bp_5years-v2.csv"

# 페이지 기본 설정
st.set_page_config(page_title="공공기관 임원 보수 대시보드", page_icon="📊", layout="wide")
st.title("📊 공공기관 임원 보수 및 업무추진비 관리 대시보드")

# 데이터 불러오기 함수
@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    else:
        # 파일이 없을 경우 빈 데이터프레임 생성
        return pd.DataFrame(columns=[
            "기관명", "연도", "기관장 연봉(천원)", 
            "상임감사 연봉(천원)", "상임이사 연봉(천원)", "기관장 업무추진비(천원)"
        ])

# 세션 상태에 데이터 저장 (상태 유지를 위함)
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 탭(Tab) 구성
tab1, tab2 = st.tabs(["📝 데이터 조회 및 편집 (CRUD)", "📈 대시보드 시각화"])

# ---- 탭 1: 데이터 조회 및 편집 (CRUD) ----
with tab1:
    st.subheader("데이터 조회, 생성, 수정, 삭제")
    st.markdown("""
    - **조회**: 아래 표에서 전체 데이터를 확인할 수 있습니다.
    - **수정**: 변경하고 싶은 셀을 **더블 클릭**하여 값을 직접 수정하세요.
    - **생성**: 표의 가장 하단 빈 행을 클릭하여 새로운 데이터를 추가할 수 있습니다.
    - **삭제**: 표 왼쪽의 체크박스를 선택한 후 키보드의 `Delete` 키를 누르거나 휴지통 아이콘을 클릭하세요.
    """)
    
    # 엑셀처럼 동작하는 인터랙티브 데이터 에디터 적용
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",        # 행 추가/삭제 허용
        use_container_width=True,  # 가로폭 꽉 차게
        key="data_editor_1"
    )
    
    # 저장 버튼
    if st.button("💾 변경사항 저장 (CSV 파일 업데이트)"):
        # 변경된 데이터를 CSV 파일로 덮어쓰기 (한글 깨짐 방지 utf-8-sig)
        edited_df.to_csv(FILE_PATH, index=False, encoding='utf-8-sig')
        # 캐시 초기화 및 세션 업데이트
        st.cache_data.clear()
        st.session_state.df = edited_df
        st.success("✅ 성공적으로 CSV 파일에 저장되었습니다!")

# ---- 탭 2: 대시보드 시각화 ----
with tab2:
    st.subheader("기관별 연도별 추이 시각화")
    
    if not edited_df.empty:
        # 기관 선택 필터
        institution_list = edited_df["기관명"].dropna().unique()
        selected_inst = st.selectbox("조회할 기관을 선택하세요", institution_list)
        
        # 선택된 기관 데이터 필터링
        filtered_df = edited_df[edited_df["기관명"] == selected_inst].sort_values("연도")
        
        # 레이아웃 분할
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**[{selected_inst}] 기관장 연봉 추이**")
            # 연도별 연봉 라인 차트
            st.line_chart(filtered_df, x="연도", y="기관장 연봉(천원)")
            
        with col2:
            st.markdown(f"**[{selected_inst}] 기관장 업무추진비 추이**")
            # 연도별 업무추진비 바 차트
            st.bar_chart(filtered_df, x="연도", y="기관장 업무추진비(천원)", color="#ffaa00")
    else:
        st.warning("데이터가 없습니다. 첫 번째 탭에서 데이터를 추가해 주세요.")
