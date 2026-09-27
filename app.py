# app.py
# pip install streamlit pandas plotly

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="TeaHack TikTok Optimizer",
    page_icon="📈",
    layout="wide"
)

st.title("TeaHack TikTok Optimizer")
st.caption("Phân tích dữ liệu video để tối ưu lượt xem và tương tác tự nhiên.")

uploaded = st.file_uploader(
    "Tải CSV dữ liệu TikTok",
    type=["csv"]
)

st.info("""
CSV nên có các cột:

posted_at, views, likes, comments, shares, duration_sec, avg_watch_sec, hook
""")

if uploaded:
    df = pd.read_csv(uploaded)

    required = [
        "posted_at",
        "views",
        "likes",
        "comments",
        "shares",
        "duration_sec",
        "avg_watch_sec"
    ]

    missing = [x for x in required if x not in df.columns]

    if missing:
        st.error(f"Thiếu cột: {', '.join(missing)}")
        st.stop()

    df["posted_at"] = pd.to_datetime(df["posted_at"])

    # thời gian
    df["hour"] = df["posted_at"].dt.hour
    df["weekday"] = df["posted_at"].dt.day_name()

    # engagement
    df["engagement"] = (
        df["likes"] +
        df["comments"] * 2 +
        df["shares"] * 3
    )

    df["engagement_rate"] = (
        df["engagement"] /
        df["views"].replace(0, 1)
    ) * 100

    # retention
    df["retention"] = (
        df["avg_watch_sec"] /
        df["duration_sec"].replace(0, 1)
    ) * 100

    # viral score
    df["viral_score"] = (
        df["engagement_rate"] * 0.4 +
        df["retention"] * 0.4 +
        (df["shares"] / df["views"].replace(0, 1) * 100) * 0.2
    )

    # dashboard
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Tổng View",
        f"{int(df['views'].sum()):,}"
    )

    col2.metric(
        "Tổng Like",
        f"{int(df['likes'].sum()):,}"
    )

    col3.metric(
        "Engagement TB",
        f"{df['engagement_rate'].mean():.2f}%"
    )

    col4.metric(
        "Retention TB",
        f"{df['retention'].mean():.1f}%"
    )

    st.divider()

    # giờ đăng tốt nhất
    hour_stats = (
        df.groupby("hour")
        .agg(
            views=("views", "mean"),
            engagement=("engagement_rate", "mean"),
            retention=("retention", "mean")
        )
        .reset_index()
    )

    hour_stats["score"] = (
        hour_stats["engagement"] * 0.5 +
        hour_stats["retention"] * 0.5
    )

    best_hour = hour_stats.sort_values(
        "score",
        ascending=False
    ).iloc[0]

    st.subheader("Giờ đăng đề xuất")

    st.success(
        f"Khoảng {int(best_hour['hour'])}:00 "
        f"đang có hiệu suất tốt nhất."
    )

    fig = px.bar(
        hour_stats,
        x="hour",
        y="views",
        title="View trung bình theo giờ đăng"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # video tốt nhất
    st.subheader("Video hiệu quả nhất")

    top = df.sort_values(
        "viral_score",
        ascending=False
    ).head(10)

    columns = [
        "posted_at",
        "views",
        "likes",
        "comments",
        "shares",
        "engagement_rate",
        "retention",
        "viral_score"
    ]

    if "hook" in df.columns:
        columns.insert(1, "hook")

    st.dataframe(
        top[columns],
        use_container_width=True
    )

    # hook analyzer
    if "hook" in df.columns:

        st.subheader("Hook hiệu quả")

        hook_stats = (
            df.groupby("hook")
            .agg(
                views=("views", "mean"),
                retention=("retention", "mean"),
                engagement=("engagement_rate", "mean")
            )
            .reset_index()
        )

        hook_stats["score"] = (
            hook_stats["retention"] * 0.6 +
            hook_stats["engagement"] * 0.4
        )

        hook_stats = hook_stats.sort_values(
            "score",
            ascending=False
        )

        st.dataframe(
            hook_stats,
            use_container_width=True
        )

    st.divider()

    st.subheader("Gợi ý tự động")

    avg_retention = df["retention"].mean()
    avg_engagement = df["engagement_rate"].mean()

    tips = []

    if avg_retention < 35:
        tips.append(
            "Retention thấp → rút ngắn phần mở đầu và đưa cảnh mạnh nhất vào 1–2 giây đầu."
        )

    elif avg_retention < 60:
        tips.append(
            "Retention ổn → thử tăng tốc dựng và tạo chuyển cảnh ở mỗi 2–4 giây."
        )

    else:
        tips.append(
            "Retention rất tốt → giữ cấu trúc video hiện tại và thử nhiều chủ đề tương tự."
        )

    if avg_engagement < 3:
        tips.append(
            "Tỷ lệ tương tác thấp → thêm câu hỏi hoặc CTA tự nhiên ở cuối video."
        )

    share_rate = (
        df["shares"].sum() /
        max(df["views"].sum(), 1)
    ) * 100

    if share_rate < 0.5:
        tips.append(
            "Share thấp → ưu tiên nội dung gây bất ngờ, hữu ích hoặc khiến người xem muốn gửi cho bạn bè."
        )

    for tip in tips:
        st.write("•", tip)

    st.subheader("Kế hoạch video tiếp theo")

    best_duration = (
        df.assign(
            duration_group=pd.cut(
                df["duration_sec"],
                bins=[0, 10, 20, 30, 60, 120, 9999],
                labels=[
                    "0-10s",
                    "10-20s",
                    "20-30s",
                    "30-60s",
                    "60-120s",
                    "120s+"
                ]
            )
        )
        .groupby("duration_group", observed=False)["viral_score"]
        .mean()
        .idxmax()
    )

    st.write(
        f"""
**Giờ đăng:** {int(best_hour['hour'])}:00

**Độ dài nên thử:** {best_duration}

**Ưu tiên:** Hook mạnh trong 1–2 giây đầu → nội dung chính → payoff → CTA ngắn.
"""
    )
