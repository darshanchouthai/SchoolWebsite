# 🎓 School/College Management Website

Welcome to the **School/College Management Website**! This platform is designed to streamline the management of academic institutions by providing a comprehensive solution for students, staff, and administrators. Built with **Python Flask** and **Flask-Login**, the website offers a user-friendly interface to access academic performance, course information, staff details, and administrative tools.

---

## 🌟 Features

### 1. **Home Page**
   - Displays the institute's performance in various exams.
   - Includes an embedded map location for easy navigation.

### 2. **About Us Page**
   - Provides detailed information about the school/college, including its history, mission, and vision.

### 3. **Courses Page**
   - Lists all available courses.
   - Each course has an **"Apply" button** that redirects users to the application page.
   - On the application page, parents/students can apply for courses by providing their and their child's information.

### 4. **Staff Information**
   - Displays information about staff members for each section and course.

### 5. **Student Information**
   - **Student Login**: Parents/students can log in using a unique **Institute Number** (generated during student registration) and the student's **Date of Birth**.
   - **Student Dashboard**:
     - Displays average marks in each subject as histograms.
     - Shows attendance in each subject as histograms.
     - Lists all subjects allocated to the student with **Exam** and **Attendance** buttons.
       - **Exam Button**: Redirects to the exam page, showing all exams for the related subject with class average marks.
       - **Attendance Button**: Redirects to the attendance page, displaying present and absent dates.

### 6. **Staff Portal**
   - **Staff Login**: Teachers can log in using their **Institute ID** and **password** (generated during registration).
   - **Change Password**: Teachers can reset their password using **OTP verification via Twilio**.
   - **Staff Dashboard**:
     - Teachers can view a list of students assigned to them.
     - Sort students class-wise.
     - Add exam marks and attendance for each section.
     - Update marks and attendance for individual students.
     - Generate printouts of student details, including marks and attendance for each exam.

### 7. **Admin Portal**
   - **Admin Login**: Secure login for admin access.
   - **Admin Dashboard**:
     - Add students, teachers, and subjects.
     - Assign teachers to subjects and classes.
     - Generate unique **Institute Numbers** for students and teachers during registration.
     - Generate printouts of student and teacher details, including Institute Numbers and Date of Birth.

---

## 🛠️ Technical Specifications

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: Flask-Login for user authentication
- **Data Visualization**: Chart.js for histograms
- **APIs**: RESTful APIs for seamless communication between frontend and backend
- **Third-Party Integration**:
  - Twilio for OTP-based password reset functionality.
  - Google Maps API for embedded location.
  - reportlab for generating reports in PDF format.

---

## 🚀 How to Install and Run

### 1. Clone the Repository
```bash
git clone https://github.com/darshanchouthai/SchoolWebsite.git
cd SchoolWebsite
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
#### On Windows:
```bash
venv\Scripts\activate
```
#### On macOS/Linux:
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the root directory and add:
```ini
SECRET_KEY=your_secret_key
DATABASE_URI=your_database_uri
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### 6. Run the Flask Development Server
```bash
flask run
```

### 7. Open the Website
Go to: [http://localhost:5000](http://localhost:5000)

---

## 📂 Project Structure
```
school-management-website/
├── app.py
│
│── templates/ # HTML templates (Jinja2)
│   ├── home.html
│   ├── about.html
│   ├── courses.html
│   ├── student_login.html
│   ├── staff_login.html
│   ├── admin_login.html
│   └── ...
│
│── static/ # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

---

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## 🙏 Acknowledgments
- Thanks to **Twilio** for OTP integration.
- Thanks to **Google Maps API** for location embedding.
- Thanks to **Flask** and **Flask-Login** for authentication support.

---

## 💌 Contact
For any queries or feedback, feel free to reach out:

**Email**: [darshanchouthai@gmail.com](mailto:darshanchouthai@gmail.com)

**GitHub**: [darshanchouthai](https://github.com/darshanchouthai)

Enjoy using the **School/College Management Website**! 🎉

