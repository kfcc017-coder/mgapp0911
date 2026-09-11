import streamlit as st
import pandas as pd
import os

# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="주요 금융기관 정기예금 금리 대시보드",
    page_icon="🏦",
    layout="wide"
)

CSV_FILE = "주요_금융기관_정기예금_금리비교_2026-09-10.csv"


# ============================================================
# CSV 불러오기
# ============================================================

def load_data():

    if not os.path.exists(CSV_FILE):

        st.error(
            f"CSV 파일을 찾을 수 없습니다.\n\n"
            f"찾는 파일명: {CSV_FILE}"
        )

        st.info(
            "GitHub 저장소에서 app.py와 CSV 파일이 "
            "같은 폴더에 있는지 확인해주세요."
        )

        st.stop()

    try:

        df = pd.read_csv(
            CSV_FILE
        )

        return df

    except UnicodeDecodeError:

        try:

            df = pd.read_csv(
                CSV_FILE,
                encoding="cp949"
            )

            return df

        except Exception as e:

            st.error(
                f"CSV 파일을 읽을 수 없습니다.\n\n{e}"
            )

            st.stop()

    except Exception as e:

        st.error(
            f"CSV 파일을 읽는 중 오류가 발생했습니다.\n\n{e}"
        )

        st.stop()


df = load_data()


# ============================================================
# 사이드바
# ============================================================

with st.sidebar:

    st.title("🏦 예금 금리 분석")

    menu = st.radio(
        "메뉴",
        [
            "📊 대시보드",
            "🔍 데이터 조회",
            "📈 금리 분석",
            "📋 원본 데이터"
        ]
    )

    st.divider()

    if st.button(
        "🔄 새로고침",
        use_container_width=True
    ):
        st.rerun()

    st.caption(
        f"데이터 파일\n{CSV_FILE}"
    )


# ============================================================
# 대시보드
# ============================================================

if menu == "📊 대시보드":

    st.title(
        "📊 주요 금융기관 정기예금 금리 대시보드"
    )

    st.caption(
        "2026년 9월 10일 기준 금융기관 정기예금 금리 비교"
    )

    # --------------------------------------------------------
    # 기본 데이터 정보
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "데이터 건수",
        f"{len(df):,}건"
    )

    col2.metric(
        "컬럼 수",
        f"{len(df.columns):,}개"
    )

    col3.metric(
        "결측값",
        f"{df.isna().sum().sum():,}개"
    )

    st.divider()

    st.subheader(
        "📋 데이터 미리보기"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🔎 CSV 컬럼 정보"
    )

    column_df = pd.DataFrame({
        "컬럼명": df.columns,
        "데이터형": [
            str(df[col].dtype)
            for col in df.columns
        ],
        "결측값": [
            df[col].isna().sum()
            for col in df.columns
        ]
    })

    st.dataframe(
        column_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 데이터 조회
# ============================================================

elif menu == "🔍 데이터 조회":

    st.title(
        "🔍 금융기관 데이터 조회"
    )

    search = st.text_input(
        "통합 검색",
        placeholder="은행명, 상품명 등을 입력하세요."
    )

    filtered_df = df.copy()

    if search:

        mask = (
            filtered_df
            .astype(str)
            .apply(
                lambda row:
                row.str.contains(
                    search,
                    case=False,
                    na=False
                ).any(),
                axis=1
            )
        )

        filtered_df = filtered_df[
            mask
        ]

    st.write(
        f"조회 결과: **{len(filtered_df):,}건**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = (
        filtered_df
        .to_csv(
            index=False
        )
        .encode(
            "utf-8-sig"
        )
    )

    st.download_button(
        "📥 조회 결과 CSV 다운로드",
        data=csv_data,
        file_name="deposit_rate_search.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# 금리 분석
# ============================================================

elif menu == "📈 금리 분석":

    st.title(
        "📈 정기예금 금리 분석"
    )

    # 숫자형으로 변환 가능한 컬럼 찾기
    numeric_candidates = []

    for column in df.columns:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if converted.notna().sum() > 0:
            numeric_candidates.append(
                column
            )

    if not numeric_candidates:

        st.warning(
            "분석 가능한 숫자형 금리 컬럼을 찾지 못했습니다."
        )

    else:

        selected_column = st.selectbox(
            "분석할 금리 컬럼",
            numeric_candidates
        )

        values = pd.to_numeric(
            df[selected_column],
            errors="coerce"
        ).dropna()

        if values.empty:

            st.warning(
                "선택한 컬럼에서 숫자 데이터를 찾을 수 없습니다."
            )

        else:

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "평균",
                f"{values.mean():.2f}"
            )

            col2.metric(
                "최고",
                f"{values.max():.2f}"
            )

            col3.metric(
                "최저",
                f"{values.min():.2f}"
            )

            col4.metric(
                "최고-최저 차이",
                f"{values.max() - values.min():.2f}"
            )

            st.divider()

            st.subheader(
                f"📊 {selected_column} 분포"
            )

            chart_df = pd.DataFrame({
                selected_column: values
            })

            st.bar_chart(
                chart_df
            )

            # ----------------------------------------------
            # 최고 / 최저 데이터
            # ----------------------------------------------

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "🔺 최고 금리"
                )

                max_value = values.max()

                max_rows = df[
                    pd.to_numeric(
                        df[selected_column],
                        errors="coerce"
                    )
                    == max_value
                ]

                st.dataframe(
                    max_rows,
                    use_container_width=True,
                    hide_index=True
                )

            with col2:

                st.subheader(
                    "🔻 최저 금리"
                )

                min_value = values.min()

                min_rows = df[
                    pd.to_numeric(
                        df[selected_column],
                        errors="coerce"
                    )
                    == min_value
                ]

                st.dataframe(
                    min_rows,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# 원본 데이터
# ============================================================

elif menu == "📋 원본 데이터":

    st.title(
        "📋 원본 CSV 데이터"
    )

    st.write(
        f"총 **{len(df):,}건**의 데이터가 있습니다."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = (
        df
        .to_csv(
            index=False
        )
        .encode(
            "utf-8-sig"
        )
    )

    st.download_button(
        "📥 전체 데이터 다운로드",
        data=csv_data,
        file_name=CSV_FILE,
        mime="text/csv",
        use_container_width=True
    )
