import streamlit as st

# Cấu hình giao diện ứng dụng
st.set_page_config(page_title="App Thẩm Định Tín Dụng Toàn Diện 2026", page_icon="🏦", layout="centered")

# --- THÔNG TIN TIÊU ĐỀ ---
st.title("🏦 Hệ Thống Thẩm Định & Phê Duyệt Tín Dụng Tự Động")
st.write("Đánh giá hồ sơ dựa trên: Khả năng trả nợ (DTI), Tài sản bảo đảm (LTV), Pháp lý (Tuổi) và Lịch sử tín dụng (CIC).")
st.markdown("---")

# --- PHẦN NHẬP DỮ LIỆU ĐẦU VÀO ---
st.subheader("📋 Nhập thông tin hồ sơ khách hàng")

# Phân chia thành các Tab để giao diện chuyên nghiệp
tab1, tab2, tab3 = st.tabs(["👤 Khách hàng & Lịch sử CIC", "💰 Tài chính & Khoản vay", "🛡️ Tài sản bảo đảm"])

with tab1:
    stkh = st.number_input("Tuổi của khách hàng (Tuổi):", min_value=1, max_value=100, value=30, step=1)
    
    # Bổ sung điều kiện Lịch sử tín dụng theo yêu cầu của bạn
    cic_status = st.selectbox(
        "Lịch sử tín dụng của khách hàng (CIC):",
        options=[
            "Chưa từng vay (CIC trắng)",
            "Vay đã trả (Lịch sử tốt - Nhóm 1)",
            "Vay nhưng nợ quá hạn (Nhóm 2)",
            "Vay nhưng nợ xấu (Nhóm 3, 4, 5)"
        ]
    )

with tab2:
    stv = st.number_input("Số tiền muốn vay (Triệu đồng):", min_value=0.0, value=500.0, step=10.0)
    tgv = st.number_input("Thời gian vay (Năm):", min_value=0.5, value=5.0, step=0.5)
    lsv = st.number_input("Lãi suất vay (%/năm):", min_value=0.0, value=10.5, step=0.1)
    tn = st.number_input("Thu nhập hàng tháng (Triệu đồng):", min_value=1.0, value=50.0, step=1.0)
    sntgd = st.number_input("Số người trong gia đình (Người):", min_value=1.0, value=3.0, step=1.0)
    ptmc = st.number_input("Số tiền phải trả cho khoản vay cũ (Triệu đồng/tháng):", min_value=0.0, value=0.0, step=0.5)
    CPSH = 5.0  # Chi phí sinh hoạt định mức/người

with tab3:
    gttsdb = st.number_input("Giá trị tài sản bảo đảm (Triệu đồng):", min_value=1.0, value=1000.0, step=10.0)

st.markdown("---")


# --- HÀM LOGIC TÍNH TOÁN VÀ THẨM ĐỊNH ---
def tham_dinh_ho_so(STV, TGV, LSV, TN, SNTGD, PTMC, GTTSDB, STKH, CIC_STATUS):
    # 1. Tính toán số tiền phải trả cho khoản vay mới hàng tháng (Quy đổi LSV % sang thập phân)
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
    
    # 5. Đánh giá điều kiện CIC theo luật tổ chức tín dụng hiện hành
    cic_hop_le = True
    ly_do_cic = ""
    nguong_dti_ap_dung = 0.7  # Tiêu chuẩn DTI chung là 70%
    
    if CIC_STATUS == "Vay nhưng nợ xấu (Nhóm 3, 4, 5)":
        cic_hop_le = False
        ly_do_cic = "Khách hàng có nợ xấu trên hệ thống CIC (Quá hạn > 90 ngày). Hệ thống tự động TỪ CHỐI cấp tín dụng."
    elif CIC_STATUS == "Vay nhưng nợ quá hạn (Nhóm 2)":
        # Một số chính sách siết DTI xuống 50% đối với nhóm có tì vết chậm trả
        nguong_dti_ap_dung = 0.5
        ly_do_cic = "Khách hàng có lịch sử nợ cần chú ý (Nhóm 2). Hệ thống thắt chặt điều kiện: Hạ mức trần DTI cho phép xuống còn 50%."
    elif CIC_STATUS == "Chưa từng vay (CIC trắng)":
        ly_do_cic = "Khách hàng chưa có lịch sử tín dụng. Yêu cầu tăng cường thẩm định thực tế nguồn thu nhập."
    else:
        ly_do_cic = "Lịch sử tín dụng tốt (Nhóm 1). Áp dụng chính sách phê duyệt thông thường."

    # Kiểm tra điều kiện tổng thể để ra quyết định vay
    # Điều kiện: DTI hợp lệ theo ngưỡng riêng + LTV <= 70% + Tuổi hợp lệ + Không có nợ xấu
    duoc_cho_vay = (dti <= nguong_dti_ap_dung) and (ltv <= 0.7) and tuoi_hop_le and cic_hop_le

    return PTMM, dti, ltv, tuoi_hop_le, cic_hop_le, ly_do_cic, nguong_dti_ap_dung, duoc_cho_vay, mau_so_dti


