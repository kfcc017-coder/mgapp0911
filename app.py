import streamlit as st
import pandas as pd
from supabase import create_client, Client


# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="조합원 관리 시스템",
    page_icon="👥",
    layout="wide"
)

TABLE_NAME = "members"


# =========================================================
# Supabase 연결
# =========================================================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SECRET_KEY"]

    return create_client(url, key)


try:
    supabase = init_supabase()

except Exception as e:
    st.error("Supabase 연결 설정을 확인해주세요.")
    st.exception(e)
    st.stop()


# =========================================================
# 관리자 로그인
# =========================================================
def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 조합원 관리 시스템")

    st.caption("관리자 로그인이 필요합니다.")

    with st.form("login_form"):
        login_id = st.text_input("관리자 ID")
        login_pw = st.text_input(
            "비밀번호",
            type="password"
        )

        submit = st.form_submit_button(
            "로그인",
            use_container_width=True
        )

    if submit:

        admin_id = st.secrets["ADMIN_ID"]
        admin_pw = st.secrets["ADMIN_PASSWORD"]

        if login_id == admin_id and login_pw == admin_pw:

            st.session_state.authenticated = True
            st.rerun()

        else:
            st.error("ID 또는 비밀번호가 올바르지 않습니다.")

    return False


if not login():
    st.stop()


# =========================================================
# 데이터 처리 함수
# =========================================================
def get_members():

    response = (
        supabase
        .table(TABLE_NAME)
        .select("*")
        .order("id")
        .execute()
    )

    return response.data


def add_member(data):

    return (
        supabase
        .table(TABLE_NAME)
        .insert(data)
        .execute()
    )


def update_member(member_id, data):

    return (
        supabase
        .table(TABLE_NAME)
        .update(data)
        .eq("id", member_id)
        .execute()
    )


def delete_member(member_id):

    return (
        supabase
        .table(TABLE_NAME)
        .delete()
        .eq("id", member_id)
        .execute()
    )


# =========================================================
# 사이드바
# =========================================================
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

    if st.button(
        "로그아웃",
        use_container_width=True
    ):
        st.session_state.authenticated = False
        st.rerun()


# =========================================================
# 데이터 로딩
# =========================================================
try:

    members = get_members()

except Exception as e:

    st.error("조합원 데이터를 불러올 수 없습니다.")
    st.exception(e)
    st.stop()


df = pd.DataFrame(members)


