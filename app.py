import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="TeaHack TikTok Growth Booster",
    page_icon="🚀",
    layout="wide"
)

# =========================
# SESSION
# =========================

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# HEADER
# =========================

st.title("🚀 TeaHack TikTok Growth Booster")

st.caption(
    "Phân tích video và tạo kế hoạch tối ưu để tăng lượt xem, tương tác và khả năng phân phối."
)

# =========================
# INPUT
# =========================

st.subheader("Thông tin video")

video_name = st.text_input(
    "Tên video",
    placeholder="Ví dụ: Video AI biến hình"
)

topic = st.text_input(
    "Chủ đề video",
    placeholder="Ví dụ: AI, anime, review, hài..."
)

hook = st.text_input(
    "Hook 1–3 giây đầu",
    placeholder="Ví dụ: Đừng lướt nếu bạn đang..."
)

caption = st.text_area(
    "Caption hiện tại",
    placeholder="#fyp #xh..."
)

col1, col2 = st.columns(2)

with col1:

    views = st.number_input(
        "Lượt xem",
        min_value=0,
        value=1000,
        step=100
    )

    likes = st.number_input(
        "Lượt thích",
        min_value=0,
        value=100,
        step=10
    )

    comments = st.number_input(
        "Bình luận",
        min_value=0,
        value=10,
        step=1
    )

    shares = st.number_input(
        "Chia sẻ",
        min_value=0,
        value=5,
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
        "Thời gian xem trung bình",
        min_value=0.0,
        value=12.0,
        step=0.5
    )

    post_hour = st.slider(
        "Giờ đăng",
        0,
        23,
        20
    )

    target_views = st.number_input(
        "Mục tiêu lượt xem",
        min_value=100,
        value=10000,
        step=1000
    )

# =========================
# HELPERS
# =========================

def generate_captions(topic, hook):

    base_topic = topic if topic else "video này"

    options = [
        f"{hook or 'Coi tới cuối mới thấy bất ngờ'} 👀 #{base_topic.replace(' ', '')}",
        f"Tưởng bình thường cho tới đoạn cuối 💀 #{base_topic.replace(' ', '')}",
        f"Ai xem tới cuối mới hiểu 😳 #{base_topic.replace(' ', '')}",
        f"Không ngờ {base_topic} lại ra kết quả như này...",
        f"Rate kết quả này từ 1–10 đi 👇 #{base_topic.replace(' ', '')}",
    ]

    return options


def generate_hashtags(topic):

    clean = topic.replace(" ", "") if topic else "viral"

    return [
        f"#{clean}",
        "#fyp",
        "#xuhuong",
        "#viral",
        "#tiktokvn",
        "#trend",
    ]


def generate_ctas():

    return [
        "Bạn chấm video này mấy điểm?",
        "Muốn phần 2 không?",
        "Gửi cho đứa bạn cần xem cái này.",
        "Bạn chọn phiên bản nào?",
        "Comment chủ đề tiếp theo mình làm.",
    ]


# =========================
# ANALYZE
# =========================

