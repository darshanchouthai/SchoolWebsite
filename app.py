from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify,send_file
from flask_login import login_required, current_user
import mysql.connector
from mysql.connector import connect, Error
import secrets
import random
import string
import pymysql
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from io import BytesIO



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  


# Sample data for courses
courses = [
    {"id": 1, "name": "1st to 10th Classes", "description": "A comprehensive course for students in grades 1 to 10, covering all core subjects like Mathematics, Science, Social Studies, and Languages, with a focus on conceptual understanding and exam preparation."},
    {"id": 2, "name": "Navodaya Coaching (5th Standard Entrance Preparation)", "description": "Specialized coaching for students preparing for the Jawahar Navodaya Vidyalaya Selection Test (NVST), focusing on Mental Ability, Arithmetic, and Language proficiency to excel in the entrance examination."},
    {"id": 3, "name": "Sainik School Coaching (5th Standard Entrance Preparation)", "description": "Coaching for students aspiring to join Sainik Schools through the entrance examination, with training in General Knowledge, Mathematics, and English to prepare for both written and physical tests."},
    {"id": 4, "name": "PUC Science", "description": "A detailed study of Science subjects (Physics, Chemistry, Biology, Maths) for Pre-University Course (PUC) students, preparing them for board exams and future careers in engineering, medicine, or research."},
    {"id": 5, "name": "NEET Coaching", "description": "Focused coaching for students preparing for the National Eligibility cum Entrance Test (NEET), covering Physics, Chemistry, and Biology with practice questions, mock exams, and expert guidance."}
]
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',        # Your MySQL host
            user='root',             # Your MySQL username
            password='Darshan@2003', # Your MySQL password
            database='School_Collage' # The name of your database
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def fetch_teachers_and_subjects():
    try:
        # Create a database connection
        connection = get_db_connection()

        if connection is not None:
            # Create a cursor object to interact with the database
            cursor = connection.cursor(dictionary=True)

            # Fetch all teachers
            cursor.execute("SELECT name FROM teachers")
            teachers = cursor.fetchall()

            # Fetch all subjects
            cursor.execute("SELECT subject_name FROM subjects")
            subjects = cursor.fetchall()

            # Debugging: Check if the data is being fetched
            print("Teachers:", teachers)
            print("Subjects:", subjects)

            # Close cursor and connection
            cursor.close()
            connection.close()

            return teachers, subjects
        else:
            print("Connection error: No connection to the database.")
            return None, None
    except Error as e:
        print(f"Error fetching teachers and subjects: {e}")
        return None, None


# Create table if it doesn't exist (Run once to create the table)
def create_table():
    try:
        connection = get_db_connection()
        if connection is not None:
            cursor = connection.cursor()
            
            # Create the applications table
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS applications (
                    Application_id INT AUTO_INCREMENT PRIMARY KEY,
                    course_name VARCHAR(100) NOT NULL,
                    child_name VARCHAR(100) NOT NULL,
                    child_previous_score INT NOT NULL,
                    parent_mobile_number VARCHAR(15) NOT NULL,
                    parent_email VARCHAR(100) NOT NULL
                )
            ''')
            
            # Create the students table
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                course_name VARCHAR(100) NOT NULL,
                security_number VARCHAR(20) ,
                birth_date DATE NOT NULL,
                medium varchar(20)                      
)

            ''')
            

          
            cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INT PRIMARY KEY AUTO_INCREMENT, 
        subject_name VARCHAR(100) UNIQUE
    )
