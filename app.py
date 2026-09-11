import streamlit as st
import pandas as pd
import os

# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="조합원 CRUD 대시보드",
    page_icon="👥",
    layout="wide"
)

CSV_FILE = "members.csv"


# ============================================================
# CSV 데이터 관리 함수
# ============================================================

def load_data():

    if os.path.exists(CSV_FILE):

        try:
            df = pd.read_csv(
                CSV_FILE,
                dtype={
                    "member_no": str,
                    "phone": str
                }
            )

            return df

        except Exception as e:

            st.error(
                f"CSV 파일을 읽는 중 오류가 발생했습니다.\n\n{e}"
            )

            return pd.DataFrame()

    else:

        st.error(
            "members.csv 파일을 찾을 수 없습니다."
        )

        return pd.DataFrame()


def save_data(df):

    try:

        df.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        return True

    except Exception as e:

        st.error(
            f"CSV 저장 중 오류가 발생했습니다.\n\n{e}"
        )

        return False


# ============================================================
# 데이터 불러오기
# ============================================================

df = load_data()


# ============================================================
# 사이드바
# ============================================================

with st.sidebar:

    st.title("👥 조합원 관리")

    st.caption(
        "CSV 기반 CRUD Dashboard"
    )

    st.divider()

    menu = st.radio(
        "메뉴",
        [
            "📊 대시보드",
            "🔍 조합원 조회",
            "➕ 조합원 등록",
            "✏️ 조합원 수정",
            "🗑️ 조합원 삭제"
        ]
    )

    st.divider()

    if st.button(
        "🔄 데이터 새로고침",
        use_container_width=True
    ):

        st.rerun()

    st.info(
        "현재 데이터는 members.csv 파일을 기준으로 표시됩니다."
    )


# ============================================================
# Dashboard
# ============================================================

