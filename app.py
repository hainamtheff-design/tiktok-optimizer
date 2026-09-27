import streamlit as st
from urllib.parse import urlparse
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="TeaHack TikTok Promote Builder",
    page_icon="🚀",
    layout="wide"
)

# ============================================================
# CONSTANTS
# ============================================================

PROMOTE_HELP_URL = (
    "https://ads.tiktok.com/resources/help/article/"
    "how-to-find-promote-in-app-and-on-web?lang=vi"
)

if "campaigns" not in st.session_state:
    st.session_state.campaigns = []


# ============================================================
# HELPERS
# ============================================================

def valid_tiktok_url(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())

        if parsed.scheme not in ("http", "https"):
            return False

        host = parsed.netloc.lower().split(":")[0]

        return (
            host == "tiktok.com"
            or host.endswith(".tiktok.com")
        )

    except Exception:
        return False


def money(value):
    return f"{int(value):,}".replace(",", ".") + " VNĐ"


def goal_description(goal):
    mapping = {
        "Tăng lượt xem":
            "Ưu tiên phân phối video tới nhiều người xem hơn.",

        "Tăng người theo dõi":
            "Ưu tiên tăng khả năng người xem ghé hồ sơ và theo dõi.",

        "Tăng lượt xem hồ sơ":
            "Ưu tiên đưa người xem tới trang cá nhân.",

        "Tăng tin nhắn":
            "Hướng người xem tới hành động nhắn tin nếu tài khoản đủ điều kiện."
    }

    return mapping.get(goal, "")


# ============================================================
# HEADER
# ============================================================

st.title("🚀 TikTok Promote Builder")

st.caption(
    "Tạo cấu hình quảng bá video TikTok và chuyển nhanh "
    "sang video cần Promote."
)

st.info(
    "Tool này không tự cộng view/tim. "
    "Chiến dịch chỉ bắt đầu sau khi bạn xác nhận và thanh toán "
    "trong TikTok Promote."
)


# ============================================================
# VIDEO URL
# ============================================================

st.header("1️⃣ Video TikTok")

video_url = st.text_input(
    "Dán link video",
    placeholder=(
        "https://www.tiktok.com/@username/video/..."
    )
)

if video_url:

    if valid_tiktok_url(video_url):

        st.success("✓ Link TikTok hợp lệ")

        st.link_button(
            "▶️ Mở video trên TikTok",
            video_url,
            use_container_width=True
        )

    else:

        st.error(
            "Link chưa hợp lệ. Hãy dán link video TikTok."
        )


# ============================================================
# CAMPAIGN GOAL
# ============================================================

st.header("2️⃣ Mục tiêu")

goal = st.selectbox(
    "Bạn muốn chiến dịch tập trung vào đâu?",
    [
        "Tăng lượt xem",
        "Tăng người theo dõi",
        "Tăng lượt xem hồ sơ",
        "Tăng tin nhắn"
    ]
)

st.caption(
    goal_description(goal)
)


# ============================================================
# AUDIENCE
# ============================================================

st.header("3️⃣ Đối tượng")

audience_mode = st.radio(
    "Cách chọn đối tượng",
    [
        "Tự động",
        "Tự chọn"
    ],
    horizontal=True
)

audience_summary = "TikTok tự tối ưu đối tượng"

if audience_mode == "Tự chọn":

    age = st.selectbox(
        "Nhóm tuổi ưu tiên",
        [
            "18–24",
            "25–34",
            "35–44",
            "45–54",
            "55+",
            "Không giới hạn"
        ]
    )

    gender = st.selectbox(
        "Giới tính",
        [
            "Tất cả",
            "Nam",
            "Nữ"
        ]
    )

    interests = st.multiselect(
        "Nhóm nội dung / sở thích",
        [
            "Giải trí",
            "Công nghệ",
            "Gaming",
            "Anime",
            "Phim",
            "Âm nhạc",
            "Thời trang",
            "Làm đẹp",
            "Ẩm thực",
            "Thể thao",
            "Giáo dục",
            "Kinh doanh"
        ]
    )

    audience_summary = (
        f"{age} | {gender}"
    )

    if interests:
        audience_summary += (
            " | " + ", ".join(interests)
        )


