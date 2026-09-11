import streamlit as st
import pandas as pd
import requests


# ============================================================
# Streamlit 기본 설정
# ============================================================
st.set_page_config(
    page_title="조합원 CRUD 관리",
    page_icon="👥",
    layout="wide"
)

TABLE_NAME = "members"


# ============================================================
# Secrets 읽기
# ============================================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip("/")
    SUPABASE_KEY = st.secrets["SUPABASE_SECRET_KEY"]

    ADMIN_ID = st.secrets.get("ADMIN_ID", "017")
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "2026")

except Exception:
    st.error(
        "Streamlit Secrets 설정을 확인해주세요.\n\n"
        "SUPABASE_URL과 SUPABASE_SECRET_KEY가 필요합니다."
    )
    st.stop()


# ============================================================
# Supabase REST API 설정
# ============================================================
API_URL = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# ============================================================
# API 에러 처리
# ============================================================
def check_response(response):
    if response.ok:
        return

    try:
        error_data = response.json()
        message = error_data.get(
            "message",
            response.text
        )
    except Exception:
        message = response.text

    raise Exception(
        f"Supabase API 오류 "
        f"({response.status_code}) : {message}"
    )


# ============================================================
# CRUD 함수
# ============================================================
def get_members():

    params = {
        "select": "*",
        "order": "id.asc"
    }

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params=params,
        timeout=20
    )

    check_response(response)

    return response.json()


def add_member(data):

    headers = {
        **HEADERS,
        "Prefer": "return=representation"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=20
    )

    check_response(response)

    return response.json()


def update_member(member_id, data):

    headers = {
        **HEADERS,
        "Prefer": "return=representation"
    }

    params = {
        "id": f"eq.{member_id}"
    }

    response = requests.patch(
        API_URL,
        headers=headers,
        params=params,
        json=data,
        timeout=20
    )

    check_response(response)

    return response.json()


def delete_member(member_id):

    headers = {
        **HEADERS,
        "Prefer": "return=representation"
    }

    params = {
        "id": f"eq.{member_id}"
    }

    response = requests.delete(
        API_URL,
        headers=headers,
        params=params,
        timeout=20
    )

    check_response(response)

    return response.json()


# ============================================================
# 로그인
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def login():

    st.title("🔐 조합원 관리 시스템")

    st.write(
        "관리자 계정으로 로그인해주세요."
    )

    with st.form("login_form"):

        user_id = st.text_input(
            "관리자 ID"
        )

        password = st.text_input(
            "비밀번호",
            type="password"
        )

        login_button = st.form_submit_button(
            "로그인",
            use_container_width=True
        )

    if login_button:

        if (
            user_id == ADMIN_ID
            and password == ADMIN_PASSWORD
        ):

            st.session_state.authenticated = True

            st.rerun()

        else:

            st.error(
                "ID 또는 비밀번호가 올바르지 않습니다."
            )


if not st.session_state.authenticated:

    login()

    st.stop()


# ============================================================
# 사이드바
# ============================================================
with st.sidebar:

    st.title("👥 조합원 관리")

    menu = st.radio(
        "메뉴 선택",
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

    if st.button(
        "🚪 로그아웃",
        use_container_width=True
    ):

        st.session_state.authenticated = False

        st.rerun()


# ============================================================
# Supabase 연결 테스트 및 데이터 조회
# ============================================================
try:

    members = get_members()

    df = pd.DataFrame(members)

except Exception as e:

    st.error(
        "Supabase 데이터 조회에 실패했습니다."
    )

    st.code(str(e))

    st.info(
        """
확인할 항목

1. SUPABASE_URL
2. SUPABASE_SECRET_KEY
3. members 테이블 존재 여부
4. Data API 설정
5. 테이블 권한
"""
    )

    st.stop()


# ============================================================
# Dashboard
# ============================================================
if menu == "📊 대시보드":

    st.title(
        "📊 조합원 관리 대시보드"
    )

    st.caption(
        "Supabase REST API 실시간 연결"
    )

    col1, col2, col3 = st.columns(3)

    total = len(df)

    normal = 0
    inactive = 0

    if (
        not df.empty
        and "status" in df.columns
    ):

        normal = len(
            df[
                df["status"]
                .fillna("")
                .astype(str)
                == "정상"
            ]
        )

        inactive = total - normal

    col1.metric(
        "전체 조합원",
        f"{total:,}명"
    )

    col2.metric(
        "정상 조합원",
        f"{normal:,}명"
    )

    col3.metric(
        "기타 상태",
        f"{inactive:,}명"
    )

    st.divider()

    st.subheader(
        "조합원 현황"
    )

    if df.empty:

        st.info(
            "등록된 조합원이 없습니다."
        )

    else:

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
        "검색",
        placeholder=(
            "이름, 조합원번호, 연락처, "
            "소속 금고 등을 입력하세요."
        )
    )

    filtered_df = df.copy()

    if (
        search
        and not df.empty
    ):

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
        f"조회 결과: "
        f"**{len(filtered_df):,}명**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    if not filtered_df.empty:

        csv = filtered_df.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            "📥 CSV 다운로드",
            data=csv,
            file_name="members.csv",
            mime="text/csv"
        )