# =========================================================
# 대시보드
# =========================================================
if menu == "📊 대시보드":

    st.title("📊 조합원 관리 대시보드")

    st.caption(
        "Supabase 데이터베이스와 실시간으로 연결되어 있습니다."
    )

    col1, col2, col3 = st.columns(3)

    total_members = len(df)

    if not df.empty and "status" in df.columns:

        active_members = len(
            df[df["status"] == "정상"]
        )

        inactive_members = total_members - active_members

    else:
        active_members = 0
        inactive_members = 0

    col1.metric(
        "전체 조합원",
        f"{total_members:,}명"
    )

    col2.metric(
        "정상",
        f"{active_members:,}명"
    )

    col3.metric(
        "기타",
        f"{inactive_members:,}명"
    )

    st.divider()

    st.subheader("최근 조합원")

    if not df.empty:

        st.dataframe(
            df.tail(10),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("등록된 조합원이 없습니다.")


# =========================================================
# 조회
# =========================================================
elif menu == "🔍 조합원 조회":

    st.title("🔍 조합원 조회")

    search = st.text_input(
        "조합원 검색",
        placeholder="이름, 조합원번호, 연락처 등을 입력하세요."
    )

    filtered_df = df.copy()

    if search and not df.empty:

        mask = (
            df.astype(str)
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

        filtered_df = df[mask]

    st.write(
        f"조회 결과 : **{len(filtered_df):,}명**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name="members.csv",
        mime="text/csv"
    )


# =========================================================
# 등록
# =========================================================
elif menu == "➕ 조합원 등록":

    st.title("➕ 조합원 등록")

    with st.form(
        "add_member_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            member_no = st.text_input(
                "조합원 번호 *"
            )

            name = st.text_input(
                "이름 *"
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
                [
                    "정상",
                    "휴면",
                    "탈퇴"
                ]
            )

        submitted = st.form_submit_button(
            "조합원 등록",
            use_container_width=True
        )

    if submitted:

        if not member_no or not name:

            st.warning(
                "조합원 번호와 이름은 필수입니다."
            )

        else:

            data = {
                "member_no": member_no,
                "name": name,
                "branch": branch,
                "phone": phone,
                "email": email,
                "status": status
            }

            try:

                add_member(data)

                st.success(
                    f"{name} 조합원이 등록되었습니다."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "등록 중 오류가 발생했습니다."
                )

                st.exception(e)


# =========================================================
# 수정
# =========================================================
elif menu == "✏️ 조합원 수정":

    st.title("✏️ 조합원 수정")

    if df.empty:

        st.info(
            "수정할 조합원이 없습니다."
        )

    else:

        # 표시용 이름 생성
        df["display_name"] = (
            df["id"].astype(str)
            + " | "
            + df["name"].fillna("")
        )

        selected = st.selectbox(
            "수정할 조합원",
            df["display_name"].tolist()
        )

        selected_id = int(
            selected.split("|")[0].strip()
        )

        member = df[
            df["id"] == selected_id
        ].iloc[0]

        with st.form(
            "update_member_form"
        ):

            col1, col2 = st.columns(2)

            with col1:

                member_no = st.text_input(
                    "조합원 번호",
                    value=str(
                        member.get(
                            "member_no",
                            ""
                        ) or ""
                    )
                )

                name = st.text_input(
                    "이름",
                    value=str(
                        member.get(
                            "name",
                            ""
                        ) or ""
                    )
                )

                branch = st.text_input(
                    "소속 금고",
                    value=str(
                        member.get(
                            "branch",
                            ""
                        ) or ""
                    )
                )

            with col2:

                phone = st.text_input(
                    "연락처",
                    value=str(
                        member.get(
                            "phone",
                            ""
                        ) or ""
                    )
                )

                email = st.text_input(
                    "이메일",
                    value=str(
                        member.get(
                            "email",
                            ""
                        ) or ""
                    )
                )

                status_options = [
                    "정상",
                    "휴면",
                    "탈퇴"
                ]

                current_status = (
                    member.get(
                        "status",
                        "정상"
                    )
                    or "정상"
                )

                try:

                    status_index = (
                        status_options.index(
                            current_status
                        )
                    )

                except ValueError:

                    status_index = 0

                status = st.selectbox(
                    "상태",
                    status_options,
                    index=status_index
                )

            submitted = (
                st.form_submit_button(
                    "변경사항 저장",
                    use_container_width=True
                )
            )

        if submitted:

            update_data = {
                "member_no": member_no,
                "name": name,
                "branch": branch,
                "phone": phone,
                "email": email,
                "status": status
            }

            try:

                update_member(
                    selected_id,
                    update_data
                )

                st.success(
                    "조합원 정보가 수정되었습니다."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "수정 중 오류가 발생했습니다."
                )

                st.exception(e)


# =========================================================
# 삭제
# =========================================================
elif menu == "🗑️ 조합원 삭제":

    st.title("🗑️ 조합원 삭제")

    st.warning(
        "삭제한 조합원 정보는 복구할 수 없습니다."
    )

    if df.empty:

        st.info(
            "삭제할 조합원이 없습니다."
        )

    else:

        df["display_name"] = (
            df["id"].astype(str)
            + " | "
            + df["name"].fillna("")
        )

        selected = st.selectbox(
            "삭제할 조합원",
            df["display_name"].tolist()
        )

        selected_id = int(
            selected.split("|")[0].strip()
        )

        member = df[
            df["id"] == selected_id
        ].iloc[0]

        st.write("### 삭제 대상")

        st.dataframe(
            pd.DataFrame(
                [member.drop(
                    labels=["display_name"],
                    errors="ignore"
                )]
            ),
            use_container_width=True,
            hide_index=True
        )

        confirm = st.checkbox(
            "위 조합원을 삭제하는 것에 동의합니다."
        )

        if st.button(
            "조합원 삭제",
            type="primary",
            disabled=not confirm,
            use_container_width=True
        ):

            try:

                delete_member(
                    selected_id
                )

                st.success(
                    "조합원이 삭제되었습니다."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "삭제 중 오류가 발생했습니다."
                )

                st.exception(e)
