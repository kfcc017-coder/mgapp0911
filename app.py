import os

import pandas as pd
import streamlit as st


# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="정기예금 금리 CRUD 대시보드",
    page_icon="🏦",
    layout="wide",
)

CSV_FILE = "주요_금융기관_정기예금_금리비교_2026-09-10.csv"


# ============================================================
# CSV 데이터 함수
# ============================================================

def load_data():
    """CSV 파일을 문자열 중심으로 불러옵니다."""

    if not os.path.exists(CSV_FILE):
        st.error(f"CSV 파일을 찾을 수 없습니다: {CSV_FILE}")
        st.info(
            "GitHub 저장소에서 app.py와 CSV 파일이 "
            "같은 폴더에 있는지 확인해주세요."
        )
        st.stop()

    encodings = ["utf-8-sig", "utf-8", "cp949"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                CSV_FILE,
                encoding=encoding,
                dtype=str,
                keep_default_na=False,
            )
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다.\n\n{e}")
            st.stop()

    st.error("CSV 파일의 문자 인코딩을 확인할 수 없습니다.")
    st.stop()


def save_data(dataframe):
    """현재 DataFrame을 CSV 파일로 저장합니다."""

    try:
        dataframe.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig",
        )
        return True

    except Exception as e:
        st.error(f"CSV 저장 중 오류가 발생했습니다.\n\n{e}")
        return False


def make_row_label(dataframe, index):
    """수정/삭제 대상 선택용 표시 문자열을 생성합니다."""

    row = dataframe.loc[index]

    values = []

    for column in dataframe.columns[:3]:
        value = str(row[column]).strip()

        if value:
            values.append(value)

    text = " | ".join(values)

    if not text:
        text = f"데이터 {index + 1}"

    return f"{index + 1}. {text}"


def numeric_series(dataframe, column):
    """%, 쉼표 등이 포함된 숫자 데이터를 숫자로 변환합니다."""

    cleaned = (
        dataframe[column]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    )


# ============================================================
# 데이터 로딩
# ============================================================

df = load_data()


# ============================================================
# 사이드바
# ============================================================

with st.sidebar:

    st.title("🏦 예금 금리 관리")

    menu = st.radio(
        "메뉴",
        [
            "📊 대시보드",
            "🔍 데이터 조회",
            "➕ 데이터 등록",
            "✏️ 데이터 수정",
            "🗑️ 데이터 삭제",
            "📈 금리 분석",
            "📋 원본 데이터",
        ],
    )

    st.divider()

    if st.button(
        "🔄 데이터 새로고침",
        use_container_width=True,
    ):
        st.rerun()

    st.caption("현재 데이터 파일")

    st.code(CSV_FILE)

    st.info(
        "CSV 파일을 직접 읽고 수정하는 "
        "교육·실습용 CRUD 대시보드입니다."
    )


# ============================================================
# 1. 대시보드
# ============================================================

