import streamlit as st
import pandas as pd
import os

# 페이지 기본 설정 (와이드 모드로 설정하여 조회 칸을 넓게 사용)
st.set_page_config(page_title="공공기관 임원 보수 대시보드", page_icon="🏢", layout="wide")

FILE_PATH = "public_institutions_executive_salary_bp_5years-v2.csv"

# 데이터 불러오기 함수
@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(FILE_PATH):
        # 숫자가 소수점으로 나오는 것을 방지하기 위해 타입 지정
        df = pd.read_csv(FILE_PATH)
        for col in ["연도", "기관장 연봉(천원)", "상임감사 연봉(천원)", "상임이사 연봉(천원)", "기관장 업무추진비(천원)"]:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)
        return df
    else:
        return pd.DataFrame(columns=[
            "기관명", "연도", "기관장 연봉(천원)", 
            "상임감사 연봉(천원)", "상임이사 연봉(천원)", "기관장 업무추진비(천원)"
        ])

def save_data(df):
    df.to_csv(FILE_PATH, index=False, encoding='utf-8-sig')
    st.cache_data.clear()
    st.session_state.df = df

if 'df' not in st.session_state:
    st.session_state.df = load_data()

st.title("🏢 공공기관 임원 보수 및 업무추진비 현황")
st.markdown("---")

# 화면을 좌우 비율 7:3으로 분할 (조회 칸을 훨씬 넓게)
col_view, col_action = st.columns([7, 3])

# ==========================================
# 왼쪽 영역: 데이터 넓게 조회 및 시각화
# ==========================================
with col_view:
    st.subheader("📋 전체 데이터 조회")
    
    # 데이터 검색 기능 추가
    search_term = st.text_input("🔍 기관명 검색", "")
    display_df = st.session_state.df.copy()
    if search_term:
        display_df = display_df[display_df["기관명"].str.contains(search_term, case=False, na=False)]
    
    # 표 출력 (조회 칸)
    st.dataframe(
        display_df, 
        use_container_width=True, 
        height=400, # 표 높이 지정
        hide_index=True
    )
    
    st.markdown("---")
    st.subheader("📈 기관별 차트 분석")
    if not display_df.empty:
        inst_list = display_df["기관명"].unique()
        selected_inst = st.selectbox("분석할 기관 선택", inst_list, key="chart_select")
        
        chart_df = display_df[display_df["기관명"] == selected_inst].sort_values("연도")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**기관장 연봉 추이**")
            st.line_chart(chart_df, x="연도", y="기관장 연봉(천원)")
        with c2:
            st.write("**기관장 업무추진비 추이**")
            st.bar_chart(chart_df, x="연도", y="기관장 업무추진비(천원)", color="#ffaa00")

# ==========================================
# 오른쪽 영역: 직관적인 생성/수정/삭제 패널
# ==========================================
with col_action:
    st.subheader("⚙️ 데이터 관리 (생성·수정·삭제)")
    
    action = st.radio(
        "수행할 작업을 선택하세요",
        ["새로운 데이터 추가 (Create)", "기존 데이터 수정 (Update)", "데이터 삭제 (Delete)"]
    )
    
    st.markdown("---")
    df = st.session_state.df
    
    if action == "새로운 데이터 추가 (Create)":
        with st.form("create_form", clear_on_submit=True):
            st.write("새 기관/연도 데이터를 입력하세요")
            new_inst = st.text_input("기관명")
            new_year = st.number_input("연도 (예: 2026)", min_value=2000, max_value=2100, step=1, value=2026)
            new_ceo_sal = st.number_input("기관장 연봉 (천원)", min_value=0, step=1000)
            new_aud_sal = st.number_input("상임감사 연봉 (천원)", min_value=0, step=1000)
            new_dir_sal = st.number_input("상임이사 연봉 (천원)", min_value=0, step=1000)
            new_ceo_bp = st.number_input("업무추진비 (천원)", min_value=0, step=500)
            
            submitted = st.form_submit_button("➕ 데이터 추가하기")
            if submitted:
                if not new_inst:
                    st.error("기관명을 입력해주세요.")
                else:
                    new_row = pd.DataFrame([{
                        "기관명": new_inst, "연도": new_year, "기관장 연봉(천원)": new_ceo_sal,
                        "상임감사 연봉(천원)": new_aud_sal, "상임이사 연봉(천원)": new_dir_sal, "기관장 업무추진비(천원)": new_ceo_bp
                    }])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    save_data(updated_df)
                    st.success(f"{new_inst} ({new_year}년) 데이터가 추가되었습니다.")
                    st.rerun()
                    
    elif action == "기존 데이터 수정 (Update)":
        if df.empty:
            st.warning("수정할 데이터가 없습니다.")
        else:
            # 수정할 행을 선택하기 위해 고유값 생성
            df['unique_id'] = df['기관명'] + " - " + df['연도'].astype(str) + "년"
            selected_id = st.selectbox("수정할 데이터를 선택하세요", df['unique_id'].tolist())
            
            # 선택된 행의 데이터 가져오기
            target_idx = df[df['unique_id'] == selected_id].index[0]
            target_row = df.loc[target_idx]
            
            with st.form("update_form"):
                st.write(f"**{selected_id}** 수정")
                # 기관명과 연도는 변경 불가 처리 (PK 성격)
                st.text_input("기관명 (수정불가)", value=target_row["기관명"], disabled=True)
                st.number_input("연도 (수정불가)", value=int(target_row["연도"]), disabled=True)
                
                up_ceo_sal = st.number_input("기관장 연봉 (천원)", value=int(target_row["기관장 연봉(천원)"]), step=1000)
                up_aud_sal = st.number_input("상임감사 연봉 (천원)", value=int(target_row["상임감사 연봉(천원)"]), step=1000)
                up_dir_sal = st.number_input("상임이사 연봉 (천원)", value=int(target_row["상임이사 연봉(천원)"]), step=1000)
                up_ceo_bp = st.number_input("업무추진비 (천원)", value=int(target_row["기관장 업무추진비(천원)"]), step=500)
                
                updated = st.form_submit_button("✏️ 수정사항 저장")
                if updated:
                    df.at[target_idx, "기관장 연봉(천원)"] = up_ceo_sal
                    df.at[target_idx, "상임감사 연봉(천원)"] = up_aud_sal
                    df.at[target_idx, "상임이사 연봉(천원)"] = up_dir_sal
                    df.at[target_idx, "기관장 업무추진비(천원)"] = up_ceo_bp
                    
                    df = df.drop(columns=['unique_id']) # 임시 컬럼 삭제
                    save_data(df)
                    st.success("데이터가 성공적으로 수정되었습니다.")
                    st.rerun()

    elif action == "데이터 삭제 (Delete)":
        if df.empty:
            st.warning("삭제할 데이터가 없습니다.")
        else:
            df['unique_id'] = df['기관명'] + " - " + df['연도'].astype(str) + "년"
            del_selected = st.selectbox("삭제할 데이터를 선택하세요", df['unique_id'].tolist())
            
            st.warning(f"정말로 **{del_selected}** 데이터를 삭제하시겠습니까?")
            
            if st.button("🗑️ 삭제하기", type="primary"):
                target_idx = df[df['unique_id'] == del_selected].index[0]
                df = df.drop(index=target_idx)
                df = df.drop(columns=['unique_id']) # 임시 컬럼 삭제
                save_data(df)
                st.success("데이터가 삭제되었습니다.")
                st.rerun()