# --- PHẦN NÚT BẤM KÍCH HOẠT VÀ HIỂN THỊ KẾT QUẢ ---
if st.button("🧮 Chạy Hệ Thống Thẩm Định CIC", type="primary"):
    ptmm, dti, ltv, tuoi_hop_le, cic_hop_le, ly_do_cic, nguong_dti, duoc_cho_vay, dong_tien_con_lai = tham_dinh_ho_so(
        stv, tgv, lsv, tn, sntgd, ptmc, gttsdb, stkh, cic_status
    )
    
    st.subheader("🎯 Kết Quả Phân Tích Chỉ Số")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if dti == float('inf'):
            st.metric(label="Chỉ số DTI thực tế", value="Vô cực", delta="Dòng tiền âm", delta_color="inverse")
        else:
            st.metric(label="Chỉ số DTI thực tế", value=f"{dti * 100:.2f}%", delta=f"Ngưỡng áp dụng: ≤ {nguong_dti*100:.0f}%")
    with col2:
        st.metric(label="Chỉ số LTV (Biên thế chấp)", value=f"{ltv * 100:.2f}%", delta="Ngưỡng tối đa: ≤ 70%")
    with col3:
        st.metric(label="Độ tuổi khách hàng", value=f"{int(stkh)} Tuổi", delta="Hợp lệ: 18 - 70")

    st.markdown("---")
    
    # --- ĐƯA RA KẾT LUẬN CUỐI CÙNG ---
    if duoc_cho_vay:
        st.success("🎉 KẾT LUẬN: HỒ SƠ ĐƯỢC PHÊ DUYỆT CHO VAY")
        st.write(f"Khách hàng đủ điều kiện cấp vốn. Nghĩa vụ trả nợ mới: **{ptmm:.2f} triệu đồng/tháng**.")
        st.info(f"💡 **Trạng thái CIC:** {ly_do_cic}")
    else:
        st.error("❌ KẾT LUẬN: HỒ SƠ KHÔNG ĐƯỢC PHÊ DUYỆT")
        st.write("### 🔍 Chi tiết các điểm không đạt tiêu chuẩn kỹ thuật:")
        
        # 1. Sai phạm về Lịch sử tín dụng CIC (Hard Block)
        if not cic_hop_le:
            st.write(f"- **Từ chối do CIC:** {ly_do_cic}")
            
        # 2. Sai phạm về khả năng trả nợ (DTI)
        if dti > nguong_dti:
            if dti == float('inf') or dong_tien_con_lai <= 0:
                st.write("- **Từ chối do DTI:** Thu nhập hàng tháng không đủ chi trả chi phí sinh hoạt tối thiểu của gia đình.")
            else:
                st.write(f"- **Từ chối do DTI:** Chỉ số DTI ({dti * 100:.2f}%) vượt ngưỡng an toàn quy định cho nhóm khách hàng này (≤ {nguong_dti*100:.0f}%).")
                
        # 3. Sai phạm về giá trị tài sản thế chấp (LTV)
        if ltv > 0.7:
            st.write(f"- **Từ chối do LTV:** Tỷ lệ cho vay trên tài sản bảo đảm ({ltv * 100:.2f}%) vượt quá hạn mức tối đa quy định (70%).")
            
        # 4. Sai phạm về mặt Pháp lý / Độ tuổi
        if not tuoi_hop_le:
            st.write(f"- **Từ chối do Độ Tuổi:** Khách hàng ({int(stkh)} tuổi) nằm ngoài khung tuổi quy định (18 - 70 tuổi).")
