import streamlit as st
import pandas as pd
import os
from score_weights import weights

# --- Cấu hình trang ---
st.set_page_config(page_title="TỔNG KẾT TUẦN", page_icon="🏆", layout="wide")

# --- CSS tuỳ chỉnh ---
st.markdown("""
<style>
.main {
    background-color: #f4f7fc;
}
h1, h2, h3, h4 {
    color: #002855;
}
.stButton>button {
    background-color: #0066cc;
    color: white;
    border-radius: 10px;
    font-size: 16px;
    height: 3em;
    width: 100%;
}
.stButton>button:hover {
    background-color: #004c99;
}
.stDataFrame {
    border-radius: 10px;
    background: white;
    padding: 10px;
    box-shadow: 0 0 5px rgba(0,0,0,0.1);
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1200px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

# --- Đường dẫn dữ liệu ---
data_path = "data/Score.xlsx"
os.makedirs("data", exist_ok=True)

if os.path.exists(data_path):
    df = pd.read_excel(data_path)
else:
    df = pd.DataFrame(columns=["Tên Tài Khoản", "LỚP", "Tuần"] + list(weights.keys()) + ["Điểm tổng"])

# --- Hàm tính điểm ---
def tinh_diem(row):
    total = 0
    for col, w in weights.items():
        val = row.get(col)
        if pd.notna(val) and val not in ["", 0]:
            total += w
    return total

# --- Giao diện đầu ---
st.markdown("""
    <h1 style='text-align: center; color: #002855;'>🏆 ỨNG DỤNG TỔNG KẾT THI ĐUA TUẦN</h1>
    <p style='text-align: center; color: gray;'>Phiên bản Streamlit - Thiết kế bởi DANG CAO KY & ChatGPT</p>
""", unsafe_allow_html=True)

# --- Menu ---
menu = st.sidebar.radio("📋 Chức năng", ["Nhập thi đua", "Kết quả lớp"])

# --- Giao diện nhập dữ liệu ---
if menu == "Nhập thi đua":
    st.subheader("📝 Nhập thông tin thi đua")

    col1, col2, col3 = st.columns(3)
    with col1:
        ten_taikhoan = st.text_input("👤 Tên tài khoản")
    with col2:
        lop = st.text_input("🏫 Lớp")
    with col3:
        tuan = st.number_input("📅 Tuần", min_value=1, step=1)

    st.markdown("---")
    st.write("### 🧾 Nhập các vi phạm và điểm cộng")

    form_data = {}
    for c in weights.keys():
        form_data[c] = st.text_input(f"{c}")

    if st.button("💾 Lưu & Tính điểm"):
        row = pd.Series(form_data)
        row["Tên Tài Khoản"] = ten_taikhoan
        row["LỚP"] = lop
        row["Tuần"] = tuan
        row["Điểm tổng"] = tinh_diem(form_data)

        df.loc[len(df)] = row
        try:
            df.to_excel(data_path, index=False)
            st.success(f"✅ Lưu thành công! Điểm tổng: {row['Điểm tổng']}")
        except PermissionError:
            st.error("⚠️ Không thể ghi file. Hãy đóng Excel đang mở rồi thử lại.")

# --- Giao diện kết quả lớp ---
elif menu == "Kết quả lớp":
    st.subheader("📊 Kết quả lớp")
    if len(df) == 0:
        st.info("❗ Chưa có dữ liệu thi đua.")
    else:
        df["Điểm tổng"] = df.apply(tinh_diem, axis=1)

        def highlight_score(val):
            if val >= 50:
                color = "background-color: #a8f0c6;"  # xanh
            elif val >= 0:
                color = "background-color: #fff8b3;"  # vàng
            else:
                color = "background-color: #ffb3b3;"  # đỏ
            return color

        styled_df = df.style.applymap(highlight_score, subset=["Điểm tổng"])
        st.dataframe(styled_df, use_container_width=True)

        # Thống kê tổng hợp
        avg_score = df["Điểm tổng"].mean()
        best_class = df.loc[df["Điểm tổng"].idxmax(), "LỚP"] if not df.empty else "-"
        worst_class = df.loc[df["Điểm tổng"].idxmin(), "LỚP"] if not df.empty else "-"

        st.markdown("### 📈 Tổng quan tuần")
        st.metric("Điểm trung bình", f"{avg_score:.2f}")
        st.metric("Lớp cao nhất", best_class)
        st.metric("Lớp thấp nhất", worst_class)