# ============================================================
# BUDGET
# ============================================================

st.header("4️⃣ Ngân sách")

budget = st.number_input(
    "Tổng ngân sách dự kiến (VNĐ)",
    min_value=50000,
    max_value=100000000,
    value=100000,
    step=50000
)

days = st.slider(
    "Số ngày chạy",
    min_value=1,
    max_value=30,
    value=1
)

daily_budget = budget / days

st.metric(
    "Ngân sách trung bình/ngày",
    money(daily_budget)
)


# ============================================================
# OPTIONAL NOTE
# ============================================================

st.header("5️⃣ Ghi chú")

campaign_note = st.text_area(
    "Mục đích / ghi chú cho chiến dịch",
    placeholder=(
        "Ví dụ: muốn đẩy video AI này để test "
        "khán giả 18–24..."
    )
)


# ============================================================
# CREATE PLAN
# ============================================================

if st.button(
    "🚀 TẠO CHIẾN DỊCH",
    type="primary",
    use_container_width=True
):

    if not video_url:

        st.error(
            "Hãy dán link video TikTok trước."
        )

    elif not valid_tiktok_url(video_url):

        st.error(
            "Link TikTok không hợp lệ."
        )

    else:

        campaign = {
            "time": datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),
            "video": video_url,
            "goal": goal,
            "audience": audience_summary,
            "budget": int(budget),
            "days": days,
            "daily": int(daily_budget),
            "note": campaign_note
        }

        st.session_state.campaigns.append(
            campaign
        )

        st.success(
            "✓ Đã tạo cấu hình chiến dịch."
        )

        st.header("📋 Kế hoạch")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Ngân sách",
                money(budget)
            )

            st.metric(
                "Số ngày",
                days
            )

        with c2:

            st.metric(
                "Mỗi ngày",
                money(daily_budget)
            )

            st.metric(
                "Mục tiêu",
                goal
            )

        st.write(
            f"**Đối tượng:** {audience_summary}"
        )

        if campaign_note:

            st.write(
                f"**Ghi chú:** {campaign_note}"
            )

        # --------------------------------------------
        # COPYABLE SUMMARY
        # --------------------------------------------

        st.subheader("📋 Cấu hình để nhập vào Promote")

        summary = f"""
MỤC TIÊU
{goal}

ĐỐI TƯỢNG
{audience_summary}

NGÂN SÁCH
{money(budget)}

THỜI GIAN
{days} ngày

NGÂN SÁCH TRUNG BÌNH
{money(daily_budget)}/ngày
"""

        st.code(
            summary.strip(),
            language=None
        )

        # --------------------------------------------
        # NEXT ACTION
        # --------------------------------------------

        st.subheader("🔥 Bắt đầu chạy thật")

        st.write(
            "Bấm nút dưới để mở video. "
            "Trong TikTok, mở menu **…** của video "
            "và chọn **Promote / Quảng bá**."
        )

        st.link_button(
            "🚀 MỞ VIDEO TRÊN TIKTOK",
            video_url,
            use_container_width=True
        )

        st.link_button(
            "📖 HƯỚNG DẪN PROMOTE CHÍNH THỨC",
            PROMOTE_HELP_URL,
            use_container_width=True
        )

        st.warning(
            "View chỉ bắt đầu được phân phối sau khi "
            "TikTok chấp nhận chiến dịch và bước thanh toán "
            "trong Promote được hoàn tất."
        )


# ============================================================
# CAMPAIGN HISTORY
# ============================================================

if st.session_state.campaigns:

    st.divider()

    st.header("🗂 Chiến dịch đã tạo")

    for i, campaign in enumerate(
        reversed(st.session_state.campaigns),
        1
    ):

        with st.expander(
            f"Chiến dịch {i} — {campaign['goal']}"
        ):

            st.write(
                f"**Tạo lúc:** {campaign['time']}"
            )

            st.write(
                f"**Ngân sách:** "
                f"{money(campaign['budget'])}"
            )

            st.write(
                f"**Thời gian:** "
                f"{campaign['days']} ngày"
            )

            st.write(
                f"**Đối tượng:** "
                f"{campaign['audience']}"
            )

            st.link_button(
                "Mở video",
                campaign["video"]
            )