if st.button(
    "🚀 TẠO KẾT QUẢ",
    type="primary",
    use_container_width=True
):

    if views <= 0:
        st.error("Lượt xem phải lớn hơn 0.")
        st.stop()

    # =========================
    # METRICS
    # =========================

    like_rate = likes / views * 100
    comment_rate = comments / views * 100
    share_rate = shares / views * 100

    retention = (
        avg_watch /
        max(duration, 1)
    ) * 100

    engagement = (
        likes +
        comments * 2 +
        shares * 3
    ) / views * 100

    # =========================
    # SCORE
    # =========================

    retention_score = min(
        retention / 100,
        1
    ) * 45

    engagement_score = min(
        engagement / 15,
        1
    ) * 35

    share_score = min(
        share_rate / 2,
        1
    ) * 20

    growth_score = round(
        retention_score +
        engagement_score +
        share_score,
        1
    )

    # =========================
    # RESULT
    # =========================

    st.divider()

    st.header("📊 Kết quả")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Growth Score",
            f"{growth_score}/100"
        )

        st.metric(
            "Engagement",
            f"{engagement:.2f}%"
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

    st.progress(
        min(int(growth_score), 100)
    )

    # =========================
    # DIAGNOSIS
    # =========================

    st.header("🧠 Chẩn đoán")

    if retention < 40:
        st.error(
            "Retention thấp — phần đầu video chưa giữ được người xem."
        )

    elif retention < 60:
        st.warning(
            "Retention trung bình — nên cắt các đoạn chậm."
        )

    else:
        st.success(
            "Retention đang khá tốt."
        )

    if like_rate < 3:
        st.warning(
            "Like rate thấp — nội dung chưa tạo đủ phản ứng."
        )

    if comment_rate < 0.3:
        st.warning(
            "Comment thấp — cần thêm câu hỏi hoặc tranh luận."
        )

    if share_rate < 0.3:
        st.warning(
            "Share thấp — cần tăng yếu tố bất ngờ hoặc hữu ích."
        )

    # =========================
    # HOOK
    # =========================

    st.header("🎣 Hook")

    hook_words = len(hook.split())

    if not hook:

        st.warning(
            "Chưa nhập Hook."
        )

    elif hook_words <= 10:

        st.success(
            "Hook ngắn và dễ tiếp nhận."
        )

    elif hook_words <= 18:

        st.info(
            "Hook hơi dài. Có thể rút ngắn."
        )

    else:

        st.warning(
            "Hook quá dài. Thử giảm xuống 5–10 từ."
        )

    # =========================
    # CAPTIONS
    # =========================

    st.header("🔥 Caption đề xuất")

    for x in generate_captions(topic, hook):

        st.code(
            x,
            language=None
        )

    # =========================
    # HASHTAGS
    # =========================

    st.header("#️⃣ Hashtag")

    tags = generate_hashtags(topic)

    st.code(
        " ".join(tags),
        language=None
    )

    # =========================
    # CTA
    # =========================

    st.header("💬 CTA tăng tương tác")

    for cta in generate_ctas():

        st.write(
            "• " + cta
        )

    # =========================
    # TARGET
    # =========================

    st.header("🎯 Mục tiêu")

    multiplier = target_views / views

    estimated_likes = round(
        likes * multiplier
    )

    estimated_comments = round(
        comments * multiplier
    )

    estimated_shares = round(
        shares * multiplier
    )

    st.write(
        f"Nếu video giữ được tỷ lệ hiện tại và đạt **{target_views:,} view**, "
        f"các chỉ số tương ứng sẽ khoảng:"
    )

    t1, t2, t3 = st.columns(3)

    t1.metric(
        "Like",
        f"{estimated_likes:,}"
    )

    t2.metric(
        "Comment",
        f"{estimated_comments:,}"
    )

    t3.metric(
        "Share",
        f"{estimated_shares:,}"
    )

    # =========================
    # ACTION PLAN
    # =========================

    st.header("📈 Kế hoạch video tiếp theo")

    plan = []

    if retention < 50:
        plan.append(
            "Đưa cảnh mạnh nhất vào 1 giây đầu."
        )

    if duration > 30 and retention < 60:
        plan.append(
            "Tạo thêm phiên bản ngắn hơn 15–25 giây."
        )

    if share_rate < 0.5:
        plan.append(
            "Thêm yếu tố khiến người xem muốn gửi video cho bạn bè."
        )

    if comment_rate < 0.5:
        plan.append(
            "Kết thúc video bằng một câu hỏi ngắn."
        )

    if likes / views * 100 < 5:
        plan.append(
            "Tăng payoff ở cuối video."
        )

    plan.append(
        "Test ít nhất 3 Hook khác nhau cho cùng một ý tưởng."
    )

    plan.append(
        "So sánh kết quả sau mỗi video thay vì chỉ nhìn tổng view."
    )

    for i, item in enumerate(plan, 1):

        st.write(
            f"**{i}.** {item}"
        )

    # =========================
    # SAVE
    # =========================

    st.session_state.history.append({

        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),

        "video":
            video_name or "Untitled",

        "views":
            views,

        "likes":
            likes,

        "comments":
            comments,

        "shares":
            shares,

        "retention":
            round(retention, 2),

        "engagement":
            round(engagement, 2),

        "growth_score":
            growth_score
    })

# =========================
# HISTORY
# =========================

if st.session_state.history:

    st.divider()

    st.header("📚 Lịch sử video")

    df = pd.DataFrame(
        st.session_state.history
    )

    df = df.sort_values(
        "growth_score",
        ascending=False
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    best = df.iloc[0]

    st.success(
        f"🏆 Video có chỉ số tốt nhất: "
        f"{best['video']} — "
        f"{best['growth_score']}/100"
    )
