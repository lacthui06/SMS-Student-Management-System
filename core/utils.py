import pandas as pd

def calculate_total(comp, final):
    if comp is None or final is None: return None
    return round(comp * 0.3 + final * 0.7, 1)

def to_letter_grade(score):
    if score is None: return ""
    if score >= 8.5: return "A"
    elif score >= 7.0: return "B"
    elif score >= 5.5: return "C"
    elif score >= 4.0: return "D"
    else: return "F"

def get_time_string(start, end):
    # Mapping tiết sang giờ (Demo đơn giản)
    periods = {1: "07:00", 2: "07:50", 3: "08:40", 4: "09:35", 5: "10:25", 6: "11:15",
               7: "13:00", 8: "13:50", 9: "14:40", 10: "15:35", 11: "16:25", 12: "17:15"}
    end_times = {1: "07:50", 2: "08:40", 3: "09:30", 4: "10:25", 5: "11:15", 6: "12:05",
                 7: "13:50", 8: "14:40", 9: "15:30", 10: "16:25", 11: "17:15", 12: "18:05"}
    
    s = periods.get(start, "??")
    e = end_times.get(end, "??")
    return f"Tiết {start}-{end} ({s} - {e})"