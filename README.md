# School/College Management Website

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

### 6. **Staff Information**
   - **Staff Login**: Teachers can log in using their **Institute ID** and **password** (generated during registration).
   - **Staff Dashboard**:
     - Teachers can view a list of students assigned to them.
     - Sort students class-wise.
     - Add exam marks and attendance for each section.
     - Update marks and attendance for individual students.
     - Generate printouts of student details, including marks and attendance for each exam.

### 7. **Admin Information**
   - **Admin Login**: Admins can log in to access the admin dashboard.
   - **Admin Dashboard**:
     - Add students, teachers, and subjects.
     - Assign teachers to subjects and classes.
     - Generate unique **Institute Numbers** for students and teachers during registration.
     - Generate printouts of student and teacher details, including Institute Numbers and Date of Birth.

---

## 🛠️ Technical Specifications

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python Flask
- **Database**: SQLite/PostgreSQL/MySQL (choose one)
- **Authentication**: Flask-Login for user authentication
- **APIs**: RESTful APIs for seamless communication between frontend and backend
- **Third-Party Integration**:
  - Twilio for OTP-based password reset functionality.
  - Google Maps API for embedded location.

---

## 🚀 How to Use

1. **For Students/Parents**:
   - Visit the **Student Info** section.
   - Log in using the unique **Institute Number** and **Date of Birth**.
   - View academic performance, attendance, and exam details.

2. **For Staff**:
   - Visit the **Staff Info** section.
   - Log in using your **Institute ID** and **password**.
   - Manage student marks, attendance, and generate reports.

3. **For Admins**:
   - Visit the **Admin Info** section.
   - Log in to add students, teachers, and subjects.
   - Assign teachers to classes and generate unique IDs.

---

## 📂 Project Structure
chool-management-website/
├── app.py
|
│ ├── templates/ # HTML templates (Jinja2)
│ │ ├── home.html
│ │ ├── about.html
│ │ ├── courses.html
│ │ ├── student_login.html
│ │ ├── staff_login.html
│ │ ├── admin_login.html
│ │ └── ...
│ └── static/ # Static files (CSS, JS, images)
│ ├── css/
│ ├── js/
│ └── images/
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/darshanchouthai/SchoolWebsite.git


2. Navigate to the project directory:
cd SchoolWebsite

3. Create a virtual environment:
python -m venv venv

4. Activate the virtual environment:

On Windows:
venv\Scripts\activate

On macOS/Linux:
source venv/bin/activate

5. Install dependencies:
pip install -r requirements.txt

6. Set up environment variables:

Create a .env file in the root directory.

Add the following variables:


SECRET_KEY=your_secret_key
DATABASE_URI=your_database_uri
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token


7. Start the Flask development server:
flask run

8. Open your browser and visit http://localhost:5000.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

🙏 Acknowledgments
Thanks to Twilio for OTP integration.

Thanks to Google Maps API for location embedding.

Thanks to Flask and Flask-Login for making authentication seamless.

📧 Contact
For any queries or feedback, feel free to reach out:

Email: your-email@example.com

GitHub: your-username

Enjoy using the School/College Management Website! 🎉
