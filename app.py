import re
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st


# ============================================================
# APP CONFIG
# ============================================================

st.set_page_config(
    page_title="TeaHack TikTok Growth Service",
    page_icon="🚀",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "campaigns" not in st.session_state:
    st.session_state.campaigns = []

if "campaign_counter" not in st.session_state:
    st.session_state.campaign_counter = 1

if "resolved_video" not in st.session_state:
    st.session_state.resolved_video = None


# ============================================================
# CONSTANTS
# ============================================================

PROMOTE_HELP_URL = (
    "https://ads.tiktok.com/resources/help/article/"
    "how-to-find-promote-in-app-and-on-web?lang=vi"
)

OEMBED_ENDPOINT = "https://www.tiktok.com/oembed"

TIKTOK_VIDEO_QUERY_ENDPOINT = (
    "https://open.tiktokapis.com/v2/video/query/"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 "
        "Version/18.0 Mobile/15E148 Safari/604.1"
    )
}


# ============================================================
# UTILITIES
# ============================================================

def format_number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def money(value):
    try:
        return f"{int(value):,}".replace(",", ".") + " VNĐ"
    except Exception:
        return "0 VNĐ"


def safe_percent(current, maximum):
    if maximum <= 0:
        return 0.0

    return min(
        max(current / maximum, 0.0),
        1.0
    )


# ============================================================
# TIKTOK URL VALIDATION
# ============================================================

def is_tiktok_url(url):
    try:
        parsed = urlparse(url.strip())

        if parsed.scheme not in ("http", "https"):
            return False

        host = (parsed.hostname or "").lower()

        return (
            host == "tiktok.com"
            or host.endswith(".tiktok.com")
        )

    except Exception:
        return False


# ============================================================
# VIDEO ID EXTRACTION
# ============================================================

def extract_video_id(text):
    if not text:
        return None

    patterns = [
        r"/video/(\d+)",
        r"[?&]item_id=(\d+)",
        r"[?&]video_id=(\d+)",
        r'data-video-id=["\'](\d+)["\']',
        r'"videoId":"(\d+)"',
        r'"id":"(\d{10,})"',
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


# ============================================================
# RESOLVE SHORT TIKTOK LINK
# ============================================================

def resolve_tiktok_url(url):
    """
    Hỗ trợ:
    - vt.tiktok.com
    - vm.tiktok.com
    - www.tiktok.com/@user/video/...
    """

    if not url:
        return {
            "ok": False,
            "error": "Chưa nhập link TikTok."
        }

    url = url.strip()

    if not is_tiktok_url(url):
        return {
            "ok": False,
            "error": "Link không thuộc TikTok."
        }

    # Nếu link đã có video ID
    direct_id = extract_video_id(url)

    if direct_id:
        return {
            "ok": True,
            "original_url": url,
            "final_url": url,
            "video_id": direct_id,
        }

    # Resolve link rút gọn
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            allow_redirects=True,
            timeout=15,
        )

        final_url = response.url

        video_id = extract_video_id(
            final_url
        )

        if video_id:
            return {
                "ok": True,
                "original_url": url,
                "final_url": final_url,
                "video_id": video_id,
            }

        # Fallback tìm trong HTML
        html = (
            response.text
            .replace("\\/", "/")
        )

        canonical_match = re.search(
            r'https://(?:www\.)?tiktok\.com/'
            r'@[^"\s<>]+/video/\d+',
            html,
            flags=re.IGNORECASE
        )

        if canonical_match:

            canonical_url = canonical_match.group(0)

            video_id = extract_video_id(
                canonical_url
            )

            if video_id:
                return {
                    "ok": True,
                    "original_url": url,
                    "final_url": canonical_url,
                    "video_id": video_id,
                }

        # Một số trang chứa ID nhưng không lộ canonical
        video_id = extract_video_id(
            html
        )

        if video_id:
            return {
                "ok": True,
                "original_url": url,
                "final_url": final_url,
                "video_id": video_id,
            }

    except requests.RequestException:
        pass

    # Fallback oEmbed
    try:
        response = requests.get(
            OEMBED_ENDPOINT,
            params={"url": url},
            headers=HEADERS,
            timeout=15,
        )

        if response.status_code == 200:

            data = response.json()

            embed_html = (
                data.get("html", "")
                .replace("\\/", "/")
            )

            video_id = extract_video_id(
                embed_html
            )

            canonical_match = re.search(
                r'https://(?:www\.)?tiktok\.com/'
                r'@[^"\s<>]+/video/\d+',
                embed_html,
                flags=re.IGNORECASE
            )

            if canonical_match:
                final_url = canonical_match.group(0)
            else:
                final_url = url

            if video_id:
                return {
                    "ok": True,
                    "original_url": url,
                    "final_url": final_url,
                    "video_id": video_id,
                }

    except Exception:
        pass

    return {
        "ok": False,
        "original_url": url,
        "final_url": url,
        "video_id": None,
        "error": (
            "Không lấy được Video ID. "
            "TikTok có thể đang chặn việc resolve link này. "
            "Hãy thử lại hoặc mở video rồi copy link đầy đủ."
        )
    }


