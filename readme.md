    LMS_Project/
    ├── app.py                  # File chạy chính
    ├── core/                   # Chứa dữ liệu và hàm xử lý cốt lõi
    │   ├── __init__.py
    │   ├── database.py         # Mock Database (Class quản lý dữ liệu)
    │   ├── models.py           # Các Class đối tượng (User, Course...)
    │   └── utils.py            # Hàm tiện ích (Tính điểm, giờ học)
    ├── controllers/            # Xử lý Logic nghiệp vụ (Controller)
    │   ├── __init__.py
    │   ├── auth_controller.py
    │   ├── student_controller.py
    │   ├── lecturer_controller.py
    │   └── admin_controller.py
    └── views/                  # Giao diện người dùng (View - Streamlit)
        ├── __init__.py
        ├── login_view.py
        ├── student_view.py
        ├── lecturer_view.py
        └── admin_view.py
