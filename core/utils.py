import pandas as pd

# --- TÍNH ĐIỂM TỔNG KẾT (30% QT - 70% CK) ---
def calculate_total(comp, final):
    if comp is None or final is None: return 0.0
    # Làm tròn 1 chữ số thập phân
    return round(float(comp) * 0.3 + float(final) * 0.7, 1)

# --- QUY ĐỔI ĐIỂM SỐ SANG ĐIỂM CHỮ ---
def to_letter_grade(score):
    if score is None: return ""
    score = float(score)
    if score >= 8.5: return "A"
    elif score >= 7.0: return "B"
    elif score >= 5.5: return "C"
    elif score >= 4.0: return "D"
    else: return "F"

# --- QUY ĐỔI TIẾT HỌC SANG GIỜ (Logic mới: 50p/tiết liên tục) ---
def get_time_string(start, end):
    # Mapping giờ bắt đầu (Mỗi tiết 50p, không nghỉ)
    start_times = {
        1: "07:00", 2: "07:50", 3: "08:40", 4: "09:30", 5: "10:20", 6: "11:10",
        7: "13:00", 8: "13:50", 9: "14:40", 10: "15:30", 11: "16:20", 12: "17:10",
        13: "18:00", 14: "18:50", 15: "19:40"
    }
    
    # Mapping giờ kết thúc
    end_times = {
        1: "07:50", 2: "08:40", 3: "09:30", 4: "10:20", 5: "11:10", 6: "12:00",
        7: "13:50", 8: "14:40", 9: "15:30", 10: "16:20", 11: "17:10", 12: "18:00",
        13: "18:50", 14: "19:40", 15: "20:30"
    }
    
    s = start_times.get(start, "??:??")
    e = end_times.get(end, "??:??")
    
    return f"{s} - {e} (Tiết {start}-{end})"