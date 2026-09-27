import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from urllib.parse import urlparse

st.set_page_config(
    page_title="TeaHack TikTok Optimizer",
    page_icon="📈",
    layout="wide"
)

# =========================
# SESSION
# =========================

defaults = {
    "history": [],
    "video_name": "",
    "hook": "",
    "author": "",
    "thumbnail": "",
    "tiktok_url": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================
# URL VALIDATION
# =========================

def valid_tiktok_url(url):
    try:
        host = urlparse(url).netloc.lower()

        allowed = [
            "tiktok.com",
            "www.tiktok.com",
            "vm.tiktok.com",
            "vt.tiktok.com",
        ]

        return host in allowed or host.endswith(".tiktok.com")

    except Exception:
        return False


# =========================
# OEMBED FETCH
# =========================

def get_tiktok_info(url):

    if not valid_tiktok_url(url):
        return None, "Link TikTok không hợp lệ."

    endpoint = "https://www.tiktok.com/oembed"

    try:
        response = requests.get(
            endpoint,
            params={"url": url},
            timeout=12,
            headers={
                "User-Agent":
                "Mozilla/5.0 TikTokOptimizer/1.0"
            }
        )

        if response.status_code != 200:
            return None, f"TikTok trả về lỗi {response.status_code}"

        data = response.json()

        return {
            "title": data.get("title", ""),
            "author": data.get("author_name", ""),
            "author_url": data.get("author_url", ""),
            "thumbnail": data.get("thumbnail_url", ""),
            "provider": data.get("provider_name", ""),
        }, None

    except requests.RequestException:
        return None, "Không thể kết nối TikTok."

    except Exception as e:
        return None, f"Lỗi: {e}"


# =========================
# HEADER
# =========================

st.title("TeaHack TikTok Optimizer")

st.caption(
    "Dán link TikTok hoặc nhập dữ liệu thủ công để phân tích video."
)

st.info(
    "Viral Score là chỉ số phân tích do tool tự tính, "
    "không phải điểm chính thức của TikTok."
)


# =========================
# LINK IMPORT
# =========================

st.subheader("🔗 Nhập link TikTok")

url = st.text_input(
    "Link video TikTok",
    placeholder="https://www.tiktok.com/@username/video/..."
)

if st.button(
    "Lấy thông tin video",
    use_container_width=True
):

    if not url:
        st.warning("Hãy dán link TikTok trước.")

    else:
        with st.spinner("Đang đọc thông tin video..."):

            info, error = get_tiktok_info(url)

        if error:
            st.error(error)

        else:
            st.session_state.tiktok_url = url
            st.session_state.video_name = info["title"]
            st.session_state.author = info["author"]
            st.session_state.thumbnail = info["thumbnail"]

            st.success("Đã lấy thông tin video.")


# =========================
# VIDEO PREVIEW
# =========================

if st.session_state.thumbnail:

    st.subheader("Video đã nhận diện")

    st.image(
        st.session_state.thumbnail,
        width=300
    )

    if st.session_state.author:
        st.write(
            f"**Tác giả:** {st.session_state.author}"
        )

    if st.session_state.video_name:
        st.write(
            f"**Caption:** {st.session_state.video_name}"
        )


# =========================
# DATA INPUT
# =========================

st.divider()

st.subheader("Nhập dữ liệu Analytics")

video_name = st.text_input(
    "Tên / Caption video",
    value=st.session_state.video_name
)

hook = st.text_input(
    "Hook 1–3 giây đầu",
    value=st.session_state.hook,
    placeholder="Ví dụ: Đừng lướt nếu bạn đang..."
)

col1, col2 = st.columns(2)

with col1:

    views = st.number_input(
        "Lượt xem",
        min_value=0,
        value=0,
        step=100
    )

    likes = st.number_input(
        "Lượt thích",
        min_value=0,
        value=0,
        step=10
    )

    comments = st.number_input(
        "Bình luận",
        min_value=0,
        value=0,
        step=1
    )

    shares = st.number_input(
        "Chia sẻ",
        min_value=0,
        value=0,
        step=1
    )

with col2:

    duration = st.number_input(
        "Thời lượng video (giây)",
        min_value=1.0,
        value=20.0,
        step=1.0
    )

    avg_watch = st.number_input(
        "Thời gian xem trung bình (giây)",
        min_value=0.0,
        value=10.0,
        step=0.5
    )

    post_hour = st.slider(
        "Giờ đăng",
        0,
        23,
        20
    )


# =========================
# ANALYSIS
# =========================

if st.button(
    "🚀 Phân tích video",
    type="primary",
    use_container_width=True
):

    if views <= 0:

        st.error(
            "Lượt xem phải lớn hơn 0 để phân tích."
        )

    else:

        safe_views = max(views, 1)

        like_rate = (
            likes / safe_views
        ) * 100

        comment_rate = (
            comments / safe_views
        ) * 100

        share_rate = (
            shares / safe_views
        ) * 100

        engagement_rate = (
            likes
            + comments * 2
            + shares * 3
        ) / safe_views * 100

        retention = (
            avg_watch /
            max(duration, 1)
        ) * 100


        # =========================
        # VIRAL SCORE
        # =========================

        retention_score = min(
            retention / 100,
            1
        ) * 45

        engagement_score = min(
            engagement_rate / 15,
            1
        ) * 35

        share_score = min(
            share_rate / 2,
            1
        ) * 20

        viral_score = round(
            retention_score
            + engagement_score
            + share_score,
            1
        )


        # =========================
        # RESULTS
        # =========================

        st.divider()

        st.subheader("📊 Kết quả")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Viral Score",
                f"{viral_score}/100"
            )

            st.metric(
                "Engagement",
                f"{engagement_rate:.2f}%"
            )

        with c2:

            st.metric(
                "Retention",
                f"{retention:.1f}%"
            )

            st.metric(
                "Share Rate",
                f"{share_rate:.2f}%"
            )


        # =========================
        # PROGRESS
        # =========================

        st.write("**Viral Meter**")

        st.progress(
            min(
                int(viral_score),
                100
            )
        )


        # =========================
        # RATING
        # =========================

        st.subheader("Đánh giá")

        if viral_score >= 80:

            st.success(
                "🔥 Các chỉ số của video đang rất mạnh."
            )

        elif viral_score >= 60:

            st.success(
                "✅ Video có hiệu suất tốt."
            )

        elif viral_score >= 40:

            st.warning(
                "⚠️ Hiệu suất trung bình."
            )

        else:

            st.error(
                "📉 Video đang có nhiều chỉ số yếu."
            )


        # =========================
        # HOOK
        # =========================

        st.subheader("🎣 Hook")

        if not hook:

            st.warning(
                "Chưa nhập Hook để phân tích."
            )

        else:

            words = len(
                hook.split()
            )

            if words <= 12:

                st.success(
                    "Hook ngắn gọn."
                )

            elif words <= 20:

                st.info(
                    "Hook hơi dài."
                )

            else:

                st.warning(
                    "Hook dài. Thử rút xuống khoảng 5–12 từ."
                )


        # =========================
        # RECOMMENDATIONS
        # =========================

        st.subheader("💡 Gợi ý tối ưu")

        tips = []

        if retention < 40:

            tips.append(
                "Thay đổi mạnh 1–3 giây đầu video."
            )

        elif retention < 60:

            tips.append(
                "Cắt bớt các đoạn chậm để tăng retention."
            )

        if like_rate < 5:

            tips.append(
                "Tăng payoff hoặc giá trị cảm xúc để kích thích Like."
            )

        if comment_rate < 0.5:

            tips.append(
                "Thêm câu hỏi cuối video để tăng bình luận."
            )

        if share_rate < 0.5:

            tips.append(
                "Thử nội dung hữu ích, bất ngờ hoặc dễ gửi cho bạn bè."
            )

        if duration > 30 and retention < 60:

            tips.append(
                "Thử phiên bản video ngắn hơn."
            )

        if post_hour < 18 or post_hour > 22:

            tips.append(
                "Test thêm các khung giờ tối rồi so sánh với dữ liệu hiện tại."
            )

        if not tips:

            tips.append(
                "Các chỉ số khá ổn. Tiếp tục thử nhiều Hook khác nhau."
            )

        for tip in tips:

            st.write(
                "• " + tip
            )


        # =========================
        # SAVE HISTORY
        # =========================

        result = {

            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),

            "video": (
                video_name
                or "Untitled"
            ),

            "author":
                st.session_state.author,

            "url":
                st.session_state.tiktok_url,

            "views":
                views,

            "likes":
                likes,

            "comments":
                comments,

            "shares":
                shares,

            "duration":
                duration,

            "avg_watch":
                avg_watch,

            "post_hour":
                post_hour,

            "engagement":
                round(
                    engagement_rate,
                    2
                ),

            "retention":
                round(
                    retention,
                    2
                ),

            "viral_score":
                viral_score,
        }

        st.session_state.history.append(
            result
        )


# =========================
# HISTORY
# =========================

if st.session_state.history:

    st.divider()

    st.subheader("📚 Lịch sử")

    df = pd.DataFrame(
        st.session_state.history
    )

    df = df.sort_values(
        "viral_score",
        ascending=False
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    best = df.iloc[0]

    st.success(
        f"🏆 Video tốt nhất: "
        f"{best['video']} — "
        f"{best['viral_score']}/100"
    )

    csv = df.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        "⬇️ Tải lịch sử CSV",
        csv,
        "tiktok_history.csv",
        "text/csv",
        use_container_width=True
    )

    if st.button(
        "Xóa lịch sử",
        use_container_width=True
    ):

        st.session_state.history = []

        st.rerun()
