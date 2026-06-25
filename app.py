import streamlit as st

# Cấu hình giao diện ứng dụng
st.set_page_config(page_title="App Đánh Giá Chỉ Số DTI & Cấp Tín Dụng", page_icon="🏦", layout="centered")

# --- THÔNG TIN TIÊU ĐỀ ---
st.title("🏦 Ứng Dụng Thẩm Định Tín Dụng & Tính Chỉ Số DTI")
st.write("Hỗ trợ tính toán tỷ lệ nợ trên thu nhập và đưa ra quyết định cho vay tự động.")
st.markdown("---")

# --- PHẦN NHẬP DỮ LIỆU ĐẦU VÀO ---
st.subheader("📋 Nhập thông tin tài chính người vay")

# Sử dụng st.columns để phân chia giao diện cho gọn gàng
col1, col2 = st.columns(2)

with col1:
    stv = st.number_input("1. Số tiền muốn vay (Triệu đồng):", min_value=0.0, value=100.0, step=10.0)
    tgv = st.number_input("2. Thời gian vay (Năm):", min_value=0.5, value=2.0, step=0.5)
    lsv = st.number_input("3. Lãi suất vay (%/năm):", min_value=0.0, value=10.5, step=0.5)

with col2:
    tn = st.number_input("4. Thu nhập hàng tháng (Triệu đồng):", min_value=1.0, value=30.0, step=1.0)
    sntgd = st.number_input("5. Số người trong gia đình (Người):", min_value=1.0, value=3.0, step=1.0)
    ptmc = st.number_input("6. Số tiền phải trả cho khoản vay cũ (Triệu đồng/tháng):", min_value=0.0, value=0.0, step=0.5)

# Chi phí sinh hoạt mặc định (theo code gốc của bạn)
CPSH = 5.0

st.markdown("---")

# --- HÀM LOGIC TÍNH TOÁN THEO CÔNG THỨC GỐC ---
def tinh_toan_dti(STV, TGV, LSV, TN, SNTGD, PTMC):
    # Công thức gốc của bạn để tính số tiền phải trả khoản vay mới hàng tháng
    # (LSV chia cho 100 để đổi từ % sang hệ số phân số)
    PTMM = (STV / (TGV * 12)) + (STV * (LSV / 100) / 12)
    
    # Mẫu số: Thu nhập trừ chi phí sinh hoạt gia đình
    mau_so = TN - (SNTGD * CPSH)
    
    # Tránh lỗi chia cho 0 hoặc mẫu số bị âm
    if mau_so <= 0:
        return PTMM, float('inf'), mau_so
        
    # Công thức tính DTI gốc của bạn
    DTI = (PTMC + PTMM) / mau_so
    return PTMM, DTI, mau_so

# --- PHẦN NÚT BẤM KÍCH HOẠT VÀ HIỂN THỊ KẾT QUẢ ---
if st.button("🧮 Thẩm Định Khoản Vay", type="primary"):
    ptmm, dti, dong_tien_con_lai = tinh_toan_dti(stv, tgv, lsv, tn, sntgd, ptmc)
    
    st.subheader("🎯 Kết Quả Phân Tích")
    
    # Hiển thị các chỉ số cốt lõi dưới dạng thẻ Metric
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Số tiền trả khoản vay mới (Tháng đầu)", value=f"{ptmm:.2f} Triệu")
        st.metric(label="Dòng tiền còn lại sau sinh hoạt phí", value=f"{dong_tien_con_lai:.2f} Triệu")
    with c2:
        if dti == float('inf'):
            st.metric(label="Chỉ số DTI của bạn", value="Vô cực (Thu nhập < Chi phí)")
        else:
            st.metric(label="Chỉ số DTI của bạn", value=f"{dti * 100:.2f}%")

    st.markdown("---")
    
    # --- BIỆN LUẬN ĐIỀU KIỆN ĐƯỢC CHO VAY ---
    if dti <= 0.7:
        st.success("🎉 KẾT LUẬN: ĐƯỢC CHO VAY")
        st.write("Khách hàng thỏa mãn điều kiện chỉ số DTI nằm trong ngưỡng an toàn (≤ 70%).")
    else:
        st.error("❌ KẾT LUẬN: KHÔNG ĐƯỢC CHO VAY")
        st.write("### [Lý do từ chối]:")
        if dti == float('inf') or dong_tien_con_lai <= 0:
            st.write("- Thu nhập hàng tháng không đủ chi trả cho chi phí sinh hoạt định mức của gia đình.")
        else:
            st.write(f"- Chỉ số DTI hiện tại ({dti * 100:.2f}%) đã vượt quá ngưỡng rủi ro cho phép (70%).")
