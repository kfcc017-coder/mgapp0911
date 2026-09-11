import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="조합원 CRUD 대시보드",
    page_icon="👥",
    layout="wide"
)


# ============================
# 초기 샘플 데이터
# ============================
if "members" not in st.session_state:
    st.session_state.members = [
        {
            "id": 1,
            "member_no": "M001",
            "name": "홍길동",
            "branch": "서울중앙금고",
            "phone": "010-1234-5678",
            "email": "hong@example.com",
            "status": "정상"
        },
        {
            "id": 2,
            "member_no": "M002",
            "name": "김민수",
            "branch": "강남금고",
            "phone": "010-2222-3333",
            "email": "kim@example.com",
            "status": "정상"
        },
        {
            "id": 3,
            "member_no": "M003",
            "name": "이영희",
            "branch": "서초금고",
            "phone": "010-5555-7777",
            "email": "lee@example.com",
            "status": "휴면"
        }
    ]


def get_df():
    return pd.DataFrame(st.session_state.members)


# ============================
# 사이드바
# ============================
with st.sidebar:
    st.title("👥 조합원 관리")

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

    st.caption("Demo Mode")
    st.info(
        "현재는 Supabase와 연결하지 않은 "
        "Streamlit 데모 버전입니다."
    )


df = get_df()


# ============================
# 대시보드
# ============================
if menu == "📊 대시보드":

    st.title("📊 조합원 관리 대시보드")

    st.caption(
        "Supabase 연결 없이 동작하는 Demo Dashboard"
    )

    total = len(df)

    if not df.empty:
        normal = len(df[df["status"] == "정상"])
        dormant = len(df[df["status"] == "휴면"])
        withdrawn = len(df[df["status"] == "탈퇴"])
    else:
        normal = dormant = withdrawn = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("전체 조합원", f"{total:,}명")
    col2.metric("정상", f"{normal:,}명")
    col3.metric("휴면", f"{dormant:,}명")
    col4.metric("탈퇴", f"{withdrawn:,}명")

    st.divider()

    st.subheader("전체 조합원 현황")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================
# 조회
# ============================
elif menu == "🔍 조합원 조회":

    st.title("🔍 조합원 조회")

    search = st.text_input(
        "검색",
        placeholder="이름, 조합원번호, 금고명, 연락처 등을 입력하세요."
    )

    filtered_df = df.copy()

    if search and not df.empty:

        mask = df.astype(str).apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False
            ).any(),
            axis=1
        )

        filtered_df = df[mask]

    st.write(
        f"조회 결과: **{len(filtered_df)}명**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    if not filtered_df.empty:

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 CSV 다운로드",
            data=csv,
            file_name="members.csv",
            mime="text/csv"
        )


# ============================
# 등록
# ============================
elif menu == "➕ 조합원 등록":

    st.title("➕ 조합원 등록")

    with st.form(
        "add_member",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:
            member_no = st.text_input(
                "조합원 번호 *"
            )

            name = st.text_input(
                "성명 *"
            )

            branch = st.text_input(
                "소속 금고"
            )

        with col2:
            phone = st.text_input(
                "연락처"
            )

            email = st.text_input(
                "이메일"
            )

            status = st.selectbox(
                "상태",
                ["정상", "휴면", "탈퇴"]
            )

        submitted = st.form_submit_button(
            "💾 등록",
            use_container_width=True
        )

    if submitted:

        if not member_no or not name:

            st.warning(
                "조합원 번호와 성명은 필수입니다."
            )

        else:

            if st.session_state.members:
                new_id = max(
                    m["id"]
                    for m in st.session_state.members
                ) + 1
            else:
                new_id = 1

            new_member = {
                "id": new_id,
                "member_no": member_no,
                "name": name,
                "branch": branch,
                "phone": phone,
                "email": email,
                "status": status
            }

            st.session_state.members.append(
                new_member
            )

            st.success(
                f"{name} 조합원이 등록되었습니다."
            )

            st.rerun()


# ============================
# 수정
# ============================
elif menu == "✏️ 조합원 수정":

    st.title("✏️ 조합원 수정")

    if df.empty:

        st.info(
            "등록된 조합원이 없습니다."
        )

    else:

        options = {
            f"{row['id']} | {row['name']}": row["id"]
            for _, row in df.iterrows()
        }

        selected = st.selectbox(
            "수정할 조합원",
            list(options.keys())
        )

        selected_id = options[selected]

        member = next(
            m
            for m in st.session_state.members
            if m["id"] == selected_id
        )

        with st.form("update_member"):

            col1, col2 = st.columns(2)

            with col1:

                member_no = st.text_input(
                    "조합원 번호",
                    value=member["member_no"]
                )

                name = st.text_input(
                    "성명",
                    value=member["name"]
                )

                branch = st.text_input(
                    "소속 금고",
                    value=member["branch"]
                )

            with col2:

                phone = st.text_input(
                    "연락처",
                    value=member["phone"]
                )

                email = st.text_input(
                    "이메일",
                    value=member["email"]
                )

                status_options = [
                    "정상",
                    "휴면",
                    "탈퇴"
                ]

                status = st.selectbox(
                    "상태",
                    status_options,
                    index=status_options.index(
                        member["status"]
                    )
                )

            submitted = st.form_submit_button(
                "💾 변경사항 저장",
                use_container_width=True
            )

        if submitted:

            member["member_no"] = member_no
            member["name"] = name
            member["branch"] = branch
            member["phone"] = phone
            member["email"] = email
            member["status"] = status

            st.success(
                "조합원 정보가 수정되었습니다."
            )

            st.rerun()


# ============================
# 삭제
# ============================
elif menu == "🗑️ 조합원 삭제":

    st.title("🗑️ 조합원 삭제")

    if df.empty:

        st.info(
            "등록된 조합원이 없습니다."
        )

    else:

        options = {
            f"{row['id']} | {row['name']}": row["id"]
            for _, row in df.iterrows()
        }

        selected = st.selectbox(
            "삭제할 조합원",
            list(options.keys())
        )

        selected_id = options[selected]

        selected_df = df[
            df["id"] == selected_id
        ]

        st.dataframe(
            selected_df,
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "삭제 후에는 현재 세션에서 해당 데이터가 제거됩니다."
        )

        confirm = st.checkbox(
            "삭제에 동의합니다."
        )

        if st.button(
            "🗑️ 삭제",
            type="primary",
            disabled=not confirm,
            use_container_width=True
        ):

            st.session_state.members = [
                member
                for member in st.session_state.members
                if member["id"] != selected_id
            ]

            st.success(
                "조합원이 삭제되었습니다."
            )

            st.rerun()
