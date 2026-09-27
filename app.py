import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="TeaHack TikTok Optimizer",
    page_icon="📈",
    layout="wide"
)

# =========================
# SESSION HISTORY
# =========================

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# HEADER
# =========================

st.title("TeaHack TikTok Optimizer")

st.caption(
    "Nhập số liệu video TikTok trực tiếp để phân tích hiệu suất."
)

st.info(
    "Viral Score là điểm phân tích tham khảo do tool tính toán, "
    "không phải điểm chính thức của TikTok."
)

# =========================
# INPUT
# =========================

st.subheader("Nhập dữ liệu video")

video_name = st.text_input(
    "Tên video",
    placeholder="Ví dụ: Video review AI #1"
)

hook = st.text_input(
    "Hook 1–3 giây đầu",
    placeholder="Ví dụ: Đừng lướt nếu bạn đang làm TikTok..."
)

col1, col2 = st.columns(2)

with col1:
    views = st.number_input(
        "Lượt xem",
        min_value=0,
        step=100,
        value=1000
    )

    likes = st.number_input(
        "Lượt thích",
        min_value=0,
        step=10,
        value=100
    )

    comments = st.number_input(
        "Bình luận",
        min_value=0,
        step=1,
        value=10
    )

    shares = st.number_input(
        "Chia sẻ",
        min_value=0,
        step=1,
        value=5
    )

with col2:
    duration = st.number_input(
        "Thời lượng video (giây)",
        min_value=1.0,
        step=1.0,
        value=20.0
    )

    avg_watch = st.number_input(
        "Thời gian xem trung bình (giây)",
        min_value=0.0,
        step=0.5,
        value=12.0
    )

    post_hour = st.slider(
        "Giờ đăng",
        min_value=0,
        max_value=23,
        value=20
    )

# =========================
# ANALYZE
# =========================

if st.button(
    "Phân tích video",
    type="primary",
    use_container_width=True
):

    safe_views = max(views, 1)

    like_rate = likes / safe_views * 100
    comment_rate = comments / safe_views * 100
    share_rate = shares / safe_views * 100

    engagement_rate = (
        likes +
        comments * 2 +
        shares * 3
    ) / safe_views * 100

    retention = (
        avg_watch / max(duration, 1)
    ) * 100

    # =========================
    # VIRAL SCORE 0–100
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
        retention_score +
        engagement_score +
        share_score,
        1
    )

    # =========================
    # DISPLAY METRICS
    # =========================

    st.divider()

    st.subheader("Kết quả phân tích")

    m1, m2 = st.columns(2)

    with m1:
        st.metric(
            "Viral Score",
            f"{viral_score}/100"
        )

        st.metric(
            "Engagement",
            f"{engagement_rate:.2f}%"
        )

    with m2:
        st.metric(
            "Retention",
            f"{retention:.1f}%"
        )

        st.metric(
            "Share Rate",
            f"{share_rate:.2f}%"
        )

    # =========================
    # SCORE RATING
    # =========================

    st.subheader("Đánh giá video")

    if viral_score >= 80:
        st.success(
            "🔥 Video đang có các chỉ số rất mạnh."
        )

    elif viral_score >= 60:
        st.success(
            "✅ Video có hiệu suất tốt."
        )

    elif viral_score >= 40:
        st.warning(
            "⚠️ Video ở mức trung bình, còn nhiều chỗ tối ưu."
        )

    else:
        st.error(
            "📉 Video đang có tín hiệu yếu."
        )

    # =========================
    # RETENTION
    # =========================

    st.subheader("Retention")

    if retention >= 80:
        st.success(
            "Retention rất tốt. Cấu trúc video đang giữ người xem tốt."
        )

    elif retention >= 60:
        st.info(
            "Retention khá tốt. Có thể thử rút gọn vài đoạn chậm."
        )

    elif retention >= 40:
        st.warning(
            "Retention trung bình. Nên đưa nội dung hấp dẫn lên sớm hơn."
        )

    else:
        st.error(
            "Retention thấp. Cần thay đổi mạnh phần mở đầu."
        )

    # =========================
    # HOOK ANALYSIS
    # =========================

    st.subheader("Phân tích Hook")

    if not hook:
        st.warning(
            "Chưa nhập Hook."
        )

    else:
        hook_length = len(
            hook.split()
        )

        if hook_length <= 12:
            st.success(
                "Hook khá ngắn gọn, phù hợp TikTok."
            )

        elif hook_length <= 20:
            st.info(
                "Hook hơi dài. Có thể rút gọn thêm."
            )

        else:
            st.warning(
                "Hook khá dài. Nên rút xuống khoảng 5–12 từ."
            )

    # =========================
    # AUTO RECOMMENDATIONS
    # =========================

    st.subheader("Gợi ý tối ưu")

    tips = []

    if retention < 50:
        tips.append(
            "Đưa cảnh mạnh nhất hoặc câu gây tò mò vào 1–2 giây đầu."
        )

    if like_rate < 5:
        tips.append(
            "Thử làm nội dung tạo cảm xúc hoặc giá trị rõ hơn để tăng Like."
        )

    if comment_rate < 0.5:
        tips.append(
            "Cuối video thêm câu hỏi khiến người xem muốn bình luận."
        )

    if share_rate < 0.5:
        tips.append(
            "Tăng yếu tố bất ngờ, hữu ích hoặc khiến người xem muốn gửi cho bạn bè."
        )

    if duration > 30 and retention < 60:
        tips.append(
            "Video khá dài so với retention hiện tại. Thử cắt ngắn."
        )

    if 18 <= post_hour <= 22:
        tips.append(
            "Giờ đăng đang nằm trong khung buổi tối — tiếp tục test thêm dữ liệu."
        )
    else:
        tips.append(
            "Thử test thêm khung 18:00–22:00 và so sánh hiệu suất."
        )

    if not tips:
        tips.append(
            "Các chỉ số hiện khá ổn. Hãy thử nhiều phiên bản Hook để tìm bản mạnh nhất."
        )

    for tip in tips:
        st.write("•", tip)

    # =========================
    # SAVE TO HISTORY
    # =========================

    result = {
        "time_analyzed": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),
        "video": video_name or "Untitled",
        "hook": hook,
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "duration_sec": duration,
        "avg_watch_sec": avg_watch,
        "post_hour": post_hour,
        "engagement_rate": round(
            engagement_rate,
            2
        ),
        "retention": round(
            retention,
            2
        ),
        "share_rate": round(
            share_rate,
            2
        ),
        "viral_score": viral_score
    }

    st.session_state.history.append(
        result
    )

# =========================
# HISTORY
# =========================

if st.session_state.history:

    st.divider()

    st.subheader("Lịch sử phân tích")

    history_df = pd.DataFrame(
        st.session_state.history
    )

    history_df = history_df.sort_values(
        "viral_score",
        ascending=False
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # BEST VIDEO
    # =========================

    best = history_df.iloc[0]

    st.success(
        f"🏆 Video tốt nhất hiện tại: "
        f"{best['video']} — "
        f"{best['viral_score']}/100"
    )

    # =========================
    # DOWNLOAD HISTORY
    # =========================

    csv = history_df.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        "Tải lịch sử CSV",
        data=csv,
        file_name="tiktok_analysis_history.csv",
        mime="text/csv",
        use_container_width=True
    )

    # =========================
    # CLEAR
    # =========================

    if st.button(
        "Xóa lịch sử",
        use_container_width=True
    ):
        st.session_state.history = []
        st.rerun()