''')
            cursor.execute(''' 
                    CREATE TABLE IF NOT EXISTS teachers(
                    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    teacher_security_key VARCHAR(32) NOT NULL,
                    password varchar(20),
                           Email Varchar(40) NOT NULL,
                           Mobine_no varchar(20) not null
                )
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS teacher_subjects (
    teacher_subject_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    subject_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    UNIQUE(teacher_id, subject_id) ) ''')
            
           
           
            cursor.execute('''CREATE TABLE IF NOT EXISTs teacher_student_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    student_id INT NOT NULL,
                           subject_id int NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    UNIQUE(teacher_id, student_id,subject_id)
)
''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS student_marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique identifier for each mark entry
    student_id INT NOT NULL,                  -- ID of the student
    teacher_id INT NOT NULL,                  -- ID of the teacher
    subject_id INT NOT NULL,                  -- ID of the subject
    maximum_marks INT NOT NULL,               -- Maximum marks for the exam
    marks_got Int not null, 
    examname varchar(20),                 -- Marks obtained by the student
    FOREIGN KEY (student_id) REFERENCES students(student_id),  -- Linking to the students table
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),  -- Linking to the teachers table (assuming a teachers table exists)
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)   -- Linking to a subjects table (assuming it exists)
)
''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    subject_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    UNIQUE(student_id, teacher_id, course_name, subject_id, date)  -- Ensures unique attendance entry per student per day
)''')
          
            
           
            connection.commit()
            cursor.close()
            connection.close()
    except Error as e:
        print(f"Error creating table: {e}")

# Call this once when you first run the app to create the table
create_table()

# Route to apply for a course
@app.route('/apply', methods=['GET', 'POST'])
def apply_for_course():
    if request.method == 'GET':
        # Render the application form
        return render_template('applications.html')

    elif request.method == 'POST':
        data = request.form

        # Required fields validation
        required_fields = ['courseName', 'childName', 'childPreviousScore', 'parentMobileNumber', 'parentEmail']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            flash(f"Error: {', '.join(missing_fields)} are required.", "danger")
            return redirect(url_for('apply_for_course'))

        # Extract and sanitize data
        course_name = data['courseName']
        child_name = data['childName']
        try:
            child_previous_score = int(data['childPreviousScore'])  # Ensure it's an integer
        except ValueError:
            flash("Error: Child's previous score must be a number.", "danger")
            return redirect(url_for('apply_for_course'))
        
        parent_mobile_number = data['parentMobileNumber']
        parent_email = data['parentEmail']

        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO applications (course_name, child_name, child_previous_score, parent_mobile_number, parent_email)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (course_name, child_name, child_previous_score, parent_mobile_number, parent_email))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                flash("Your application has been received! Our team will contact you after verification.", "success")
                return redirect(url_for('apply_for_course'))
            else:
                flash("Error: Database connection failed.", "danger")
                return redirect(url_for('apply_for_course'))
        except mysql.connector.Error as e:
            flash(f"Database Error: {str(e)}", "danger")
            return redirect(url_for('apply_for_course'))

# Home route to render the main page
@app.route('/')
def home():
    return render_template('index.html')

# Route to get course details
@app.route('/get_courses', methods=['GET'])
def get_courses():
    return render_template('Cources.html', courses=courses)

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'GET':
        try:
            connection = get_db_connection()
            if connection is not None:
                cursor = connection.cursor(dictionary=True)
                
                # Fetch all teachers and subjects
                cursor.execute("SELECT name FROM teachers")
                teachers = cursor.fetchall()

                cursor.execute("SELECT subject_name FROM subjects")
                subjects = cursor.fetchall()

                # Debugging: Check if the data is being fetched
                print("Teachers:", teachers)
                print("Subjects:", subjects)

                # Close cursor and connection
                cursor.close()
                connection.close()
                
                return render_template('admin.html', teachers=teachers, subjects=subjects)

        except Error as e:
            print(f"Error: {e}")
            return render_template('error.html', error="Failed to load teachers or subjects."), 500

    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_student':
            # Get form data
            student_name = request.form.get('studentName')
            course_name = request.form.get('courseName')
            birth_date = request.form.get('birthDate')
            medium = request.form.get('medium')

            # Validate form data
            if not student_name or not course_name or not birth_date or not medium:
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template(
                    'admin.html', 
                    error1="All fields are required: student name, course name, birthdate, and medium.",teachers=teachers, subjects=subjects
                ), 400

            try:
                connection = get_db_connection()
                if connection is not None:
                    cursor = connection.cursor()

                    # Determine the prefix for security number
                    if course_name in ["1st", "2nd", "3rd", "4th", "5th"]:
                        prefix = f"SDE{course_name.upper()}KM" if medium.lower() == "kannada" else f"SDE{course_name.upper()}EM"
                    elif course_name in ["6th", "7th", "8th", "9th", "10th"]:
                        prefix = f"SDE{course_name.upper()}{'KM' if medium.lower() == 'kannada' else 'EM'}"
                    elif course_name == "PUC I":
                        prefix = "SDEPUCI"
                    elif course_name == "PUC II":
                        prefix = "SDEPUCII"
                    else:
                        teachers, subjects = fetch_teachers_and_subjects()
                        return render_template('admin.html',teachers=teachers, subjects=subjects, error1="Invalid course name or medium provided."), 400

                    # Generate a new security number
                    cursor.execute("""
                        SELECT security_number FROM students 
                        WHERE security_number LIKE %s
                        ORDER BY student_id DESC LIMIT 1
                    """, (prefix + "%",))
                    last_security_number = cursor.fetchone()

                    if last_security_number and last_security_number[0]:
                        numeric_part = ''.join(filter(str.isdigit, last_security_number[0][len(prefix):]))
                        numeric_part = int(numeric_part) if numeric_part else 0
                    else:
                        numeric_part = 0

                    # Increment the numeric part and generate the new security number
                    numeric_part += 1
                    security_number = f"{prefix}{numeric_part:03}"  # Format: PREFIX###

                    # Insert student details into the table
                    cursor.execute("""
                        INSERT INTO students (name, course_name, birth_date, security_number, medium)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (student_name, course_name, birth_date, security_number, medium))
                    connection.commit()

                    
                    # Close cursor and connection
                    cursor.close()
                    connection.close()
                    try:
        # Fetch all teachers and subjects for the form
                        connection = get_db_connection()
                        with connection.cursor(dictionary=True) as cursor:
                            cursor.execute("SELECT name FROM teachers")
                            teachers = cursor.fetchall()

                            cursor.execute("SELECT subject_name FROM subjects")
                            subjects = cursor.fetchall()
                            print(teachers)
                            print(subjects)
                            connection.close()

                    

                    # Return the template with success message and updated data
                        return render_template(
                        'admin.html', 
                        message1=f"Student {student_name} added successfully with security number {security_number}.",
                        teachers=teachers,  # Pass updated teachers
                        subjects=subjects   # Pass updated subjects
                    )
                
                    except Exception as e:
                        print(f"Error fetching teachers or subjects: {e}")
                       
                        return render_template('error.html', error="Error fetching teachers or subjects.")
            except Error as e:
                print(f"Error: {e}")
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template('admin.html',teachers=teachers, subjects=subjects, error1="Failed to add student."), 500


        elif action == 'add_teacher':
            teacher_name = request.form.get('teacherName')
            Email=request.form.get('Emailid')
            Mobile_no=request.form.get('mobileno')
            
            if not teacher_name:
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template('admin.html',teachers=teachers, subjects=subjects, error2="Teacher name required."), 400

            try:
                connection = get_db_connection()
                if connection is not None:
                    cursor = connection.cursor()
                    
                    # Generate Teacher Security Number
                    teacher_secret_key = f"SDE{random.randint(100, 999)}{''.join(random.choices(string.ascii_uppercase, k=2))}"
                    
                    # Insert teacher details into the teachers table
                    cursor.execute("""
                        INSERT INTO teachers (name, teacher_security_key, password,email,Mobile_no)
                        VALUES (%s, %s, %s,%s,%s)
                    """, (teacher_name, teacher_secret_key, 'defaultpassword',Email,Mobile_no))
                    connection.commit()

                    cursor.close()
                    connection.close()
                    try:
        # Fetch all teachers and subjects for the form
                        connection = get_db_connection()
                        with connection.cursor(dictionary=True) as cursor:
                            cursor.execute("SELECT name FROM teachers")
                            teachers = cursor.fetchall()

                            cursor.execute("SELECT subject_name FROM subjects")
                            subjects = cursor.fetchall()
                            print(teachers)
                            print(subjects)
                            connection.close()

                    

                    # Return the template with success message and updated data
                        return render_template(
                        'admin.html', 
                      message2=f"Teacher {teacher_name} added successfully with security number {teacher_secret_key}.",
                        teachers=teachers,  # Pass updated teachers
                        subjects=subjects   # Pass updated subjects
                    )
                
                    except Exception as e:
                        print(f"Error fetching teachers or subjects: {e}")
                        return render_template('error.html', error="Error fetching teachers or subjects.")
                    
                    

                    
            except Error as e:
                print(f"Error: {e}")
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template('admin.html',teachers=teachers, subjects=subjects, error2="Failed to add teacher."), 500
        elif action == 'add_subject':
            subject_name = request.form.get('subjectName')
            
            if not subject_name:
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template('error.html',teachers=teachers, subjects=subjects, error3="Subject name is required."), 400
            
            try:
                connection = get_db_connection()
                if connection is not None:
                    cursor = connection.cursor()
                    
                    # Insert subject into subjects table
                    cursor.execute("""
                        INSERT INTO subjects (subject_name)
                        VALUES (%s)
                        ON DUPLICATE KEY UPDATE subject_name = subject_name
                    """, (subject_name,))
                    connection.commit()
                    
                    cursor.close()
                    connection.close()
                    try:
        # Fetch all teachers and subjects for the form
                        connection = get_db_connection()
                        with connection.cursor(dictionary=True) as cursor:
                            cursor.execute("SELECT name FROM teachers")
                            teachers = cursor.fetchall()

                            cursor.execute("SELECT subject_name FROM subjects")
                            subjects = cursor.fetchall()
                            print(teachers)
                            print(subjects)
                            connection.close()

                    

                    # Return the template with success message and updated data
                        return render_template(
                        'admin.html', 
                      message3=f"Subject {subject_name} added successfully.",
                        teachers=teachers,  # Pass updated teachers
                        subjects=subjects   # Pass updated subjects
                    )
                
                    except Exception as e:
                        print(f"Error fetching teachers or subjects: {e}")
                        return render_template('error.html',error="Error fetching teachers or subjects.")
                    
                   
                    
            except Error as e:
                print(f"Error: {e}")
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template('admin.html',teachers=teachers, subjects=subjects, error1="Failed to add student."), 500
            except Error as e:
                print(f"Error: {e}")
                teachers, subjects = fetch_teachers_and_subjects()
                return render_template('admin.html',teachers=teachers, subjects=subjects, error3="Failed to add subject."), 500
        elif action == 'assign_teacher':
            return redirect(url_for('assign_teacher'))
        elif action ==' assign_teacher_to_students':
            return redirect(url_for('assign_teacher_to_students'))

@app.route('/assign_teacher', methods=['GET', 'POST'])
def assign_teacher():
    # Fetch all teachers and subjects for the form
    connection = get_db_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT name FROM teachers")
        teachers = cursor.fetchall()

        cursor.execute("SELECT subject_name FROM subjects")
        subjects = cursor.fetchall()
    connection.close()

    if request.method == 'POST':
        teacher_name = request.form.get('teacher_name')
        subject_name = request.form.get('subject_name')

        # Validate that both fields are provided
        if not teacher_name or not subject_name:
            return render_template('admin.html', error="Both teacher name and subject name are required.", teachers=teachers, subjects=subjects)

        try:
            connection = get_db_connection()
            if not connection:
                return render_template('error.html', error="Database connection error.")

            with connection.cursor(dictionary=True) as cursor:
                # Get teacher_id based on teacher_name
                cursor.execute("SELECT teacher_id FROM teachers WHERE name = %s", (teacher_name,))
                teacher_data = cursor.fetchone()

                # Get subject_id based on subject_name
                cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = %s", (subject_name,))
                subject_data = cursor.fetchone()

                # Check if teacher and subject exist
                if not teacher_data or not subject_data:
                    return render_template('admin.html', error="Invalid teacher or subject selected.", teachers=teachers, subjects=subjects)

                teacher_id = teacher_data['teacher_id']
                subject_id = subject_data['subject_id']

                # Check if the teacher is already assigned to the subject
                cursor.execute(
                    "SELECT * FROM teacher_subjects WHERE teacher_id = %s AND subject_id = %s",
                    (teacher_id, subject_id)
                )
                existing_assignment = cursor.fetchone()

                # If assignment already exists, show error message
                if existing_assignment:
                    return render_template('admin.html', error="This teacher is already assigned to this subject.", teachers=teachers, subjects=subjects)

                # Insert the teacher-subject assignment into the teacher_subjects table
                cursor.execute(
                    "INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (%s, %s)",
                    (teacher_id, subject_id)
                )
                connection.commit()

            connection.close()

            # On successful assignment, show success message
            return render_template('admin.html', teachers=teachers, subjects=subjects, message6="Teacher has been successfully assigned to the subject.")

        except Exception as e:
            print(f"Error assigning teacher: {e}")
            return render_template('admin.html', teachers=teachers, subjects=subjects, error=str(e))

    # Pass teachers and subjects to the template for the form
    return render_template('admin.html', teachers=teachers, subjects=subjects)
@app.route('/assign_teacher_to_students', methods=['GET', 'POST'])
def assign_teacher_to_students():
    subjects1 = []  # Start with an empty list for subjects

    if request.method == 'POST':
        teacher_name = request.form.get('teacher_name')
        course_name = request.form.get('course_name')
        subject_name = request.form.get('subject_name')
        print(teacher_name)
        print(course_name)
        print(subject_name)

        # Check if required fields are provided
        
        try:
            connection = get_db_connection()
            with connection.cursor(dictionary=True) as cursor:
                # Fetch all teachers
                cursor.execute("SELECT name FROM teachers")
                teachers = cursor.fetchall()

                # Fetch all course names
                cursor.execute("SELECT DISTINCT course_name FROM students")
                courses = cursor.fetchall()

                # Fetch subjects assigned to the entered teacher
                cursor.execute(
                    "SELECT subject_name, subject_id FROM subjects WHERE subject_id IN (SELECT subject_id FROM teacher_subjects WHERE teacher_id = (SELECT teacher_id FROM teachers WHERE name = %s))", 
                    (teacher_name,)
                )
                subjects1 = cursor.fetchall()

                if not subjects1:
                    return render_template('admin.html',teachers=teachers, subjects=subjects, error4=f"No subjects found for teacher '{teacher_name}'.")

                # Now, proceed with the logic to assign teacher to students

                # Get teacher_id based on teacher_name
                cursor.execute("SELECT teacher_id FROM teachers WHERE name = %s", (teacher_name,))
                teacher_data = cursor.fetchone()

                if not teacher_data:
                    return render_template('admin.html',teachers=teachers, subjects=subjects, error4="Teacher not found.")

                teacher_id = teacher_data['teacher_id']

                # Fetch subject_id for the selected subject
                cursor.execute(
                    "SELECT subject_id FROM subjects WHERE subject_name = %s", 
                    (subject_name,)
                )
                subject_data = cursor.fetchone()

                if not subject_data:
                    return render_template('admin.html',teachers=teachers, subjects=subjects, error4="Subject not found.")

                subject_id = subject_data['subject_id']

                # Check if the teacher is assigned to the given subject
                cursor.execute(
                    "SELECT subject_id FROM teacher_subjects WHERE teacher_id = %s AND subject_id = %s",
                    (teacher_id, subject_id)
                )
                subject_assignment = cursor.fetchone()

                if not subject_assignment:
                    teachers, subjects = fetch_teachers_and_subjects()
                    return render_template('admin.html',teachers=teachers, subjects=subjects, error4="Teacher is not assigned to the selected subject.")

                # Fetch all students from the given course_name
                cursor.execute("SELECT student_id FROM students WHERE course_name = %s", (course_name,))
                students = cursor.fetchall()

                if not students:
                    return render_template('admin.html',teachers=teachers, subjects=subjects, error4="No students found for the given course.")

                # Assign the teacher to each student
                for student in students:
                    student_id = student['student_id']
                    
                    # Check if the teacher is already assigned to this student (optional, to prevent duplicate assignments)
                    cursor.execute(
                        "SELECT * FROM teacher_student_assignments WHERE teacher_id = %s AND student_id = %s",
                        (teacher_id, student_id)
                    )
                    existing_assignment = cursor.fetchone()

                    if not existing_assignment:
                        cursor.execute(
                            "INSERT INTO teacher_student_assignments (teacher_id, student_id, subject_id) VALUES (%s, %s, %s)",
                            (teacher_id, student_id, subject_id)
                        )

                connection.commit()

            connection.close()
            try:
        # Fetch all teachers and subjects for the form
                connection = get_db_connection()
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT name FROM teachers")
                    teachers = cursor.fetchall()

                    cursor.execute("SELECT subject_name FROM subjects")
                    subjects = cursor.fetchall()
                    print(teachers)
                    print(subjects)

                connection.close()

        # Pass teachers and subjects to the template for the form
                return render_template('admin.html', teachers=teachers, subjects=subjects, message5=f"Assignment Successfull")

            except Exception as e:
                print(f"Error fetching teachers or subjects: {e}")
                return render_template('error.html', error="Error fetching teachers or subjects.")

        except Exception as e:
            print(f"Error assigning teacher to students: {e}")
            teachers, subjects = fetch_teachers_and_subjects()
            return render_template('admin.html', teachers=teachers, subjects=subjects, error4="Error while assigning teacher to students.")

    # For GET request handling (loading the page with teachers and courses)
    try:
        connection = get_db_connection()
        with connection.cursor(dictionary=True) as cursor:
            # Fetch all teachers
            cursor.execute("SELECT name FROM teachers")
            teachers = cursor.fetchall()

            # Fetch all course names
            cursor.execute("SELECT DISTINCT course_name FROM students")
            courses = cursor.fetchall()

        connection.close()

        return render_template('admin.html', teachers=teachers, courses=courses, subjects1=subjects1)

    except Exception as e:
        print(f"Error fetching teachers or courses: {e}")
        return render_template('error.html', error4="Error fetching teachers or courses.")


@app.route('/get_subjects_for_teacher', methods=['POST'])
def get_subjects_for_teacher():
    try:
        # Get the teacher name from the AJAX request
        teacher_name = request.json.get('teacher_name')

        if not teacher_name:
            return jsonify({'subjects': []})  # No teacher name provided

        connection = get_db_connection()
        with connection.cursor(dictionary=True) as cursor:
            # Fetch subjects assigned to the teacher
            cursor.execute(
                "SELECT subject_name FROM subjects WHERE subject_id IN (SELECT subject_id FROM teacher_subjects WHERE teacher_id = (SELECT teacher_id FROM teachers WHERE name = %s))", 
                (teacher_name,)
            )
            subjects = cursor.fetchall()

        connection.close()

        return jsonify({'subjects': subjects})

    except Exception as e:
        print(f"Error fetching subjects: {e}")
        return jsonify({'subjects': []})  # Return an empty list in case of error


@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        # Get form data
        security_number = request.form.get('securityNumber')
        birth_date = request.form.get('birthDate')
        print(security_number)
        print(birth_date)

        try:
            connection = get_db_connection()
            if not connection:
                return render_template('student_login.html', message="Database connection error.")

            with connection.cursor(dictionary=True) as cursor:
                query = '''
                    SELECT student_id FROM students 
                    WHERE security_number = %s AND birth_date = %s
                '''
                cursor.execute(query, (security_number, birth_date))
                student = cursor.fetchone()
                print(student)

            connection.close()

            if student:
                # Store student details in session
                session.permanent = True
                session['student_id'] = student['student_id']

                return redirect(url_for('student_dashboard', student_id=student['student_id']))

            return render_template('student_login.html', message="Invalid credentials. Please try again.")

        except Error as e:
            print(f"Error: {e}")
            return render_template('student_login.html', message="An error occurred. Please try again later.")

    return render_template('student_login.html')  # Render the login page for GET requests


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None  # Initialize error variable
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded credentials (replace with environment variables for security in production)
        admin_username = ''
        admin_password = ''

        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))  # Redirect to the admin panel
        else:
            error = "Invalid credentials. Please try again."

    return render_template('admin_login.html', error=error)

# Assuming 'db' is your database connection object

# Staff Login Route
@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        security_number = request.form.get('security_number')
        password = request.form.get('password')

        if not security_number or not password:
            return render_template('staff_login.html', error="Security number and password are required.")

        try:
            connection = get_db_connection()
            if not connection:
                return render_template('staff_login.html', error="Database connection error.")

            with connection.cursor(dictionary=True) as cursor:
                query = '''
                    SELECT teacher_id, password FROM teachers 
                    WHERE teacher_security_key = %s
                '''
                cursor.execute(query, (security_number,))
                teacher_data = cursor.fetchone()

            connection.close()

            if teacher_data:
                stored_password = teacher_data['password']
                
                # Directly compare plain-text password (Not secure!)
                if stored_password == password:
                    session.permanent = True
                    session['teacher_id'] = teacher_data['teacher_id']
                    
                    return redirect(url_for('staff_dashboard', teacher_id=teacher_data['teacher_id']))

                return render_template('staff_login.html', error="Invalid security number or password.")

            return render_template('staff_login.html', error="Security number not found.")

        except Exception as e:
            print(f"Error: {e}")
            return render_template('staff_login.html', error="Error during login.")

    return render_template('staff_login.html')  # Render login page on GET request

@app.route('/staff_dashboard', methods=['GET', 'POST'])
def staff_dashboard():
    teacher_id = request.args.get('teacher_id')  # Get the teacher ID from query params
    
    if not teacher_id:
        return render_template('staff_login.html')

    try:
        # Establish a database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch courses assigned to the teacher
        cursor.execute("""
            SELECT DISTINCT c.course_name
            FROM students c
            JOIN teacher_student_assignments tsa ON tsa.student_id = c.student_id
            WHERE tsa.teacher_id = %s
        """, (teacher_id,))
        courses = cursor.fetchall()
        print(courses)
        # Fetch students assigned to the teacher
        cursor.execute("""
            SELECT s.student_id,s.security_number, s.name, s.course_name
            FROM students s
            JOIN teacher_student_assignments tsa ON tsa.student_id = s.student_id
            WHERE tsa.teacher_id = %s
        """, (teacher_id,))
        students = cursor.fetchall()
        

        cursor.close()
        connection.close()

        # Render the dashboard with students, courses, and buttons for Exam and Attendance
        return render_template('staff_dashboard.html', teacher_id=teacher_id, students=students, courses=courses)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error="Error processing request.")


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        security_number = request.form['security_number']
        new_password = request.form['new_password']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            
            
            # Check if the teacher exists with the given security number
            cursor.execute(f"SELECT teacher_security_key FROM teachers WHERE teacher_security_key = %s", (security_number,))
            teacher_exists = cursor.fetchone()
            
            if teacher_exists:
                # Update the teacher's password
                cursor.execute(f"UPDATE teachers SET password = %s WHERE teacher_security_key = %s", (new_password, security_number))
                connection.commit()
                
                return redirect(url_for('staff_login', message="Password updated successfully. Please log in again."))
            else:
                return render_template('change_password.html', error="Invalid security number.")
        
        except Exception as e:
            print(f"Error: {e}")
            return render_template('change_password.html', error="Error while changing the password.")
    
    return render_template('change_password.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    teacher_id = request.args.get('teacher_id')  # Get the teacher ID from query params
    
    if not teacher_id:
        return render_template('error.html', error="Teacher ID is required.")
    
    try:
        # Establish a database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch courses assigned to the teacher (from the students table)
        cursor.execute("""
            SELECT DISTINCT s.course_name
            FROM students s
            JOIN teacher_student_assignments tsa ON tsa.student_id = s.student_id
            WHERE tsa.teacher_id = %s
        """, (teacher_id,))
        courses = cursor.fetchall()  # Format: [('1st',), ('2nd',), ...]

        if request.method == 'POST':
            exam_name = request.form.get('exam_name')
            maximum_marks = request.form.get('maximum_marks')
            course_name = request.form.get('course_name')

            # Check if all fields are correctly populated
            print(f"Exam Name: {exam_name}, Maximum Marks: {maximum_marks}, Course Name: {course_name}")

            # Fetch students for the selected course
            cursor.execute("""
                SELECT s.student_id, s.name
                FROM students s
                WHERE s.course_name = %s
            """, (course_name,))
            students = cursor.fetchall()

            # Check if students are retrieved correctly
            if not students:
                print("No students found for the selected course.")
                return render_template('error.html', error="No students found for the selected course.")

            # Insert marks into the database
            for student in students:
                student_id = student[0]
                marks_got = request.form.get(f'marks_{student_id}')
                
                # Ensure marks_got is not empty or invalid
                if not marks_got:
                    print(f"Marks not provided for student ID: {student_id}")
                    continue  # Skip this student if marks are not entered

                # Fetch subject_id from teacher_student_assignments based on student_id and teacher_id
                cursor.execute("""
                    SELECT tsa.subject_id
                    FROM teacher_student_assignments tsa
                    WHERE tsa.student_id = %s AND tsa.teacher_id = %s
                """, (student_id, teacher_id))
                subject_id_result = cursor.fetchone()
                if not subject_id_result:
                    print(f"No subject found for student ID: {student_id}")
                    continue  # Skip this student if no subject_id is found
                
                subject_id = subject_id_result[0]

                # Print the values before inserting into the database for debugging
                print(f"Inserting into student_marks: student_id={student_id}, teacher_id={teacher_id}, "
                      f"subject_id={subject_id}, maximum_marks={maximum_marks}, marks_got={marks_got}")
                
                # Insert the marks into the student_marks table
                cursor.execute("""
                    INSERT INTO student_marks (student_id, teacher_id, subject_id, maximum_marks, marks_got,examname)
                    VALUES (%s, %s, %s, %s, %s,%s)
                """, (student_id, teacher_id, subject_id, maximum_marks, marks_got,exam_name))

            connection.commit()  # Commit the transaction
            return render_template('exam.html', message="Marks entered successfully.", teacher_id=teacher_id, courses=courses, course_name=course_name, exam_name=exam_name, maximum_marks=maximum_marks)

        cursor.close()
        connection.close()

        return render_template('exam.html', teacher_id=teacher_id, courses=courses)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('exam.html', error="Error processing request.")

@app.route('/get_students_for_course', methods=['GET'])
def get_students_for_course():
    course_name = request.args.get('course_name')

    if not course_name:
        return jsonify({'error': 'Course name is required.'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch students based on the course name
        cursor.execute("""
            SELECT s.student_id,s.security_number, s.name
            FROM students s
            WHERE s.course_name = %s
        """, (course_name,))
        students = cursor.fetchall()

        if not students:
            return jsonify({'students': []})  # No students found for the course

        students_data = [{'student_id': student[0], 'name': student[2],'security_number': student[1]} for student in students]

        cursor.close()
        connection.close()

        return jsonify({'students': students_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "teacher_id" not in session:
        return redirect(url_for("staff_login"))  # Redirect if not logged in

    teacher_id = session["teacher_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch courses assigned to this teacher
    cursor.execute("""
        SELECT DISTINCT s.course_name
        FROM students s
        JOIN teacher_student_assignments ts ON s.student_id = ts.student_id
        WHERE ts.teacher_id = %s
    """, (teacher_id,))
    courses = cursor.fetchall()

    # Fetch subjects assigned to this teacher
    cursor.execute("""
        SELECT DISTINCT s.subject_id, s.subject_name
        FROM subjects s
        JOIN teacher_subjects ts ON s.subject_id = ts.subject_id
        WHERE ts.teacher_id = %s
    """, (teacher_id,))
    subjects = cursor.fetchall()

    connection.close()

    return render_template("attendance.html", courses=courses, subjects=subjects, teacher_id=teacher_id)
@app.route("/get_subjects", methods=["POST"])
def get_subjects():
    teacher_id = session["teacher_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        select subject_name from subjects s join teacher_subjects ts where s.subject_id=ts.subject_id and teacher_id=%s
    """, (teacher_id,))

    subjects = cursor.fetchall()
    connection.close()

    return jsonify(subjects)



# --------------------- FETCH STUDENTS BASED ON COURSE (AJAX) ---------------------
@app.route("/get_students", methods=["POST"])
def get_students():
    course_name = request.form["course_name"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM students
        WHERE course_name = %s 
    """, (course_name,))
    
    students = cursor.fetchall()
    
    connection.close()
    return jsonify(students)

@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    course_name = request.form.get("course_name")
    subject_name = request.form.get("subject_name")
    selected_date = request.form.get("date")
    teacher_id = session.get("teacher_id")

    # Fetch subject_id from subjects table based on subject_name
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT subject_id FROM subjects WHERE subject_name = %s
    """, (subject_name,))

    subject = cursor.fetchone()

    if not subject:
        connection.close()
        flash("Subject not found.", "danger")  # Using flash to display error
        return redirect("/attendance")  # Redirect back to the form page

    subject_id = subject["subject_id"]

    # Prepare the attendance records
    students = request.form.getlist("student_id[]")
    statuses = {key.split("_")[1]: request.form.get(key) for key in request.form if key.startswith("status_")}

    attendance_records = [
        (student_id, teacher_id, course_name, subject_id, selected_date, statuses.get(student_id))
        for student_id in students
    ]

    try:
        cursor.executemany("""
            INSERT INTO attendance (student_id, teacher_id, course_name, subject_id, date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, attendance_records)
        connection.commit()
    except Exception as e:
        connection.rollback()
        flash(f"Error: {str(e)}", "danger")
        return redirect("/attendance")

    connection.close()
    flash("Attendance successfully recorded!", "success")
    return redirect("/attendance")  # Redirect after successful submission

@app.route("/update_marks", methods=["GET", "POST"])
def update_marks():
    if "teacher_id" not in session:
        return redirect(url_for("staff_login"))  # Redirect if not logged in

    teacher_id = session["teacher_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch all students assigned to this teacher
    cursor.execute("""
        SELECT s.student_id, s.name 
        FROM students s 
        JOIN teacher_student_assignments ts ON s.student_id = ts.student_id
        WHERE ts.teacher_id = %s
    """, (teacher_id,))
    students = cursor.fetchall()

    if request.method == "POST":
        search_query = request.form.get("search_query")

        # Fetch students matching the search query (either by student_id or name)
        cursor.execute("""
            SELECT s.student_id, s.name 
            FROM students s 
            JOIN teacher_student_assignments ts ON s.student_id = ts.student_id
            WHERE ts.teacher_id = %s AND (s.student_id LIKE %s OR s.name LIKE %s)
        """, (teacher_id, f"%{search_query}%", f"%{search_query}%"))
        students = cursor.fetchall()

    connection.close()

    return render_template("update_marks.html", students=students,teacher_id=teacher_id)
@app.route("/update_marks/<int:student_id>", methods=["GET", "POST"])
def update_marks_form(student_id):
    if "teacher_id" not in session:
        return redirect(url_for("staff_login"))  # Redirect if not logged in

    teacher_id = session["teacher_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch the student info to display on the form
    cursor.execute("SELECT student_id, name FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    if not student:
        connection.close()
        flash("Student not found", "danger")
        return redirect(url_for('staff_dashboard'))  # Redirect if student not found

    # Fetch distinct exam names for the student
    cursor.execute("SELECT DISTINCT examname FROM student_marks WHERE student_id = %s", (student_id,))
    exam_names = [row["examname"] for row in cursor.fetchall()]

    # Handle POST request to update marks
    if request.method == "POST":
        test_name = request.form.get("test_name")
        marks = request.form.get("marks")

        if not test_name or not marks:
            flash("Please enter both test name and marks", "danger")
            return redirect(url_for('update_marks_form', student_id=student_id))

        try:
            cursor.execute("""
                UPDATE student_marks
                SET marks_got = %s
                WHERE examname = %s AND student_id = %s
            """, (marks, test_name, student_id))
            connection.commit()

            flash(f"Marks updated for {student['name']}", "success")
            return redirect(url_for('update_marks_form',student_id=student_id))  # Redirect after successful update
        except Exception as e:
            connection.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('update_marks_form', student_id=student_id))

    connection.close()

    return render_template("update_marks_form.html", student=student, exam_names=exam_names)

@app.route('/modify_attendance', methods=['GET'])
def modify_attendance():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        teacher_id = session.get("teacher_id")

        if not teacher_id:
            flash("Unauthorized access. Please log in.", "danger")
            return redirect(url_for('staff_login'))
        
        # Fetch students assigned to the teacher
        cursor.execute("""
            SELECT s.student_id, s.security_number, s.name 
            FROM students s 
            JOIN teacher_student_assignments ts 
            ON s.student_id = ts.student_id 
            WHERE ts.teacher_id = %s
        """, (teacher_id,))  # Tuple format
        
        students = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('modify_attendance.html', students=students, teacher_id=teacher_id)
    
    except Exception as e:
        flash(f"Error fetching students: {e}", "danger")
        return redirect(url_for('staff_dashboard',teacher_id=teacher_id))  # Redirect to a safe page
@app.route('/update_attendance/<int:student_id>', methods=['GET', 'POST'])
def update_attendance(student_id):
    teacher_id = session.get("teacher_id")

    if not teacher_id:
        flash("Unauthorized access. Please log in.", "danger")
        return redirect(url_for('staff_login'))

    if request.method == 'POST':
        date = request.form.get('date')
        status = request.form.get('attendance')  # 'Present' or 'Absent'

        if not date or not status:
            flash("Please provide both date and attendance status.", "danger")
            return redirect(url_for('update_attendance', student_id=student_id))

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check if attendance record exists
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE student_id = %s AND date = %s AND teacher_id = %s
            """, (student_id, date, teacher_id))
            
            record = cursor.fetchone()

            if record:
                # Update existing attendance record
                cursor.execute("""
                    UPDATE attendance 
                    SET status = %s 
                    WHERE student_id = %s AND date = %s AND teacher_id = %s
                """, (status, student_id, date, teacher_id))
            else:
                flash(f"No record found for this day!", "danger")
                

            connection.commit()
            cursor.close()
            connection.close()
            
            flash("Attendance updated successfully!", "success")

        except Exception as e:
            flash(f"Error updating attendance: {e}", "danger")

        return redirect(url_for('modify_attendance'))

    # GET request: display the form with the student ID
    return render_template('update_attendance.html', student_id=student_id)

@app.route('/student_performance/<int:teacher_id>')
def student_performance(teacher_id):
    course_name = request.args.get('course_name', '')  # Get course_name from query params
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch distinct exam names based on selected course
    exams_query = """
        SELECT DISTINCT e.examname 
        FROM student_marks e 
        JOIN students s ON e.student_id = s.student_id 
        WHERE e.teacher_id = %s
    """
    exams_params = [teacher_id]

    if course_name:
        exams_query += " AND s.course_name = %s"
        exams_params.append(course_name)

    exams_query += " ORDER BY e.examname"
    cursor.execute(exams_query, tuple(exams_params))
    exams = [row[0] for row in cursor.fetchall()]  # List of exam names

    # Fetch distinct course names for the teacher
    cursor.execute("""
        SELECT DISTINCT s.course_name 
        FROM students s 
        JOIN teacher_student_assignments ts ON ts.student_id = s.student_id
        WHERE ts.teacher_id = %s
    """, (teacher_id,))
    course_names = [row[0] for row in cursor.fetchall()]  # List of course names

    # Fetch student marks with exam names, filtering by course if provided
    marks_query = """
        SELECT s.name, sm.examname, sm.marks_got 
        FROM students s 
        JOIN student_marks sm ON s.student_id = sm.student_id 
        WHERE sm.teacher_id = %s
    """
    marks_params = [teacher_id]

    if course_name:
        marks_query += " AND s.course_name = %s"
        marks_params.append(course_name)

    marks_query += " ORDER BY s.name, sm.examname"
    cursor.execute(marks_query, tuple(marks_params))
    marks_data = cursor.fetchall()

    # Fetch attendance and calculate percentage, filtering by course if provided
    attendance_query = """
        SELECT s.name, 
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_days,
               COUNT(a.status) AS total_days
        FROM students s 
        JOIN attendance a ON s.student_id = a.student_id 
        WHERE a.teacher_id = %s
    """
    attendance_params = [teacher_id]

    if course_name:
        attendance_query += " AND s.course_name = %s"
        attendance_params.append(course_name)

    attendance_query += " GROUP BY s.name"
    cursor.execute(attendance_query, tuple(attendance_params))
    attendance_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Organizing data in a structured dictionary
    student_performance = {}

    # Initialize dictionary with student names and empty marks for all exams
    for name, exam_name, marks_got in marks_data:
        if name not in student_performance:
            student_performance[name] = {"attendance": 0, "exams": {exam: "-" for exam in exams}}  # Default "-" for missing exams

        student_performance[name]["exams"][exam_name] = marks_got  # Update with actual marks

    # Process attendance
    for name, present_days, total_days in attendance_data:
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        if name in student_performance:
            student_performance[name]['attendance'] = round(attendance_percentage, 2)

    return render_template(
        'student_performance.html', 
        students=student_performance, 
        exams=exams, 
        course_names=course_names,
        selected_course=course_name,
        teacher_id=teacher_id
    )

@app.route('/generate_pdf/<int:teacher_id>/<string:course_name>', methods=['GET'])
def generate_pdf(teacher_id, course_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch distinct exam names for the given course
    cursor.execute("""
        SELECT DISTINCT sm.examname 
        FROM student_marks sm
        JOIN students s ON sm.student_id = s.student_id
        WHERE sm.teacher_id = %s AND s.course_name = %s
        ORDER BY sm.examname
    """, (teacher_id, course_name))
    exams = [row[0] for row in cursor.fetchall()]

    # Fetch student marks for the given course
    cursor.execute("""
        SELECT s.name, sm.examname, sm.marks_got 
        FROM students s 
        JOIN student_marks sm ON s.student_id = sm.student_id 
        WHERE sm.teacher_id = %s AND s.course_name = %s
        ORDER BY s.name, sm.examname
    """, (teacher_id, course_name))
    marks_data = cursor.fetchall()

    # Fetch attendance data for the given course
    cursor.execute("""
        SELECT s.name, 
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_days,
               COUNT(a.status) AS total_days
        FROM students s 
        JOIN attendance a ON s.student_id = a.student_id 
        WHERE a.teacher_id = %s AND s.course_name = %s
        GROUP BY s.name
    """, (teacher_id, course_name))
    attendance_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Organizing data into a structured dictionary
    student_performance = {}

    # Initialize dictionary with student names and exams
    for name, exam_name, marks_got in marks_data:
        if name not in student_performance:
            student_performance[name] = {"attendance": 0, "exams": {exam: "-" for exam in exams}}
        student_performance[name]["exams"][exam_name] = marks_got

    # Process attendance data
    for name, present_days, total_days in attendance_data:
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        if name in student_performance:
            student_performance[name]['attendance'] = round(attendance_percentage, 2)

    # Generate PDF using ReportLab
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Prepare data for the table (add headers)
    def create_table_for_page(exams_subset):
        table_data_subset = [["Student Name", "Attendance (%)"] + exams_subset]
        for name, data in student_performance.items():
            row = [name, str(data['attendance']) + "%"]
            for exam in exams_subset:
                row.append(str(data['exams'].get(exam, "-")))
            table_data_subset.append(row)

        # Create the Table object
        table = Table(table_data_subset, colWidths=[120, 60] + [80] * len(exams_subset))

        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ])

        table.setStyle(style)
        return table

    # Split exams into chunks of 4 exams each
    exams_per_page = 4
    pages_needed = (len(exams) // exams_per_page) + (1 if len(exams) % exams_per_page > 0 else 0)

    # Store elements for the document
    elements = []

    # Loop over each page, generating a table for the subset of exams
    for page in range(pages_needed):
        exams_subset = exams[page * exams_per_page: (page + 1) * exams_per_page]
        table = create_table_for_page(exams_subset)
        elements.append(table)

        if page < pages_needed - 1:
            elements.append(PageBreak())  # Create a new page if necessary

    # Build the document with all pages
    doc.build(elements)

    pdf_buffer.seek(0)

    # Send the generated PDF as a downloadable file
    return send_file(pdf_buffer, as_attachment=True, download_name=f'student_performance_{course_name}.pdf', mimetype='application/pdf')



@app.route('/student_dashboard/<int:student_id>')
def student_dashboard(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the student's details (name, security_number)
    cursor.execute("""SELECT name, security_number FROM students WHERE student_id=%s""", (student_id,))
    student = cursor.fetchone()

    if student:
        student_name, security_number = student
    else:
        student_name, security_number = "Unknown", "N/A"  # Default values if no student found

    # Fetch subjects assigned to the student
    cursor.execute("""
        SELECT s.subject_name, s.subject_id
        FROM subjects s
        JOIN teacher_student_assignments ts ON ts.subject_id = s.subject_id
        WHERE ts.student_id = %s
    """, (student_id,))

    # Create a list of dictionaries with subject_name and subject_id
    subjects = [{"subject_name": row[0], "subject_id": row[1]} for row in cursor.fetchall()]

    # Fetch average marks per subject
    cursor.execute("""
        SELECT s.subject_name, AVG(sm.marks_got) AS avg_marks
        FROM subjects s
        JOIN student_marks sm ON sm.subject_id = s.subject_id
        WHERE sm.student_id = %s
        GROUP BY s.subject_name
    """, (student_id,))
    marks_data = dict(cursor.fetchall())  # {subject_name: avg_marks}

    # Fetch attendance percentage per subject
    attendance_data = {}
    for subject in subjects:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_days,
                COUNT(a.status) AS total_days
            FROM attendance a
            WHERE a.student_id = %s AND a.subject_id = %s
        """, (student_id, subject["subject_id"]))
        
        attendance_result = cursor.fetchone()
        present_days, total_days = attendance_result if attendance_result else (0, 0)
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        attendance_data[subject["subject_name"]] = round(attendance_percentage, 2)

    cursor.close()
    conn.close()

    return render_template('student_dashboard.html', 
                           subjects=subjects,  # Pass the list of subjects with both name and id
                           marks_data=marks_data, 
                           attendance_data=attendance_data,
                           student_name=student_name, 
                           security_number=security_number,
                           student_id=student_id)

@app.route('/check_exam/<int:student_id>/<int:subject_id>', methods=['GET'])
def check_exam(student_id, subject_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step 1: Get teacher_id from the teacher_student_assignments table
    cursor.execute("""
        SELECT teacher_id 
        FROM teacher_student_assignments 
        WHERE subject_id = %s AND student_id = %s;
    """, (subject_id, student_id))
    teacher_id = cursor.fetchone()
    cursor.execute("""select subject_name from subjects where subject_id=%s""",(subject_id,))
    subject_name=cursor.fetchall()
    subject_name = subject_name[0] if subject_name else "Unknown Subject"

    if not teacher_id:
        return render_template('error.html', message="Teacher not found for this subject/student")

    teacher_id = teacher_id[0]
    cursor.execute('''select name,Email,Mobile_no from teachers where teacher_id=%s''',(teacher_id,))
    teacher_details=cursor.fetchall() # Extract teacher_id from the result

    # Step 2: Get distinct exam names for the teacher
    cursor.execute("""
        SELECT DISTINCT examname 
        FROM student_marks 
        WHERE teacher_id = %s 
        ORDER BY examname;
    """, (teacher_id,))
    exam_names = [row[0] for row in cursor.fetchall()]

    # Step 3: Get the marks and maximum_marks for the student in each exam for the subject
    cursor.execute("""
        SELECT sm.examname, sm.marks_got, sm.maximum_marks
        FROM student_marks sm
        WHERE sm.student_id = %s AND sm.subject_id = %s
        ORDER BY sm.examname;
    """, (student_id, subject_id))
    marks_data = cursor.fetchall()

  
    cursor.close()
    conn.close()

    # Prepare data for rendering
    marks_per_exam = {exam: {"marks_got": None, "maximum_marks": None} for exam in exam_names}  # Initialize with None
    for exam, marks_got, maximum_marks in marks_data:
        marks_per_exam[exam] = {"marks_got": marks_got, "maximum_marks": maximum_marks}

    
    return render_template('exam_dashboard.html', student_id=student_id, subject_id=subject_id, 
                           marks_per_exam=marks_per_exam,subject_name=subject_name,teacher_details=teacher_details)

@app.route('/applications', methods=['GET'])
def applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Application_id, course_name, child_name, 
               child_previous_score, parent_mobile_number, parent_email 
        FROM applications
    """)
    applications = cursor.fetchall()
    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
        return jsonify(applications)

    return render_template('show_applications.html', applications=applications)

@app.route('/get_students_data', methods=['GET'])
def get_students_data():
    try:
        # Establish DB connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT name, course_name, security_number, birth_date, medium FROM students")
        students = cursor.fetchall()

        cursor.close()
        connection.close()
    
        # Pass data to the template
        return render_template('students.html', students=students)

    except Exception as e:
        # Log error for debugging
        print(f"Error fetching students data: {e}")
        return render_template('students.html', error=f"Error: {e}")

@app.route('/get_teachers_data', methods=['GET'])
def get_teachers_data():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Query to fetch teacher details excluding teacher_id and password
        cursor.execute("""
            SELECT name, teacher_security_key, Email, Mobile_no
            FROM teachers
        """)
        teachers = cursor.fetchall()

        cursor.close()
        connection.close()

        # Debug log to confirm data is fetched
       
        # Return the template with teacher data
        return render_template('teachers.html', teachers=teachers)

    except Exception as e:
        print(f"Error fetching teachers data: {e}")
        return render_template('teachers.html', error=f"Error: {e}")
    
@app.route('/get_attendance_data/<int:student_id>/<int:subject_id>')
def get_attendance_data(student_id, subject_id):
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch teacher_id for the student and subject
        cursor.execute("""
            SELECT teacher_id 
            FROM teacher_student_assignments 
            WHERE subject_id = %s AND student_id = %s;
        """, (subject_id, student_id))
        teacher_id = cursor.fetchone()

        # Fetch subject name
        cursor.execute("SELECT subject_name FROM subjects WHERE subject_id = %s", (subject_id,))
        subject_name = cursor.fetchone()
        subject_name = subject_name['subject_name'] if subject_name else "Unknown Subject"

        if not teacher_id:
            return render_template('error.html', message="Teacher not found for this subject/student")

        # Fetch teacher details
        cursor.execute("SELECT name, Email, Mobile_no FROM teachers WHERE teacher_id = %s", (teacher_id['teacher_id'],))
        teacher_details = cursor.fetchone()  # Use fetchone() to get a single dictionary

        # Fetch dates where the student was present
        cursor.execute("""
            SELECT date
            FROM attendance
            WHERE student_id = %s AND subject_id = %s AND status = 'Present'
        """, (student_id, subject_id))
        present_dates = cursor.fetchall()

        # Fetch dates where the student was absent
        cursor.execute("""
            SELECT date
            FROM attendance
            WHERE student_id = %s AND subject_id = %s AND status = 'Absent'
        """, (student_id, subject_id))
        absent_dates = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Render the template with attendance data and teacher details
        return render_template('attendance_info.html', 
                               present_dates=present_dates, 
                               absent_dates=absent_dates, 
                               student_id=student_id, 
                               subject_id=subject_id,
                               teacher_details=teacher_details,
                               subject_name=subject_name)
    
    except Exception as e:
        # Handle any unexpected errors
        return render_template('error.html', message=f"Error fetching attendance data: {e}")
    
@app.route('/about')
def about():
    return render_template('about.html')
    
if __name__ == '__main__':
    app.run(debug=True)
