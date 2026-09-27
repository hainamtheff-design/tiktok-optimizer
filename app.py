import re
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="TeaHack TikTok Growth Service",
    page_icon="🚀",
    layout="wide"
)

if "campaigns" not in st.session_state:
    st.session_state.campaigns = []

if "campaign_id" not in st.session_state:
    st.session_state.campaign_id = 1


# =========================================================
# HELPERS
# =========================================================

def extract_video_id(url):
    """
    TikTok URL example:
    https://www.tiktok.com/@username/video/1234567890
    """
    match = re.search(r"/video/(\d+)", url)

    if match:
        return match.group(1)

    return None


def percent(value, maximum):
    if maximum <= 0:
        return 0

    return min(
        max(value / maximum, 0),
        1
    )


def format_number(number):
    return f"{int(number):,}"


# =========================================================
# TIKTOK VIDEO API
# =========================================================

def get_video_stats(video_id, access_token):

    endpoint = (
        "https://open.tiktokapis.com/"
        "v2/video/query/"
    )

    params = {
        "fields": (
            "id,title,share_url,"
            "view_count,like_count,"
            "comment_count,share_count"
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
                video_id
            ]
        }
    }

    try:

        response = requests.post(
            endpoint,
            params=params,
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            return None

        data = response.json()

        videos = (
            data
            .get("data", {})
            .get("videos", [])
        )

        if not videos:
            return None

        return videos[0]

    except Exception:
        return None


# =========================================================
# HEADER
# =========================================================

st.title(
    "🚀 TeaHack TikTok Growth Service"
)

st.caption(
    "Tạo chiến dịch tăng trưởng và theo dõi "
    "View / Like / Comment / Share theo thời gian."
)

st.info(
    "Traffic thật phải đến từ TikTok Ads/Promote "
    "hoặc một mạng phân phối người xem thật. "
    "Dashboard này quản lý và đo kết quả."
)


# =========================================================
# CREATE CAMPAIGN
# =========================================================

st.header(
    "➕ Tạo chiến dịch"
)

video_url = st.text_input(
    "Link TikTok",
    placeholder=(
        "https://www.tiktok.com/"
        "@username/video/123456789"
    )
)

video_id = extract_video_id(
    video_url
)

if video_url:

    if video_id:

        st.success(
            f"✓ Video ID: {video_id}"
        )

    else:

        st.warning(
            "Không đọc được Video ID. "
            "Nếu đang dùng link rút gọn, "
            "hãy mở video rồi copy link đầy đủ."
        )


# =========================================================
# CAMPAIGN TYPE
# =========================================================

service = st.selectbox(
    "Nguồn traffic",
    [
        "TikTok Ads / Promote",
        "Creator Network",
        "Theo dõi Organic"
    ]
)


# =========================================================
# GOAL
# =========================================================

col1, col2 = st.columns(2)

with col1:

    target_views = st.number_input(
        "View muốn tăng",
        min_value=100,
        value=10000,
        step=1000
    )

with col2:

    duration_days = st.slider(
        "Thời gian chiến dịch",
        min_value=1,
        max_value=30,
        value=3
    )


# =========================================================
# CURRENT NUMBERS
# =========================================================

st.subheader(
    "📊 Số liệu ban đầu"
)

c1, c2 = st.columns(2)

with c1:

    starting_views = st.number_input(
        "View hiện tại",
        min_value=0,
        value=0,
        step=100
    )

    starting_likes = st.number_input(
        "Like hiện tại",
        min_value=0,
        value=0,
        step=10
    )

with c2:

    starting_comments = st.number_input(
        "Comment hiện tại",
        min_value=0,
        value=0
    )

    starting_shares = st.number_input(
        "Share hiện tại",
        min_value=0,
        value=0
    )


# =========================================================
# CREATE
# =========================================================

if st.button(
    "🚀 TẠO CHIẾN DỊCH",
    type="primary",
    use_container_width=True
):

    if not video_url:

        st.error(
            "Chưa nhập link TikTok."
        )

    else:

        campaign = {

            "id":
                st.session_state.campaign_id,

            "url":
                video_url,

            "video_id":
                video_id,

            "provider":
                service,

            "target_views":
                target_views,

            "days":
                duration_days,

            "start_views":
                starting_views,

            "start_likes":
                starting_likes,

            "start_comments":
                starting_comments,

            "start_shares":
                starting_shares,

            "current_views":
                starting_views,

            "current_likes":
                starting_likes,

            "current_comments":
                starting_comments,

            "current_shares":
                starting_shares,

            "status":
                "READY",

            "created":
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
        }

        st.session_state.campaigns.append(
            campaign
        )

        st.session_state.campaign_id += 1

        st.success(
            "✓ Đã tạo chiến dịch."
        )


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.campaigns:

    st.divider()

    st.header(
        "📡 Campaign Dashboard"
    )

    for campaign in reversed(
        st.session_state.campaigns
    ):

        cid = campaign["id"]

        title = (
            f"Campaign #{cid} — "
            f"{campaign['provider']}"
        )

        with st.expander(
            title,
            expanded=True
        ):

            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            status = st.selectbox(
                "Trạng thái",
                [
                    "READY",
                    "ACTIVE",
                    "PAUSED",
                    "COMPLETED"
                ],
                index=[
                    "READY",
                    "ACTIVE",
                    "PAUSED",
                    "COMPLETED"
                ].index(
                    campaign["status"]
                ),
                key=f"status_{cid}"
            )

            campaign["status"] = status

            # -----------------------------------------
            # VIDEO
            # -----------------------------------------

            st.write(
                f"**Video ID:** "
                f"{campaign['video_id'] or 'N/A'}"
            )

            st.link_button(
                "▶️ Mở TikTok",
                campaign["url"]
            )

            # -----------------------------------------
            # CURRENT NUMBERS
            # -----------------------------------------

            st.subheader(
                "Cập nhật số liệu"
            )

            x1, x2 = st.columns(2)

            with x1:

                current_views = st.number_input(
                    "View hiện tại",
                    min_value=0,
                    value=int(
                        campaign[
                            "current_views"
                        ]
                    ),
                    key=f"views_{cid}"
                )

                current_likes = st.number_input(
                    "Like hiện tại",
                    min_value=0,
                    value=int(
                        campaign[
                            "current_likes"
                        ]
                    ),
                    key=f"likes_{cid}"
                )

            with x2:

                current_comments = st.number_input(
                    "Comment hiện tại",
                    min_value=0,
                    value=int(
                        campaign[
                            "current_comments"
                        ]
                    ),
                    key=f"comments_{cid}"
                )

                current_shares = st.number_input(
                    "Share hiện tại",
                    min_value=0,
                    value=int(
                        campaign[
                            "current_shares"
                        ]
                    ),
                    key=f"shares_{cid}"
                )

            campaign[
                "current_views"
            ] = current_views

            campaign[
                "current_likes"
            ] = current_likes

            campaign[
                "current_comments"
            ] = current_comments

            campaign[
                "current_shares"
            ] = current_shares

            # -----------------------------------------
            # GAINS
            # -----------------------------------------

            gained_views = max(
                0,
                current_views
                - campaign["start_views"]
            )

            gained_likes = max(
                0,
                current_likes
                - campaign["start_likes"]
            )

            gained_comments = max(
                0,
                current_comments
                - campaign["start_comments"]
            )

            gained_shares = max(
                0,
                current_shares
                - campaign["start_shares"]
            )

            # -----------------------------------------
            # PROGRESS
            # -----------------------------------------

            progress = percent(
                gained_views,
                campaign["target_views"]
            )

            st.subheader(
                "📈 Kết quả"
            )

            a, b = st.columns(2)

            with a:

                st.metric(
                    "View tăng",
                    f"+{format_number(gained_views)}"
                )

                st.metric(
                    "Like tăng",
                    f"+{format_number(gained_likes)}"
                )

            with b:

                st.metric(
                    "Comment tăng",
                    f"+{format_number(gained_comments)}"
                )

                st.metric(
                    "Share tăng",
                    f"+{format_number(gained_shares)}"
                )

            # -----------------------------------------
            # TARGET
            # -----------------------------------------

            st.write(
                "**Tiến độ View**"
            )

            st.progress(
                progress
            )

            st.write(
                f"{format_number(gained_views)} "
                f"/ "
                f"{format_number(campaign['target_views'])}"
            )

            percent_done = (
                progress * 100
            )

            st.write(
                f"**{percent_done:.1f}% hoàn thành**"
            )

            # -----------------------------------------
            # LIKE RATE
            # -----------------------------------------

            if current_views > 0:

                like_rate = (
                    current_likes
                    / current_views
                    * 100
                )

                st.metric(
                    "Like / View",
                    f"{like_rate:.2f}%"
                )

            # -----------------------------------------
            # DELIVERY STATUS
            # -----------------------------------------

            remaining = max(
                campaign["target_views"]
                - gained_views,
                0
            )

            st.write(
                f"**Còn lại:** "
                f"{format_number(remaining)} view"
            )

            if remaining == 0:

                st.success(
                    "🏆 Đã đạt mục tiêu chiến dịch."
                )


# =========================================================
# SUMMARY
# =========================================================

if st.session_state.campaigns:

    st.divider()

    st.header(
        "📋 Tất cả chiến dịch"
    )

    rows = []

    for c in st.session_state.campaigns:

        gained = (
            c["current_views"]
            - c["start_views"]
        )

        rows.append({

            "Campaign":
                c["id"],

            "Provider":
                c["provider"],

            "Status":
                c["status"],

            "Target Views":
                c["target_views"],

            "Views Gained":
                max(gained, 0),

            "Created":
                c["created"]
        })

    df = pd.DataFrame(
        rows
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