# ============================================================
# OEMBED METADATA
# ============================================================

def get_public_video_info(url):
    try:
        response = requests.get(
            OEMBED_ENDPOINT,
            params={"url": url},
            headers=HEADERS,
            timeout=15,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        return {
            "title": data.get("title", ""),
            "author_name": data.get(
                "author_name",
                ""
            ),
            "author_url": data.get(
                "author_url",
                ""
            ),
            "thumbnail_url": data.get(
                "thumbnail_url",
                ""
            ),
            "provider_name": data.get(
                "provider_name",
                ""
            ),
        }

    except Exception:
        return None


# ============================================================
# OPTIONAL TIKTOK API
# ============================================================

def get_tiktok_access_token():
    """
    Nếu muốn dùng API thật sau này,
    thêm vào Streamlit Secrets:

    TIKTOK_ACCESS_TOKEN = "..."
    """

    try:
        return st.secrets.get(
            "TIKTOK_ACCESS_TOKEN",
            ""
        )
    except Exception:
        return ""


def get_authorized_video_stats(
    video_id,
    access_token
):
    """
    Chỉ hoạt động nếu access token có quyền
    phù hợp và video thuộc tài khoản đã cấp quyền.
    """

    if not video_id:
        return None, "Không có Video ID."

    if not access_token:
        return None, "Chưa cấu hình TikTok Access Token."

    params = {
        "fields": (
            "id,"
            "title,"
            "share_url,"
            "view_count,"
            "like_count,"
            "comment_count,"
            "share_count"
        )
    }

    headers = {
        "Authorization":
            f"Bearer {access_token}",

        "Content-Type":
            "application/json"
    }

    payload = {
        "filters": {
            "video_ids": [
                str(video_id)
            ]
        }
    }

    try:
        response = requests.post(
            TIKTOK_VIDEO_QUERY_ENDPOINT,
            params=params,
            headers=headers,
            json=payload,
            timeout=20,
        )

        if response.status_code != 200:

            return (
                None,
                f"TikTok API trả về "
                f"{response.status_code}"
            )

        payload = response.json()

        videos = (
            payload
            .get("data", {})
            .get("videos", [])
        )

        if not videos:
            return (
                None,
                "Không tìm thấy dữ liệu video."
            )

        return videos[0], None

    except requests.RequestException as e:

        return (
            None,
            f"Lỗi kết nối TikTok API: {e}"
        )


# ============================================================
# HEADER
# ============================================================

st.title(
    "🚀 TeaHack TikTok Growth Service"
)

st.caption(
    "Nhận diện video TikTok, tạo chiến dịch "
    "và theo dõi View / Like / Comment / Share."
)

st.info(
    "Dashboard này không tự tạo tương tác giả. "
    "Traffic thực tế phải đến từ TikTok Promote/Ads, "
    "creator hoặc lượt xem organic."
)


# ============================================================
# STEP 1 — VIDEO
# ============================================================

st.header(
    "1️⃣ Nhận diện video"
)

video_url_input = st.text_input(
    "Dán link TikTok",
    placeholder=(
        "https://vt.tiktok.com/..."
    ),
)


if st.button(
    "🔎 NHẬN DIỆN VIDEO",
    use_container_width=True
):

    with st.spinner(
        "Đang xử lý link TikTok..."
    ):

        result = resolve_tiktok_url(
            video_url_input
        )

    if not result.get("ok"):

        st.session_state.resolved_video = None

        st.error(
            result.get(
                "error",
                "Không nhận diện được video."
            )
        )

    else:

        final_url = result["final_url"]

        public_info = get_public_video_info(
            final_url
        )

        st.session_state.resolved_video = {
            "original_url":
                result["original_url"],

            "final_url":
                final_url,

            "video_id":
                result["video_id"],

            "public_info":
                public_info,
        }

        st.success(
            f"✅ Video ID: "
            f"{result['video_id']}"
        )


# ============================================================
# VIDEO PREVIEW
# ============================================================

resolved = (
    st.session_state.resolved_video
)

if resolved:

    info = resolved.get(
        "public_info"
    )

    st.subheader(
        "📹 Video đã nhận diện"
    )

    st.write(
        f"**Video ID:** "
        f"{resolved['video_id']}"
    )

    if (
        resolved["original_url"]
        != resolved["final_url"]
    ):
        st.caption(
            "Link rút gọn đã được chuyển "
            "thành link đầy đủ."
        )

    if info:

        if info.get(
            "thumbnail_url"
        ):
            st.image(
                info["thumbnail_url"],
                width=320
            )

        if info.get(
            "author_name"
        ):
            st.write(
                f"**Tác giả:** "
                f"{info['author_name']}"
            )

        if info.get(
            "title"
        ):
            st.write(
                f"**Caption:** "
                f"{info['title']}"
            )

    st.link_button(
        "▶️ MỞ VIDEO TRÊN TIKTOK",
        resolved["final_url"],
        use_container_width=True,
    )


# ============================================================
# STEP 2 — CAMPAIGN
# ============================================================

st.divider()

st.header(
    "2️⃣ Tạo chiến dịch"
)

provider = st.selectbox(
    "Nguồn traffic",
    [
        "TikTok Ads / Promote",
        "Creator Network",
        "Organic Tracking",
    ]
)

goal = st.selectbox(
    "Mục tiêu",
    [
        "Tăng lượt xem",
        "Tăng lượt xem hồ sơ",
        "Tăng người theo dõi",
    ]
)

col1, col2 = st.columns(2)

with col1:

    target_views = st.number_input(
        "View muốn tăng",
        min_value=100,
        value=10000,
        step=1000,
    )

with col2:

    campaign_days = st.slider(
        "Thời gian chiến dịch",
        min_value=1,
        max_value=30,
        value=3,
    )


# ============================================================
# OPTIONAL BUDGET
# ============================================================

budget = 0

if provider == "TikTok Ads / Promote":

    budget = st.number_input(
        "Ngân sách dự kiến (VNĐ)",
        min_value=0,
        value=0,
        step=50000,
    )

    if budget > 0:

        st.metric(
            "Ngân sách/ngày",
            money(
                budget / campaign_days
            )
        )


# ============================================================
# STARTING DATA
# ============================================================

st.subheader(
    "📊 Số liệu ban đầu"
)

start_col1, start_col2 = (
    st.columns(2)
)

with start_col1:

    start_views = st.number_input(
        "View hiện tại",
        min_value=0,
        value=0,
        step=100,
    )

    start_likes = st.number_input(
        "Like hiện tại",
        min_value=0,
        value=0,
        step=10,
    )

with start_col2:

    start_comments = st.number_input(
        "Comment hiện tại",
        min_value=0,
        value=0,
        step=1,
    )

    start_shares = st.number_input(
        "Share hiện tại",
        min_value=0,
        value=0,
        step=1,
    )


# ============================================================
# OPTIONAL AUTO LOAD STATS
# ============================================================

access_token = get_tiktok_access_token()

if resolved and access_token:

    if st.button(
        "🔄 LẤY SỐ LIỆU TỪ TIKTOK API",
        use_container_width=True
    ):

        with st.spinner(
            "Đang đọc số liệu..."
        ):

            stats, api_error = (
                get_authorized_video_stats(
                    resolved["video_id"],
                    access_token,
                )
            )

        if api_error:

            st.error(
                api_error
            )

        else:

            st.success(
                "✅ Đã đọc số liệu từ TikTok API."
            )

            st.write(
                f"View: "
                f"{format_number(stats.get('view_count', 0))}"
            )

            st.write(
                f"Like: "
                f"{format_number(stats.get('like_count', 0))}"
            )

            st.write(
                f"Comment: "
                f"{format_number(stats.get('comment_count', 0))}"
            )

            st.write(
                f"Share: "
                f"{format_number(stats.get('share_count', 0))}"
            )


# ============================================================
# CREATE CAMPAIGN
# ============================================================

if st.button(
    "🚀 TẠO CHIẾN DỊCH",
    type="primary",
    use_container_width=True
):

    if not resolved:

        st.error(
            "Hãy nhận diện video trước."
        )

    else:

        campaign = {
            "id":
                st.session_state.campaign_counter,

            "created":
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),

            "original_url":
                resolved["original_url"],

            "url":
                resolved["final_url"],

            "video_id":
                resolved["video_id"],

            "provider":
                provider,

            "goal":
                goal,

            "target_views":
                int(target_views),

            "days":
                int(campaign_days),

            "budget":
                int(budget),

            "start_views":
                int(start_views),

            "start_likes":
                int(start_likes),

            "start_comments":
                int(start_comments),

            "start_shares":
                int(start_shares),

            "current_views":
                int(start_views),

            "current_likes":
                int(start_likes),

            "current_comments":
                int(start_comments),

            "current_shares":
                int(start_shares),

            "status":
                "READY",
        }

        st.session_state.campaigns.append(
            campaign
        )

        st.session_state.campaign_counter += 1

        st.success(
            "✅ Đã tạo chiến dịch."
        )