if menu == "📊 대시보드":

    st.title("📊 주요 금융기관 정기예금 금리 대시보드")

    st.caption(
        "정기예금 금리 비교 · 조회 · 등록 · 수정 · 삭제"
    )

    total_rows = len(df)
    total_columns = len(df.columns)
    empty_cells = (df == "").sum().sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "전체 데이터",
        f"{total_rows:,}건",
    )

    col2.metric(
        "데이터 항목",
        f"{total_columns:,}개",
    )

    col3.metric(
        "빈 값",
        f"{empty_cells:,}개",
    )

    st.divider()

    st.subheader("📋 전체 데이터")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("🧱 데이터 구조")

    structure_df = pd.DataFrame(
        {
            "컬럼명": df.columns,
            "입력 데이터 수": [
                (df[column] != "").sum()
                for column in df.columns
            ],
            "빈 값": [
                (df[column] == "").sum()
                for column in df.columns
            ],
        }
    )

    st.dataframe(
        structure_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 2. 데이터 조회
# ============================================================

elif menu == "🔍 데이터 조회":

    st.title("🔍 금융기관 정기예금 데이터 조회")

    search = st.text_input(
        "통합 검색",
        placeholder="금융기관명, 상품명, 금리 등을 입력하세요.",
    )

    filtered_df = df.copy()

    if search:

        mask = filtered_df.astype(str).apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False,
            ).any(),
            axis=1,
        )

        filtered_df = filtered_df[mask]

    st.write(
        f"조회 결과: **{len(filtered_df):,}건**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = (
        filtered_df.to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        "📥 조회 결과 CSV 다운로드",
        data=csv_data,
        file_name="정기예금_조회결과.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# 3. 데이터 등록 CREATE
# ============================================================

elif menu == "➕ 데이터 등록":

    st.title("➕ 정기예금 데이터 등록")

    st.caption(
        "현재 CSV 컬럼 구조에 맞춰 새로운 데이터를 추가합니다."
    )

    if len(df.columns) == 0:
        st.warning("등록할 CSV 컬럼이 없습니다.")
        st.stop()

    new_values = {}

    with st.form("create_form"):

        columns = st.columns(2)

        for i, column in enumerate(df.columns):

            target_column = columns[i % 2]

            with target_column:

                new_values[column] = st.text_input(
                    column,
                    key=f"create_{column}",
                )

        submitted = st.form_submit_button(
            "💾 데이터 등록",
            use_container_width=True,
        )

    if submitted:

        new_row = pd.DataFrame(
            [new_values]
        )

        updated_df = pd.concat(
            [
                df,
                new_row,
            ],
            ignore_index=True,
        )

        if save_data(updated_df):

            st.success(
                "새 데이터가 등록되었습니다."
            )

            st.rerun()


# ============================================================
# 4. 데이터 수정 UPDATE
# ============================================================

elif menu == "✏️ 데이터 수정":

    st.title("✏️ 정기예금 데이터 수정")

    if df.empty:

        st.info(
            "수정할 데이터가 없습니다."
        )

    else:

        options = {
            make_row_label(df, i): i
            for i in df.index
        }

        selected_label = st.selectbox(
            "수정할 데이터를 선택하세요.",
            list(options.keys()),
        )

        row_index = options[selected_label]

        selected_row = df.loc[row_index]

        st.write("#### 현재 선택한 데이터")

        st.dataframe(
            df.loc[[row_index]],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        edit_values = {}

        with st.form("update_form"):

            columns = st.columns(2)

            for i, column in enumerate(df.columns):

                target_column = columns[i % 2]

                with target_column:

                    edit_values[column] = st.text_input(
                        column,
                        value=str(
                            selected_row[column]
                        ),
                        key=f"edit_{column}",
                    )

            submitted = st.form_submit_button(
                "💾 변경사항 저장",
                use_container_width=True,
            )

        if submitted:

            for column in df.columns:

                df.at[
                    row_index,
                    column,
                ] = edit_values[column]

            if save_data(df):

                st.success(
                    "데이터가 수정되었습니다."
                )

                st.rerun()


# ============================================================
# 5. 데이터 삭제 DELETE
# ============================================================

elif menu == "🗑️ 데이터 삭제":

    st.title("🗑️ 정기예금 데이터 삭제")

    if df.empty:

        st.info(
            "삭제할 데이터가 없습니다."
        )

    else:

        options = {
            make_row_label(df, i): i
            for i in df.index
        }

        selected_label = st.selectbox(
            "삭제할 데이터를 선택하세요.",
            list(options.keys()),
        )

        row_index = options[selected_label]

        st.write("#### 삭제 대상")

        st.dataframe(
            df.loc[[row_index]],
            use_container_width=True,
            hide_index=True,
        )

        st.warning(
            "선택한 데이터를 CSV 파일에서 삭제합니다."
        )

        confirm = st.checkbox(
            "위 데이터를 삭제하는 것에 동의합니다."
        )

        if st.button(
            "🗑️ 데이터 삭제",
            type="primary",
            disabled=not confirm,
            use_container_width=True,
        ):

            updated_df = (
                df
                .drop(index=row_index)
                .reset_index(drop=True)
            )

            if save_data(updated_df):

                st.success(
                    "데이터가 삭제되었습니다."
                )

                st.rerun()


# ============================================================
# 6. 금리 분석
# ============================================================

elif menu == "📈 금리 분석":

    st.title("📈 정기예금 금리 분석")

    numeric_candidates = []

    for column in df.columns:

        converted = numeric_series(
            df,
            column,
        )

        if converted.notna().sum() > 0:

            numeric_candidates.append(
                column
            )

    if not numeric_candidates:

        st.warning(
            "숫자로 분석할 수 있는 컬럼을 찾지 못했습니다."
        )

    else:

        selected_column = st.selectbox(
            "분석할 금리 컬럼",
            numeric_candidates,
        )

        values = numeric_series(
            df,
            selected_column,
        )

        valid_values = values.dropna()

        if valid_values.empty:

            st.warning(
                "선택한 컬럼에서 숫자 데이터를 찾지 못했습니다."
            )

        else:

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "평균",
                f"{valid_values.mean():.2f}",
            )

            col2.metric(
                "최고",
                f"{valid_values.max():.2f}",
            )

            col3.metric(
                "최저",
                f"{valid_values.min():.2f}",
            )

            col4.metric(
                "최고-최저 차이",
                f"{valid_values.max() - valid_values.min():.2f}",
            )

            st.divider()

            st.subheader(
                f"📊 {selected_column} 비교"
            )

            chart_df = df.copy()

            chart_df["_분석값"] = values

            chart_df = chart_df.dropna(
                subset=["_분석값"]
            )

            if len(df.columns) > 0:

                label_column = df.columns[0]

                chart_data = chart_df[
                    [
                        label_column,
                        "_분석값",
                    ]
                ].copy()

                chart_data = chart_data.set_index(
                    label_column
                )

                st.bar_chart(
                    chart_data
                )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "🔺 최고 금리 데이터"
                )

                max_value = valid_values.max()

                max_rows = df[
                    values == max_value
                ]

                st.dataframe(
                    max_rows,
                    use_container_width=True,
                    hide_index=True,
                )

            with col2:

                st.subheader(
                    "🔻 최저 금리 데이터"
                )

                min_value = valid_values.min()

                min_rows = df[
                    values == min_value
                ]

                st.dataframe(
                    min_rows,
                    use_container_width=True,
                    hide_index=True,
                )


# ============================================================
# 7. 원본 데이터
# ============================================================

elif menu == "📋 원본 데이터":

    st.title("📋 원본 CSV 데이터")

    st.write(
        f"현재 CSV에 **{len(df):,}건**의 데이터가 있습니다."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    csv_data = (
        df.to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        "📥 전체 CSV 다운로드",
        data=csv_data,
        file_name=CSV_FILE,
        mime="text/csv",
        use_container_width=True,
    )