# ============================================================
# 등록
# ============================================================
elif menu == "➕ 조합원 등록":

    st.title(
        "➕ 조합원 등록"
    )

    with st.form(
        "member_add_form"
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
                [
                    "정상",
                    "휴면",
                    "탈퇴"
                ]
            )

        submitted = st.form_submit_button(
            "💾 조합원 등록",
            use_container_width=True
        )

    if submitted:

        if (
            not member_no.strip()
            or not name.strip()
        ):

            st.warning(
                "조합원 번호와 성명은 필수입니다."
            )

        else:

            data = {
                "member_no": member_no.strip(),
                "name": name.strip(),
                "branch": branch.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "status": status
            }

            try:

                add_member(data)

                st.success(
                    f"{name} 조합원이 "
                    "등록되었습니다."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "등록에 실패했습니다."
                )

                st.code(str(e))


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

    elif (
        "id" not in df.columns
        or "name" not in df.columns
    ):

        st.error(
            "members 테이블에 "
            "id와 name 컬럼이 필요합니다."
        )

    else:

        member_options = {}

        for _, row in df.iterrows():

            label = (
                f"{row['id']} | "
                f"{row.get('name', '')}"
            )

            member_options[label] = row["id"]

        selected_label = st.selectbox(
            "수정할 조합원",
            list(member_options.keys())
        )

        member_id = member_options[
            selected_label
        ]

        member = df[
            df["id"] == member_id
        ].iloc[0]

        with st.form(
            "member_update_form"
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
                    "성명",
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

                current_status = str(
                    member.get(
                        "status",
                        "정상"
                    ) or "정상"
                )

                if (
                    current_status
                    not in status_options
                ):
                    status_options.insert(
                        0,
                        current_status
                    )

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

            data = {
                "member_no": member_no.strip(),
                "name": name.strip(),
                "branch": branch.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "status": status
            }

            try:

                update_member(
                    member_id,
                    data
                )

                st.success(
                    "조합원 정보가 "
                    "수정되었습니다."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "수정에 실패했습니다."
                )

                st.code(str(e))


# ============================================================
# 삭제
# ============================================================
elif menu == "🗑️ 조합원 삭제":

    st.title(
        "🗑️ 조합원 삭제"
    )

    st.warning(
        "삭제된 데이터는 복구하기 어렵습니다."
    )

    if df.empty:

        st.info(
            "등록된 조합원이 없습니다."
        )

    elif (
        "id" not in df.columns
        or "name" not in df.columns
    ):

        st.error(
            "members 테이블에 "
            "id와 name 컬럼이 필요합니다."
        )

    else:

        member_options = {}

        for _, row in df.iterrows():

            label = (
                f"{row['id']} | "
                f"{row.get('name', '')}"
            )

            member_options[label] = row["id"]

        selected_label = st.selectbox(
            "삭제할 조합원",
            list(member_options.keys())
        )

        member_id = member_options[
            selected_label
        ]

        member = df[
            df["id"] == member_id
        ]

        st.subheader(
            "삭제 대상"
        )

        st.dataframe(
            member,
            use_container_width=True,
            hide_index=True
        )

        confirm = st.checkbox(
            "위 조합원 정보를 삭제하겠습니다."
        )

        if st.button(
            "🗑️ 삭제",
            type="primary",
            disabled=not confirm,
            use_container_width=True
        ):

            try:

                delete_member(
                    member_id
                )

                st.success(
                    "조합원 정보가 "
                    "삭제되었습니다."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "삭제에 실패했습니다."
                )

                st.code(str(e))