if menu == "📊 대시보드":

    st.title(
        "📊 조합원 관리 대시보드"
    )

    st.caption(
        "GitHub CSV 파일 기반 조합원 CRUD 관리"
    )

    if df.empty:

        st.warning(
            "등록된 조합원이 없습니다."
        )

    else:

        total = len(df)

        normal = len(
            df[
                df["status"]
                .fillna("")
                .astype(str)
                == "정상"
            ]
        )

        dormant = len(
            df[
                df["status"]
                .fillna("")
                .astype(str)
                == "휴면"
            ]
        )

        withdrawn = len(
            df[
                df["status"]
                .fillna("")
                .astype(str)
                == "탈퇴"
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "전체 조합원",
            f"{total:,}명"
        )

        col2.metric(
            "정상",
            f"{normal:,}명"
        )

        col3.metric(
            "휴면",
            f"{dormant:,}명"
        )

        col4.metric(
            "탈퇴",
            f"{withdrawn:,}명"
        )

        st.divider()

        # ----------------------------------------
        # 금고별 조합원 현황
        # ----------------------------------------

        st.subheader(
            "🏦 금고별 조합원 현황"
        )

        if "branch" in df.columns:

            branch_count = (
                df["branch"]
                .fillna("미지정")
                .value_counts()
            )

            st.bar_chart(
                branch_count
            )

        st.divider()

        # ----------------------------------------
        # 조합원 목록
        # ----------------------------------------

        st.subheader(
            "👥 전체 조합원"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 조회
# ============================================================

elif menu == "🔍 조합원 조회":

    st.title(
        "🔍 조합원 조회"
    )

    search = st.text_input(
        "통합 검색",
        placeholder=(
            "이름, 조합원번호, "
            "금고명, 연락처 등을 입력하세요."
        )
    )

    status_filter = st.selectbox(
        "상태",
        [
            "전체",
            "정상",
            "휴면",
            "탈퇴"
        ]
    )

    filtered_df = df.copy()

    # ----------------------------------------
    # 검색어
    # ----------------------------------------

    if search and not filtered_df.empty:

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

    # ----------------------------------------
    # 상태 필터
    # ----------------------------------------

    if (
        status_filter != "전체"
        and not filtered_df.empty
    ):

        filtered_df = filtered_df[
            filtered_df["status"]
            == status_filter
        ]

    st.write(
        f"조회 결과: **{len(filtered_df):,}명**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------
    # CSV 다운로드
    # ----------------------------------------

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
        file_name="member_search_result.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# 등록
# ============================================================

elif menu == "➕ 조합원 등록":

    st.title(
        "➕ 조합원 등록"
    )

    with st.form(
        "add_member_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            member_no = st.text_input(
                "조합원 번호 *",
                placeholder="예: M006"
            )

            name = st.text_input(
                "성명 *"
            )

            branch = st.text_input(
                "소속 금고"
            )

        with col2:

            phone = st.text_input(
                "연락처",
                placeholder="010-0000-0000"
            )

            email = st.text_input(
                "이메일"
            )

            status = st.selectbox(
                "상태",
                [
                    "정상",
                    "휴면",
                    "탈퇴"
                ]
            )

        submitted = (
            st.form_submit_button(
                "💾 조합원 등록",
                use_container_width=True
            )
        )

    if submitted:

        # ----------------------------------------
        # 필수값 확인
        # ----------------------------------------

        if (
            not member_no.strip()
            or not name.strip()
        ):

            st.warning(
                "조합원 번호와 성명은 필수입니다."
            )

        elif (
            not df.empty
            and member_no
            in df["member_no"].astype(str).values
        ):

            st.error(
                "이미 등록된 조합원 번호입니다."
            )

        else:

            # ----------------------------------------
            # ID 자동 생성
            # ----------------------------------------

            if df.empty:

                new_id = 1

            else:

                new_id = (
                    pd.to_numeric(
                        df["id"],
                        errors="coerce"
                    )
                    .fillna(0)
                    .max()
                    + 1
                )

                new_id = int(
                    new_id
                )

            new_member = pd.DataFrame(
                [
                    {
                        "id": new_id,
                        "member_no": member_no.strip(),
                        "name": name.strip(),
                        "branch": branch.strip(),
                        "phone": phone.strip(),
                        "email": email.strip(),
                        "status": status
                    }
                ]
            )

            new_df = pd.concat(
                [
                    df,
                    new_member
                ],
                ignore_index=True
            )

            if save_data(
                new_df
            ):

                st.success(
                    f"{name} 조합원이 등록되었습니다."
                )

                st.rerun()


# ============================================================
# 수정
# ============================================================

elif menu == "✏️ 조합원 수정":

    st.title(
        "✏️ 조합원 수정"
    )

    if df.empty:

        st.info(
            "등록된 조합원이 없습니다."
        )

    else:

        options = {}

        for index, row in df.iterrows():

            label = (
                f"{row['member_no']} | "
                f"{row['name']} | "
                f"{row['branch']}"
            )

            options[
                label
            ] = index

        selected = st.selectbox(
            "수정할 조합원",
            list(
                options.keys()
            )
        )

        row_index = options[
            selected
        ]

        member = df.loc[
            row_index
        ]

        with st.form(
            "update_member_form"
        ):

            col1, col2 = st.columns(2)

            with col1:

                member_no = st.text_input(
                    "조합원 번호",
                    value=str(
                        member["member_no"]
                    )
                )

                name = st.text_input(
                    "성명",
                    value=str(
                        member["name"]
                    )
                )

                branch = st.text_input(
                    "소속 금고",
                    value=str(
                        member["branch"]
                    )
                )

            with col2:

                phone = st.text_input(
                    "연락처",
                    value=str(
                        member["phone"]
                    )
                )

                email = st.text_input(
                    "이메일",
                    value=str(
                        member["email"]
                    )
                )

                status_options = [
                    "정상",
                    "휴면",
                    "탈퇴"
                ]

                current_status = str(
                    member["status"]
                )

                if (
                    current_status
                    not in status_options
                ):

                    current_status = "정상"

                status = st.selectbox(
                    "상태",
                    status_options,
                    index=status_options.index(
                        current_status
                    )
                )

            submitted = (
                st.form_submit_button(
                    "💾 변경사항 저장",
                    use_container_width=True
                )
            )

        if submitted:

            df.at[
                row_index,
                "member_no"
            ] = member_no.strip()

            df.at[
                row_index,
                "name"
            ] = name.strip()

            df.at[
                row_index,
                "branch"
            ] = branch.strip()

            df.at[
                row_index,
                "phone"
            ] = phone.strip()

            df.at[
                row_index,
                "email"
            ] = email.strip()

            df.at[
                row_index,
                "status"
            ] = status

            if save_data(df):

                st.success(
                    "조합원 정보가 수정되었습니다."
                )

                st.rerun()


# ============================================================
# 삭제
# ============================================================

elif menu == "🗑️ 조합원 삭제":

    st.title(
        "🗑️ 조합원 삭제"
    )

    if df.empty:

        st.info(
            "등록된 조합원이 없습니다."
        )

    else:

        options = {}

        for index, row in df.iterrows():

            label = (
                f"{row['member_no']} | "
                f"{row['name']} | "
                f"{row['branch']}"
            )

            options[
                label
            ] = index

        selected = st.selectbox(
            "삭제할 조합원",
            list(
                options.keys()
            )
        )

        row_index = options[
            selected
        ]

        member = df.loc[
            [
                row_index
            ]
        ]

        st.write(
            "### 삭제 대상"
        )

        st.dataframe(
            member,
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "선택한 조합원을 삭제하시겠습니까?"
        )

        confirm = st.checkbox(
            "삭제에 동의합니다."
        )

        if st.button(
            "🗑️ 조합원 삭제",
            type="primary",
            disabled=not confirm,
            use_container_width=True
        ):

            new_df = (
                df
                .drop(
                    index=row_index
                )
                .reset_index(
                    drop=True
                )
            )

            if save_data(
                new_df
            ):

                st.success(
                    "조합원이 삭제되었습니다."
                )

                st.rerun()