# ============================================================
# PROMOTE HELPER
# ============================================================

if (
    resolved
    and provider == "TikTok Ads / Promote"
):

    st.subheader(
        "🔥 TikTok Promote"
    )

    if budget <= 0:

        st.info(
            "Nếu không có ngân sách, "
            "có thể dùng Organic Tracking "
            "hoặc Creator Network."
        )

    else:

        st.write(
            f"**Ngân sách:** "
            f"{money(budget)}"
        )

        st.write(
            f"**Thời gian:** "
            f"{campaign_days} ngày"
        )

        st.write(
            f"**Trung bình/ngày:** "
            f"{money(budget / campaign_days)}"
        )

        st.link_button(
            "🚀 MỞ VIDEO ĐỂ PROMOTE",
            resolved["final_url"],
            use_container_width=True,
        )

        st.link_button(
            "📖 HƯỚNG DẪN PROMOTE",
            PROMOTE_HELP_URL,
            use_container_width=True,
        )


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.campaigns:

    st.divider()

    st.header(
        "📡 Campaign Dashboard"
    )

    for campaign in reversed(
        st.session_state.campaigns
    ):

        cid = campaign["id"]

        with st.expander(
            (
                f"Campaign #{cid} — "
                f"{campaign['goal']}"
            ),
            expanded=True,
        ):

            # ----------------------------------------
            # STATUS
            # ----------------------------------------

            statuses = [
                "READY",
                "ACTIVE",
                "PAUSED",
                "COMPLETED",
            ]

            status = st.selectbox(
                "Trạng thái",
                statuses,
                index=statuses.index(
                    campaign["status"]
                ),
                key=f"status_{cid}",
            )

            campaign["status"] = status

            # ----------------------------------------
            # BASIC INFO
            # ----------------------------------------

            st.write(
                f"**Video ID:** "
                f"{campaign['video_id']}"
            )

            st.write(
                f"**Nguồn:** "
                f"{campaign['provider']}"
            )

            st.write(
                f"**Ngày tạo:** "
                f"{campaign['created']}"
            )

            if campaign["budget"] > 0:

                st.write(
                    f"**Ngân sách:** "
                    f"{money(campaign['budget'])}"
                )

            st.link_button(
                "▶️ Mở video TikTok",
                campaign["url"],
            )

            # ----------------------------------------
            # CURRENT STATS
            # ----------------------------------------

            st.subheader(
                "📊 Cập nhật số liệu"
            )

            c1, c2 = st.columns(2)

            with c1:

                current_views = st.number_input(
                    "View hiện tại",
                    min_value=0,
                    value=int(
                        campaign["current_views"]
                    ),
                    key=f"views_{cid}",
                )

                current_likes = st.number_input(
                    "Like hiện tại",
                    min_value=0,
                    value=int(
                        campaign["current_likes"]
                    ),
                    key=f"likes_{cid}",
                )

            with c2:

                current_comments = st.number_input(
                    "Comment hiện tại",
                    min_value=0,
                    value=int(
                        campaign["current_comments"]
                    ),
                    key=f"comments_{cid}",
                )

                current_shares = st.number_input(
                    "Share hiện tại",
                    min_value=0,
                    value=int(
                        campaign["current_shares"]
                    ),
                    key=f"shares_{cid}",
                )

            campaign["current_views"] = int(
                current_views
            )

            campaign["current_likes"] = int(
                current_likes
            )

            campaign["current_comments"] = int(
                current_comments
            )

            campaign["current_shares"] = int(
                current_shares
            )

            # ----------------------------------------
            # GAINS
            # ----------------------------------------

            gained_views = max(
                campaign["current_views"]
                - campaign["start_views"],
                0,
            )

            gained_likes = max(
                campaign["current_likes"]
                - campaign["start_likes"],
                0,
            )

            gained_comments = max(
                campaign["current_comments"]
                - campaign["start_comments"],
                0,
            )

            gained_shares = max(
                campaign["current_shares"]
                - campaign["start_shares"],
                0,
            )

            # ----------------------------------------
            # METRICS
            # ----------------------------------------

            st.subheader(
                "📈 Kết quả"
            )

            m1, m2 = st.columns(2)

            with m1:

                st.metric(
                    "View tăng",
                    "+" + format_number(
                        gained_views
                    )
                )

                st.metric(
                    "Like tăng",
                    "+" + format_number(
                        gained_likes
                    )
                )

            with m2:

                st.metric(
                    "Comment tăng",
                    "+" + format_number(
                        gained_comments
                    )
                )

                st.metric(
                    "Share tăng",
                    "+" + format_number(
                        gained_shares
                    )
                )

            # ----------------------------------------
            # PROGRESS
            # ----------------------------------------

            progress = safe_percent(
                gained_views,
                campaign["target_views"],
            )

            st.write(
                "**Tiến độ mục tiêu View**"
            )

            st.progress(
                progress
            )

            st.write(
                f"{format_number(gained_views)}"
                f" / "
                f"{format_number(campaign['target_views'])}"
            )

            st.write(
                f"**{progress * 100:.1f}% hoàn thành**"
            )

            remaining = max(
                campaign["target_views"]
                - gained_views,
                0,
            )

            st.metric(
                "View còn lại",
                format_number(
                    remaining
                )
            )

            # ----------------------------------------
            # LIKE RATE
            # ----------------------------------------

            if campaign["current_views"] > 0:

                like_rate = (
                    campaign["current_likes"]
                    / campaign["current_views"]
                    * 100
                )

                st.metric(
                    "Like / View",
                    f"{like_rate:.2f}%"
                )

            if remaining == 0:

                st.success(
                    "🏆 Đã đạt mục tiêu chiến dịch."
                )


# ============================================================
# ALL CAMPAIGNS
# ============================================================

if st.session_state.campaigns:

    st.divider()

    st.header(
        "📋 Tổng hợp chiến dịch"
    )

    rows = []

    for campaign in (
        st.session_state.campaigns
    ):

        gained_views = max(
            campaign["current_views"]
            - campaign["start_views"],
            0,
        )

        rows.append({
            "ID":
                campaign["id"],

            "Video ID":
                campaign["video_id"],

            "Nguồn":
                campaign["provider"],

            "Mục tiêu":
                campaign["goal"],

            "Trạng thái":
                campaign["status"],

            "Target View":
                campaign["target_views"],

            "View tăng":
                gained_views,

            "Ngày tạo":
                campaign["created"],
        })

    df = pd.DataFrame(
        rows
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        "⬇️ TẢI DANH SÁCH CHIẾN DỊCH",
        data=csv,
        file_name=(
            "tiktok_campaigns.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# RESET
# ============================================================

if st.session_state.campaigns:

    if st.button(
        "🗑 Xóa toàn bộ chiến dịch",
        use_container_width=True,
    ):

        st.session_state.campaigns = []
        st.session_state.campaign_counter = 1

        st.rerun()
