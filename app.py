import streamlit as st

# Cấu hình giao diện ứng dụng
st.set_page_config(page_title="App Thẩm Định Tín Dụng Toàn Diện 2026", page_icon="🏦", layout="centered")

# --- THÔNG TIN TIÊU ĐỀ ---
st.title("🏦 Hệ Thống Thẩm Định Tín Dụng Tự Động")
st.write("Đánh giá toàn diện dựa trên 3 trụ cột: Khả năng trả nợ (DTI), Tài sản bảo đảm (LTV) và Pháp lý khách hàng (Tuổi).")
st.markdown("---")

# --- PHẦN NHẬP DỮ LIỆU ĐẦU VÀO ---
st.subheader("📋 Nhập thông tin hồ sơ khách hàng")

# Phân chia thành các Tab để giao diện chuyên nghiệp hơn
tab1, tab2, tab3 = st.tabs(["👤 Khách hàng & Khoản vay", "💰 Tài chính & Phụ thuộc", "🛡️ Tài sản bảo đảm"])

with tab1:
    stkh = st.number_input("Tuổi của khách hàng (Tuổi):", min_value=1, max_value=100, value=30, step=1)
    stv = st.number_input("Số tiền muốn vay (Triệu đồng):", min_value=0.0, value=500.0, step=10.0)
    tgv = st.number_input("Thời gian vay (Năm):", min_value=0.5, value=5.0, step=0.5)
    lsv = st.number_input("Lại suất vay (%/năm):", min_value=0.0, value=10.5, step=0.1)

with tab2:
    tn = st.number_input("Thu nhập hàng tháng (Triệu đồng):", min_value=1.0, value=50.0, step=1.0)
    sntgd = st.number_input("Số người trong gia đình (Người):", min_value=1.0, value=3.0, step=1.0)
    ptmc = st.number_input("Số tiền phải trả cho khoản vay cũ (Triệu đồng/tháng):", min_value=0.0, value=0.0, step=0.5)
    CPSH = 5.0  # Chi phí sinh hoạt mặc định/người

with tab3:
    gttsdb = st.number_input("Giá trị tài sản bảo đảm (Triệu đồng):", min_value=1.0, value=1000.0, step=10.0)

st.markdown("---")

# --- HÀM LOGIC TÍNH TOÁN AN TOÀN ---
def tham_dinh_ho_so(STV, TGV, LSV, TN, SNTGD, PTMC, GTTSDB, STKH):
    # 1. Tính toán số tiền phải trả cho khoản vay mới hàng tháng (Quy đổi LSV từ % sang thập phân)
    PTMM = (STV / (TGV * 12)) + (STV * (LSV / 100) / 12)
    
    # 2. Tính toán DTI (Xử lý bẫy lỗi chia cho số âm hoặc bằng 0)
    mau_so_dti = TN - (SNTGD * CPSH)
    if mau_so_dti <= 0:
        dti = float('inf')
    else:
        dti = (PTMC + PTMM) / mau_so_dti
        
    # 3. Tính toán LTV (Tỷ lệ cho vay trên giá trị tài sản)
    ltv = STV / GTTSDB
    
    # 4. Kiểm tra điều kiện độ tuổi
    tuoi_hop_le = 18 <= STKH <= 70
    
    return PTMM, dti, ltv, tuoi_hop_le, mau_so_dti

# --- PHẦN NÚT BẤM KÍCH HOẠT VÀ HIỂN THỊ KẾT QUẢ ---
if st.button("🧮 Chạy Hệ Thống Thẩm Định", type="primary"):
    ptmm, dti, ltv, tuoi_hop_le, dong_tien_con_lai = tham_dinh_ho_so(stv, tgv, lsv, tn, sntgd, ptmc, gttsdb, stkh)
    
    st.subheader("🎯 Chỉ Số Thẩm Định Thực Tế")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if dti == float('inf'):
            st.metric(label="Chỉ số DTI (Nợ/Thu nhập)", value="Vô cực", delta="Rủi ro cao", delta_color="inverse")
        else:
            st.metric(label="Chỉ số DTI (Nợ/Thu nhập)", value=f"{dti * 100:.2f}%", delta="Mục tiêu ≤ 70%")
    with col2:
        st.metric(label="Chỉ số LTV (Nợ/Tài sản)", value=f"{ltv * 100:.2f}%", delta="Mục tiêu ≤ 70%")
    with col3:
        st.metric(label="Độ tuổi khách hàng", value=f"{int(stkh)} Tuổi", delta="Hợp lệ: 18 - 70")

    st.markdown("---")
    
    # --- ĐƯA RA KẾT LUẬN ---
    # Điều kiện phê duyệt: DTI <= 70% VÀ LTV <= 70% VÀ tuổi từ 18 đến 70
    duoc_cho_vay = (dti <= 0.7) and (ltv <= 0.7) and tuoi_hop_le
    
    if duoc_cho_vay:
        st.success("🎉 KẾT LUẬN: HỒ SƠ ĐƯỢC PHÊ DUYỆT CHO VAY")
        st.write(f"Khách hàng thỏa mãn tất cả các điều kiện tín dụng với nghĩa vụ trả nợ mới là **{ptmm:.2f} triệu đồng/tháng**.")
    else:
        st.error("❌ KẾT LUẬN: HỒ SƠ KHÔNG ĐƯỢC CHO VAY")
        st.write("### 🔍 Chi tiết các điểm chưa đạt tiêu chuẩn:")
        
        if dti > 0.7:
            if dti == float('inf') or dong_tien_con_lai <= 0:
                st.write("- **DTI Không Đạt:** Thu nhập hàng tháng bị âm hoặc không đủ bù đắp chi phí sinh hoạt định mức của gia đình.")
            else:
                st.write(f"- **DTI Không Đạt:** Chỉ số DTI ({dti * 100:.2f}%) vượt ngưỡng an toàn cho phép (70%).")
                
        if ltv > 0.7:
            st.write(f"- **LTV Không Đạt:** Tỷ lệ cho vay trên tài sản ({ltv * 100:.2f}%) vượt quá hạn mức tối đa của tài sản bảo đảm (70%).")
            
        if not tuoi_hop_le:
            st.write(f"- **Pháp lý Không Đạt:** Độ tuổi khách hàng ({int(stkh)} tuổi) nằm ngoài khung tuổi lao động quy định (18 - 70 tuổi).")
