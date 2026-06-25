import streamlit as st
# 1. Nhập dữ liệu đầu vào (Đã sửa lại đơn vị hiển thị phù hợp)
STV = float(input("Nhập số tiền muốn vay (Triệu đồng): "))
TGV = float(input("Nhập thời gian vay (Năm): "))
LSV = float(input("Nhập lãi suất vay hàng năm (%/năm): "))
TN = float(input("Nhập thu nhập hàng tháng (Triệu đồng): "))
SNTGD = float(input("Nhập số người trong gia đình (Người): "))

CPSH_dinh_muc = 5.0  # Chi phí sinh hoạt định mức/người (Triệu đồng)
PTMC = float(input("Nhập số tiền phải trả cho khoản vay cũ (Triệu đồng): "))

# 2. Tính toán các thông số tài chính theo chuẩn ngân hàng
tong_so_thang = TGV * 12
lai_suat_thang = (LSV / 100) / 12

# Tính số tiền trả định kỳ hàng tháng (Phương pháp định kỳ bằng nhau - Annuity)
if lai_suat_thang > 0:
    PTMM = STV * (lai_suat_thang * (1 + lai_suat_thang)**tong_so_thang) / ((1 + lai_suat_thang)**tong_so_thang - 1)
else:
    PTMM = STV / tong_so_thang  # Trường hợp hy hữu: Lãi suất 0%

# Chi phí sinh hoạt gia đình
tong_chi_phi_sh = SNTGD * CPSH_dinh_muc

# 3. Tính toán chỉ số đánh giá (DTI chuẩn và DTI hiệu chỉnh theo chi phí)
# DTI chuẩn = Tổng nợ / Tổng thu nhập
DTI_chuan = (PTMC + PTMM) / TN 

# 4. Biện luận điều kiện cấp tín dụng
print("\n" + "="*30)
print(f"SỐ TIỀN PHẢI TRẢ CHO KHOẢN VAY MỚI: {PTMM:.2f} Triệu đồng/tháng")
print(f"CHỈ SỐ DTI CHUẨN: {DTI_chuan * 100:.2f}%")
print("="*30)

# Ngưỡng phê duyệt: DTI không quá 70% VÀ Thu nhập phải lớn hơn tổng nợ + chi phí sinh hoạt
if DTI_chuan <= 0.7 and TN > (PTMC + PTMM + tong_chi_phi_sh):
    print("KẾT LUẬN: ĐƯỢC CHO VAY")
else:
    print("KẾT LUẬN: KHÔNG ĐƯỢC CHO VAY")
    if DTI_chuan > 0.7:
        print("-> Lý do: Chỉ số DTI vượt ngưỡng an toàn (70%).")
    if TN <= (PTMC + PTMM + tong_chi_phi_sh):
        print("-> Lý do: Thu nhập không đủ bù đắp chi phí sinh hoạt tối thiểu và nghĩa vụ nợ.")
