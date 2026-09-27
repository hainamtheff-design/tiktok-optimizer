import streamlit as st
from urllib.parse import urlparse

st.header("🚀 TikTok Real Growth")

video_url = st.text_input(
    "Dán link video TikTok",
    placeholder="Link video TikTok của bạn"
)

def valid_tiktok_url(url):
    try:
        host = urlparse(url).netloc.lower()
        return host.endswith("tiktok.com")
    except:
        return False


goal = st.selectbox(
    "Mục tiêu",
    [
        "Tăng lượt xem",
        "Tăng người theo dõi",
        "Tăng lượt xem hồ sơ"
    ]
)

budget = st.number_input(
    "Ngân sách dự kiến",
    min_value=50000,
    value=100000,
    step=50000
)

days = st.slider(
    "Số ngày chạy",
    1,
    7,
    1
)

if st.button(
    "🚀 TẠO CHIẾN DỊCH",
    type="primary",
    use_container_width=True
):

    if not video_url:
        st.error("Hãy nhập link TikTok.")

    elif not valid_tiktok_url(video_url):
        st.error("Link TikTok không hợp lệ.")

    else:

        daily_budget = budget / days

        st.success(
            "Đã tạo kế hoạch."
        )

        st.subheader("Kế hoạch")

        st.write(
            f"**Mục tiêu:** {goal}"
        )

        st.write(
            f"**Ngân sách:** {budget:,.0f} VNĐ"
        )

        st.write(
            f"**Thời gian:** {days} ngày"
        )

        st.write(
            f"**Ngân sách/ngày:** "
            f"{daily_budget:,.0f} VNĐ"
        )

        st.info(
            "Bước tiếp theo: mở TikTok Promote, "
            "chọn chính video này và nhập cấu hình trên."
        )
    
