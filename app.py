import os
import json
import requests
import re
import uuid
from flask import Flask, jsonify, render_template, request, redirect, session, flash, url_for
from flask_mysqldb import MySQL
from datetime import timedelta, datetime, date
from werkzeug.utils import secure_filename
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# ============ Configuration ============
app.secret_key = 'zitconnect_secret_key_2024'
app.permanent_session_lifetime = timedelta(minutes=30)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'zitconnect_db'

mysql = MySQL(app)

# Lenco Configuration
LENCO_BASE_URL = "https://api.lenco.co/access/v2/"
#LENCO_BASE_URL = os.getenv("LENCO_BASE_URL", "https://api.lenco.co/access/v2/")
LENCO_SECRET_KEY = os.getenv("LENCO_SECRET_KEY")
LENCO_PUBLIC_KEY = os.getenv("LENCO_PUBLIC_KEY")
LENCO_SIGNATURE = os.getenv("LENCO_SIGNATURE")

# Payment simulation mode – set to False when real credentials work
SIMULATE_PAYMENT = False

# ============ Helper Functions ============
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def _redirect_on_error():
    """Redirect users to the appropriate dashboard based on their role."""
    if 'userID' in session:
        role = session.get('role')
        if role == 'student':
            return redirect('/student-dashboard')
        elif role == 'tutor':
            return redirect('/tutor-dashboard')
        elif role == 'admin':
            return redirect('/admin')
    return redirect('/login')

def get_programs():
    """Fetch all programs from database"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT programID, programName FROM program ORDER BY programName")
        programs = cursor.fetchall()
        cursor.close()
        return programs
    except Exception as e:
        print(f"Error fetching programs: {e}")
        return []

def get_schools():
    """Fetch all schools from database"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT schoolID, schoolName FROM school ORDER BY schoolName")
        schools = cursor.fetchall()
        cursor.close()
        return schools
    except Exception as e:
        print(f"Error fetching schools: {e}")
        return []

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============ Routes ============

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    # Return a 204 No Content so the browser doesn't trigger a 404
    return '', 204

@app.route('/register1')
def register1_redirect():
    """Legacy /register1 route redirect to /register"""
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register Step 1 - Collect user information"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not all([name, username, email, password, confirm_password]):
                flash('All fields are required', 'error')
                return render_template('register1.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register1.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'error')
                return render_template('register1.html')
            
            if not validate_email(email):
                flash('Invalid email format', 'error')
                return render_template('register1.html')
            
            # Check if username already exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT userID FROM user WHERE userName = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                flash('Username already exists. Please choose a different one.', 'error')
                return render_template('register1.html')
            
            # Check if email already exists
            cursor.execute("SELECT userID FROM user WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                flash('Email already exists. Please use a different email.', 'error')
                return render_template('register1.html')
            
            cursor.close()
            
            # Store in session
            session['name'] = name
            session['username'] = username
            session['email'] = email
            session['password'] = password
            
            return redirect('/register/step2')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template('register1.html')
    
    return render_template('register1.html')

@app.route('/register/step2', methods=['GET'])
def register_step2():
    """Register Step 2 - Select program, school, and role"""
    # Check if user has completed step 1
    if 'email' not in session:
        flash('Please complete step 1 first', 'error')
        return redirect('/register')
    
    programs = get_programs()
    schools = get_schools()
    
    return render_template('register2.html', programs=programs, schools=schools)

#Fetch programs and courses based on school selection for dynamic dropdowns in registration step 2
@app.route('/api/programs/<int:schoolID>')
def api_get_programs(schoolID):
    """API endpoint to get programs for a specific school"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT programID, programName FROM program WHERE schoolID = %s ORDER BY programName",
            (schoolID,)
        )
        programs = cursor.fetchall()
        cursor.close()
        
        programs_list = [{'programID': p[0], 'programName': p[1]} for p in programs]
        return {'programs': programs_list}
    except Exception as e:
        print(f"Error fetching programs: {e}")
        return {'programs': [], 'error': str(e)}

@app.route('/api/courses/<int:schoolID>')
def api_get_courses(schoolID):
    """API endpoint to get courses for a specific school"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT courseCode, courseName FROM course WHERE schoolID = %s ORDER BY courseCode",
            (schoolID,)
        )
        courses = cursor.fetchall()
        cursor.close()
        
        courses_list = [{'courseCode': c[0], 'courseName': c[1]} for c in courses]
        return {'courses': courses_list}
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return {'courses': [], 'error': str(e)}

# Update the register_complete route
@app.route('/register/complete', methods=['POST'])
def register_complete():
    """Complete registration - Save to database"""
    # Verify step 1 data exists
    if 'email' not in session:
        flash('Session expired. Please register again.', 'error')
        return redirect('/register')
    
    try:
        # Get data from session
        full_name = session.get('name', '')
        user_name = session.get('username', '')
        email = session.get('email', '')
        password = session.get('password', '')
        
        # Get role from form
        role = request.form.get('role', '').strip()
        
        if not role:
            flash('Please select a role', 'error')
            return redirect('/register/step2')
        
        cursor = mysql.connection.cursor()
        
        # Insert into user table
        cursor.execute(
            "INSERT INTO user (fullName, userName, email, password, role, profilePicture) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (full_name, user_name, email, password, role, None)
        )
        user_id = cursor.lastrowid

        # Create role-specific records
        if role == 'student':
            program = request.form.get('program', '').strip()
            if not program:
                flash('Please select a program', 'error')
                return redirect('/register/step2')
            
            cursor.execute(
                "INSERT INTO student (studentID, programID) VALUES (%s, %s)",
                (user_id, program)
            )
            
        elif role == 'tutor':
            # Get tutor-specific data
            school = request.form.get('tutor_school', '').strip()
            program = request.form.get('tutor_program', '').strip()
            selected_courses = request.form.getlist('tutor_courses')
            
            if not school or not program:
                flash('Please select school and program', 'error')
                return redirect('/register/step2')
            
            if not selected_courses:
                flash('Please select at least one course you want to tutor', 'error')
                return redirect('/register/step2')
            
            # Create tutor record
            cursor.execute(
                "INSERT INTO tutor (tutorID, verificationStatus, averageRating) VALUES (%s, %s, %s)",
                (user_id, 'pending', 0.00)
            )
            
            # Insert selected courses into tutorcourse table
            for course_code in selected_courses:
                cursor.execute(
                    "INSERT INTO tutorcourse (tutorID, courseCode, gradeObtained) VALUES (%s, %s, %s)",
                    (user_id, course_code, 'pending')  # gradeObtained can be updated later
                )
            
        elif role == 'admin':
            # Handle admin registration if needed
            pass

        mysql.connection.commit()
        cursor.close()
        
        # Clear session
        session.clear()
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Registration error: {str(e)}', 'error')
        print(f"Registration Error: {e}")
        return redirect('/register/step2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        try:
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '').strip()
            
            if not identifier or not password:
                flash('Email/Username and password are required', 'error')
                return render_template('login.html')
            
            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT userID, fullName, role FROM user WHERE (userName = %s OR email = %s) AND password = %s",
                (identifier, identifier, password)
            )
            user = cursor.fetchone()
            
            if user:
                session.permanent = True
                session['userID'] = user[0]
                session['fullName'] = user[1]
                session['role'] = user[2]
                
                # Redirect based on role
                if user[2] == 'student':
                    flash(f'Welcome, {user[1]}!', 'success')
                    return redirect('/student-dashboard')
                elif user[2] == 'tutor':
                    # Check tutor verification status
                    cursor.execute(
                        "SELECT verificationStatus, averageRating FROM tutor WHERE tutorID = %s",
                        (user[0],)
                    )
                    tutor_info = cursor.fetchone()
                    cursor.close()
                    
                    if tutor_info:
                        tutor_status = tutor_info[0]
                        average_rating = tutor_info[1]
                        
                        # Store verification status in session
                        session['tutor_verification_status'] = tutor_status
                        session['tutor_rating'] = float(average_rating) if average_rating else 0.0
                        
                        if tutor_status == 'approved':
                            flash(f'Welcome, {user[1]}! Your tutor account is fully verified.', 'success')
                            return redirect('/tutor-dashboard')
                        elif tutor_status == 'pending':
                            flash('Welcome! Please complete your profile verification to earn badges.', 'warning')
                            return redirect('/tutor-dashboard')
                        elif tutor_status == 'rejected':
                            flash('Your tutor application has been rejected. Please contact support for more information.', 'error')
                            return redirect('/tutor-dashboard')
                        else:
                            flash('Welcome! Please complete your profile setup.', 'warning')
                            return redirect('/tutor-dashboard')
                    else:
                        flash('Tutor account not properly configured. Please contact support.', 'error')
                        return redirect('/login')
                elif user[2] == 'admin':
                    flash(f'Welcome, {user[1]}!', 'success')
                    return redirect('/admin')
            else:
                flash('Invalid username/email or password', 'error')
                return render_template('login.html')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/tutor-profile', methods=['GET', 'POST'])
def tutor_profile():
    """Tutor profile management - view and edit details, upload docs"""
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login to access your profile', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()

        if request.method == 'POST':
            action = request.form.get('action', 'update_info')

            if action == 'update_info':
                full_name = request.form.get('fullName', '').strip()
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '').strip()
                bio = request.form.get('bio', '').strip()

                if not full_name or not username:
                    flash('Name and username are required', 'error')
                else:
                    # Check if new username already exists (excluding current user)
                    cursor.execute(
                        "SELECT userID FROM user WHERE userName = %s AND userID != %s",
                        (username, session['userID'])
                    )
                    if cursor.fetchone():
                        flash('Username already taken', 'error')
                    else:
                        # Update user info
                        if password:
                            cursor.execute(
                                "UPDATE user SET fullName = %s, userName = %s, password = %s WHERE userID = %s",
                                (full_name, username, password, session['userID'])
                            )
                            session['fullName'] = full_name
                        else:
                            cursor.execute(
                                "UPDATE user SET fullName = %s, userName = %s WHERE userID = %s",
                                (full_name, username, session['userID'])
                            )
                            session['fullName'] = full_name

                        # Update tutor bio
                        cursor.execute(
                            "UPDATE tutor SET bio = %s WHERE tutorID = %s",
                            (bio, session['userID'])
                        )

                        mysql.connection.commit()
                        flash('Profile updated successfully', 'success')
                        return redirect('/tutor-profile')

            elif action == 'upload_profile_pic':
                profile_pic = request.files.get('profilePic')
                if not profile_pic or profile_pic.filename == '':
                    flash('Please choose an image to upload', 'error')
                elif profile_pic.filename.rsplit('.', 1)[1].lower() not in {'jpg', 'jpeg', 'png'}:
                    flash('Only JPG, JPEG and PNG images are allowed', 'error')
                else:
                    filename = secure_filename(f"profile_{session['userID']}_{profile_pic.filename}")
                    upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'profile_pics')
                    os.makedirs(upload_folder, exist_ok=True)

                    save_path = os.path.join(upload_folder, filename)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(save_path):
                        filename = f"{base}_{counter}{ext}"
                        save_path = os.path.join(upload_folder, filename)
                        counter += 1

                    profile_pic.save(save_path)
                    relative_path = f"uploads/profile_pics/{filename}"

                    cursor.execute(
                        "UPDATE user SET profilePicture = %s WHERE userID = %s",
                        (relative_path, session['userID'])
                    )
                    mysql.connection.commit()
                    flash('Profile picture updated successfully', 'success')
                    return redirect('/tutor-profile')

            elif action == 'upload_doc':
                document = request.files.get('document')
                if not document or document.filename == '':
                    flash('Please choose a document to upload', 'error')
                    return redirect('/tutor-profile')
                
                if not allowed_file(document.filename):
                    flash('Only PDF, JPG, JPEG and PNG files are allowed', 'error')
                    return redirect('/tutor-profile')
                
                # Create upload folder if it doesn't exist
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)

                # Secure the filename and save
                filename = secure_filename(document.filename)
                # Add timestamp to prevent filename conflicts
                import time
                name, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                filename = f"{name}_{timestamp}{ext}"
                
                save_path = os.path.join(upload_folder, filename)
                document.save(save_path)
                relative_path = f"uploads/{filename}"

                # Insert into verificationdocument with documentType
                # Determine document type based on filename or default to 'result_slip'
                document_type = 'result_slip'  # default
                if 'transcript' in filename.lower():
                    document_type = 'transcript'
                
                cursor.execute(
                    "INSERT INTO verificationdocument (tutorID, documentType, filePath, approvalStatus) VALUES (%s, %s, %s, 'pending')",
                    (session['userID'], document_type, relative_path)
                )
                mysql.connection.commit()
                flash('Document uploaded successfully and submitted for verification.', 'success')
                return redirect('/tutor-profile')

        # GET request - fetch all data
        # Get tutor info
        cursor.execute(
            "SELECT fullName, userName, email, profilePicture FROM user WHERE userID = %s",
            (session['userID'],)
        )
        user_info = cursor.fetchone()

        # Get tutor verification status and bio
        cursor.execute(
            "SELECT verificationStatus, averageRating, IFNULL(bio,'') FROM tutor WHERE tutorID = %s",
            (session['userID'],)
        )
        tutor_info = cursor.fetchone()

        # Get uploaded documents
        cursor.execute(
            "SELECT documentID, filePath, approvalStatus, uploadDate FROM verificationdocument WHERE tutorID = %s ORDER BY uploadDate DESC",
            (session['userID'],)
        )
        documents = cursor.fetchall()

        # Get courses
        cursor.execute(
            "SELECT tc.courseCode, c.courseName FROM tutorcourse tc JOIN course c ON tc.courseCode = c.courseCode WHERE tc.tutorID = %s",
            (session['userID'],)
        )
        courses = cursor.fetchall()

        cursor.close()

        return render_template('tutor_profile.html',
                             fullName=user_info[0] if user_info else '',
                             username=user_info[1] if user_info else '',
                             email=user_info[2] if user_info else '',
                             profilePicture=user_info[3] if user_info else '',
                             verificationStatus=tutor_info[0] if tutor_info else 'pending',
                             averageRating=float(tutor_info[1]) if tutor_info and tutor_info[1] else 0.0,
                             bio=tutor_info[2] if tutor_info and len(tutor_info) > 2 else '',
                             documents=[{'documentID': d[0], 'filePath': d[1], 'approvalStatus': d[2], 'uploadDate': d[3]} for d in documents],
                             courses=[{'courseCode': c[0], 'courseName': c[1]} for c in courses])

    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        print(f"Profile Error: {e}")
        import traceback
        traceback.print_exc()
        if 'cursor' in locals():
            cursor.close()
        return redirect('/tutor-dashboard')

@app.route('/tutor-dashboard')
def tutor_dashboard():
    """Tutor dashboard route with real data and verification status"""
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login to access the dashboard', 'error')
        return redirect('/login')
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get tutor verification status
        cursor.execute(
            "SELECT verificationStatus, averageRating FROM tutor WHERE tutorID = %s",
            (session['userID'],)
        )
        tutor_info = cursor.fetchone()
        verification_status = tutor_info[0] if tutor_info else 'pending'
        average_rating = float(tutor_info[1]) if tutor_info and tutor_info[1] else 0.0
        
        # Check if tutor has uploaded any documents
        cursor.execute(
            "SELECT COUNT(*) FROM verificationdocument WHERE tutorID = %s",
            (session['userID'],)
        )
        doc_count = cursor.fetchone()[0]
        has_uploaded_docs = doc_count > 0
        
        # Check if tutor has added courses
        cursor.execute(
            "SELECT COUNT(*) FROM tutorcourse WHERE tutorID = %s",
            (session['userID'],)
        )
        course_count = cursor.fetchone()[0]
        has_added_courses = course_count > 0
        
        # Check if tutor has approved documents
        cursor.execute(
            "SELECT COUNT(*) FROM verificationdocument WHERE tutorID = %s AND approvalStatus = 'approved'",
            (session['userID'],)
        )
        approved_docs = cursor.fetchone()[0]
        has_approved_docs = approved_docs > 0
        
        # Auto-verify tutor if they have approved documents AND courses
        if has_approved_docs and has_added_courses and verification_status == 'pending':
            cursor.execute(
                "UPDATE tutor SET verificationStatus = 'approved' WHERE tutorID = %s",
                (session['userID'],)
            )
            mysql.connection.commit()
            verification_status = 'approved'
            flash('Congratulations! Your account has been fully verified!', 'success')
        
        # Check if tutor has earned any badges
        cursor.execute(
            """
            SELECT b.badgeName, b.criteriaDescription 
            FROM badge b 
            JOIN tutorbadge tb ON b.badgeID = tb.badgeID 
            WHERE tb.tutorID = %s
            """,
            (session['userID'],)
        )
        badges = cursor.fetchall()
        
        # Get ALL sessions for this tutor
        cursor.execute(
            """
            SELECT s.sessionID, s.courseCode, s.scheduledDate, s.scheduledTime, 
                   s.sessionType, s.status, u.fullName as studentName,
                   s.studentID
            FROM `session` s 
            JOIN user u ON s.studentID = u.userID 
            WHERE s.tutorID = %s 
            ORDER BY 
                CASE s.status 
                    WHEN 'pending' THEN 1 
                    WHEN 'confirmed' THEN 2 
                    WHEN 'completed' THEN 3 
                    WHEN 'cancelled' THEN 4 
                    WHEN 'declined' THEN 5
                    ELSE 6
                END,
                s.scheduledDate ASC, s.scheduledTime ASC
            """,
            (session['userID'],)
        )
        all_sessions = cursor.fetchall()
        
        # Separate sessions by status
        pending_sessions = []
        confirmed_sessions = []
        completed_sessions = []
        cancelled_sessions = []
        declined_sessions = []
        
        for sess in all_sessions:
            scheduled_date = sess[2]
            if scheduled_date:
                if hasattr(scheduled_date, 'strftime'):
                    formatted_date = scheduled_date.strftime('%Y-%m-%d')
                else:
                    formatted_date = str(scheduled_date)
            else:
                formatted_date = 'N/A'
            
            scheduled_time = sess[3]
            if scheduled_time:
                if hasattr(scheduled_time, 'strftime'):
                    formatted_time = scheduled_time.strftime('%H:%M')
                else:
                    formatted_time = str(scheduled_time)
            else:
                formatted_time = 'N/A'
            
            session_data = {
                'sessionID': sess[0],
                'courseCode': sess[1],
                'scheduledDate': formatted_date,
                'scheduledTime': formatted_time,
                'sessionType': sess[4] if sess[4] else 'individual',
                'status': sess[5] if sess[5] else 'pending',
                'studentName': sess[6] if sess[6] else 'Unknown Student',
                'studentID': sess[7]
            }
            
            if sess[5] == 'pending':
                pending_sessions.append(session_data)
            elif sess[5] == 'confirmed':
                confirmed_sessions.append(session_data)
            elif sess[5] == 'completed':
                completed_sessions.append(session_data)
            elif sess[5] == 'cancelled':
                cancelled_sessions.append(session_data)
            elif sess[5] == 'declined':
                declined_sessions.append(session_data)
        
        # Calculate total earnings (only for completed sessions)
        total_earnings = len(completed_sessions) * 50
        
        # Get upcoming confirmed sessions (future dates)
        cursor.execute(
            """
            SELECT s.sessionID, s.courseCode, s.scheduledDate, s.scheduledTime, 
                   s.sessionType, s.status, u.fullName as studentName
            FROM `session` s 
            JOIN user u ON s.studentID = u.userID 
            WHERE s.tutorID = %s AND s.status = 'confirmed' 
            AND s.scheduledDate >= CURDATE() 
            ORDER BY s.scheduledDate ASC, s.scheduledTime ASC
            """,
            (session['userID'],)
        )
        upcoming_sessions_raw = cursor.fetchall()
        upcoming_sessions = []
        for sess in upcoming_sessions_raw:
            scheduled_date = sess[2]
            if scheduled_date:
                if hasattr(scheduled_date, 'strftime'):
                    formatted_date = scheduled_date.strftime('%Y-%m-%d')
                else:
                    formatted_date = str(scheduled_date)
            else:
                formatted_date = 'N/A'
            
            scheduled_time = sess[3]
            if scheduled_time:
                if hasattr(scheduled_time, 'strftime'):
                    formatted_time = scheduled_time.strftime('%H:%M')
                else:
                    formatted_time = str(scheduled_time)
            else:
                formatted_time = 'N/A'
            
            upcoming_sessions.append({
                'sessionID': sess[0],
                'courseCode': sess[1],
                'scheduledDate': formatted_date,
                'scheduledTime': formatted_time,
                'sessionType': sess[4] if sess[4] else 'individual',
                'status': sess[5] if sess[5] else 'confirmed',
                'studentName': sess[6] if sess[6] else 'Unknown Student'
            })
        
        cursor.close()
        
        # Format badges
        badges_list = [{'name': b[0], 'description': b[1]} for b in badges]
        
        return render_template('tutor_dashboard.html', 
                             fullName=session.get('fullName'),
                             verification_status=verification_status,
                             average_rating=average_rating,
                             has_uploaded_docs=has_uploaded_docs,
                             has_added_courses=has_added_courses,
                             has_approved_docs=has_approved_docs,
                             badges=badges_list,
                             total_earnings=total_earnings,
                             pending_count=len(pending_sessions),
                             upcoming_count=len(upcoming_sessions),
                             completed_count=len(completed_sessions),
                             cancelled_count=len(cancelled_sessions),
                             pending_sessions=pending_sessions,
                             confirmed_sessions=confirmed_sessions,
                             completed_sessions=completed_sessions,
                             cancelled_sessions=cancelled_sessions,
                             declined_sessions=declined_sessions,
                             upcoming_sessions=upcoming_sessions)
                             
    except Exception as e:
        print(f"Error loading tutor dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading dashboard data', 'error')
        return render_template('tutor_dashboard.html', 
                             fullName=session.get('fullName'),
                             verification_status='pending',
                             average_rating=0.0,
                             has_uploaded_docs=False,
                             has_added_courses=False,
                             has_approved_docs=False,
                             badges=[],
                             total_earnings=0,
                             pending_count=0,
                             upcoming_count=0,
                             completed_count=0,
                             cancelled_count=0,
                             pending_sessions=[],
                             confirmed_sessions=[],
                             completed_sessions=[],
                             cancelled_sessions=[],
                             declined_sessions=[],
                             upcoming_sessions=[])

@app.route('/student-dashboard')
def student_dashboard():
    """Student dashboard route - shows student sessions and available tutors"""
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login to access the dashboard', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        # Student sessions
        cursor.execute(
            "SELECT s.sessionID, s.courseCode, s.scheduledDate, s.scheduledTime, s.status, u.fullName "
            "FROM `session` s "
            "JOIN user u ON s.tutorID = u.userID "
            "WHERE s.studentID = %s "
            "ORDER BY s.scheduledDate DESC, s.scheduledTime DESC",
            (session['userID'],)
        )
        sessions_raw = cursor.fetchall()

        sessions = [
            {
                'sessionID': row[0],
                'courseCode': row[1],
                'scheduledDate': row[2],
                'scheduledTime': row[3],
                'status': row[4],
                'tutorName': row[5]
            }
            for row in sessions_raw
        ]

        # Fetch approved tutors and their courses
        cursor.execute(
            "SELECT u.userID, u.fullName, u.profilePicture, IFNULL(t.averageRating,0), t.verificationStatus, IFNULL(t.bio,'') "
            "FROM user u JOIN tutor t ON u.userID = t.tutorID "
            "ORDER BY u.fullName"
        )
        tutors_raw = cursor.fetchall()

        tutors = []
        for row in tutors_raw:
            tutor_id = row[0]
            cursor.execute(
                "SELECT c.courseCode, c.courseName FROM tutorcourse tc JOIN course c ON tc.courseCode = c.courseCode WHERE tc.tutorID = %s",
                (tutor_id,)
            )
            courses = cursor.fetchall()
            tutors.append({
                'tutorID': tutor_id,
                'fullName': row[1],
                'profilePicture': row[2],
                'averageRating': float(row[3]) if row[3] else 0.0,
                'verificationStatus': row[4] if len(row) > 4 else 'approved',
                'bio': row[5] if len(row) > 5 else '',
                'courses': [{'courseCode': c[0], 'courseName': c[1]} for c in courses]
            })

        cursor.close()
    except Exception as e:
        print(f"Error loading student dashboard: {e}")
        sessions = []
        tutors = []

    return render_template('student_dashboard.html', fullName=session.get('fullName'), sessions=sessions, tutors=tutors)

@app.route('/student-profile', methods=['GET', 'POST'])
def student_profile():
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student.', 'error')
        return redirect('/login')

    cursor = mysql.connection.cursor()
    user_id = session['userID']

    if request.method == 'POST':
        action = request.form.get('action', 'update_info')

        if action == 'update_info':
            full_name = request.form.get('fullName', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not full_name or not username:
                flash('Full name and username are required.', 'error')
                return redirect('/student-profile')

            # Check if username already exists (excluding current user)
            cursor.execute(
                "SELECT userID FROM user WHERE userName = %s AND userID != %s",
                (username, user_id)
            )
            if cursor.fetchone():
                flash('Username already taken.', 'error')
                return redirect('/student-profile')

            # Update user info
            if password:
                if password != confirm_password:
                    flash('Passwords do not match.', 'error')
                    return redirect('/student-profile')
                if len(password) < 6:
                    flash('Password must be at least 6 characters.', 'error')
                    return redirect('/student-profile')
                cursor.execute(
                    "UPDATE user SET fullName = %s, userName = %s, password = %s WHERE userID = %s",
                    (full_name, username, password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE user SET fullName = %s, userName = %s WHERE userID = %s",
                    (full_name, username, user_id)
                )

            mysql.connection.commit()
            session['fullName'] = full_name  # update session
            flash('Profile updated successfully.', 'success')
            return redirect('/student-profile')

        elif action == 'upload_profile_pic':
            profile_pic = request.files.get('profilePic')
            if not profile_pic or profile_pic.filename == '':
                flash('Please choose an image to upload.', 'error')
                return redirect('/student-profile')

            # Validate file type
            allowed = {'jpg', 'jpeg', 'png'}
            if '.' not in profile_pic.filename or profile_pic.filename.rsplit('.', 1)[1].lower() not in allowed:
                flash('Only JPG, JPEG, and PNG images are allowed.', 'error')
                return redirect('/student-profile')

            # Save file
            filename = secure_filename(f"profile_{user_id}_{profile_pic.filename}")
            upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_folder, exist_ok=True)

            # Avoid overwriting
            base, ext = os.path.splitext(filename)
            counter = 1
            save_path = os.path.join(upload_folder, filename)
            while os.path.exists(save_path):
                filename = f"{base}_{counter}{ext}"
                save_path = os.path.join(upload_folder, filename)
                counter += 1

            profile_pic.save(save_path)
            relative_path = f"uploads/profile_pics/{filename}"

            cursor.execute(
                "UPDATE user SET profilePicture = %s WHERE userID = %s",
                (relative_path, user_id)
            )
            mysql.connection.commit()
            flash('Profile picture updated successfully.', 'success')
            return redirect('/student-profile')

    # GET – fetch current user data
    cursor.execute(
        "SELECT fullName, userName, email, profilePicture FROM user WHERE userID = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash('User not found.', 'error')
        return redirect('/student-dashboard')

    return render_template('student_profile.html',
                           fullName=user[0],
                           userName=user[1],
                           email=user[2],
                           profilePicture=user[3])

@app.route('/tutor/<int:tutorID>')
def view_tutor(tutorID):
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student to view tutor profiles.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        # Get tutor details
        cursor.execute(
            "SELECT u.userID, u.fullName, u.userName, u.profilePicture, u.email, IFNULL(t.averageRating,0), t.verificationStatus, IFNULL(t.bio,'') "
            "FROM user u JOIN tutor t ON u.userID = t.tutorID WHERE u.userID = %s",
            (tutorID,)
        )
        row = cursor.fetchone()
        if not row:
            flash('Tutor not found', 'error')
            return redirect('/student-dashboard')

        # Get tutor courses
        cursor.execute(
            "SELECT c.courseCode, c.courseName FROM tutorcourse tc JOIN course c ON tc.courseCode = c.courseCode WHERE tc.tutorID = %s",
            (tutorID,)
        )
        courses = cursor.fetchall()

        # Get average rating and total count
        cursor.execute(
            "SELECT AVG(stars), COUNT(*) FROM rating WHERE tutorID = %s",
            (tutorID,)
        )
        rating_stats = cursor.fetchone()
        avg_rating = float(rating_stats[0]) if rating_stats[0] else 0.0
        rating_count = rating_stats[1] if rating_stats[1] else 0

        # Check if student has a completed session with this tutor
        has_completed_session = False
        cursor.execute(
            "SELECT sessionID FROM `session` WHERE studentID = %s AND tutorID = %s AND status = 'completed' LIMIT 1",
            (session['userID'], tutorID)
        )
        if cursor.fetchone():
            has_completed_session = True

        # Check if student already rated this tutor
        already_rated = False
        cursor.execute(
            "SELECT ratingID FROM rating WHERE studentID = %s AND tutorID = %s LIMIT 1",
            (session['userID'], tutorID)
        )
        if cursor.fetchone():
            already_rated = True

        cursor.close()

        tutor = {
            'tutorID': row[0],
            'fullName': row[1],
            'userName': row[2],
            'profilePicture': row[3],
            'email': row[4],
            'averageRating': avg_rating,
            'ratingCount': rating_count,
            'verificationStatus': row[6],
            'bio': row[7] if len(row) > 7 else ''
        }

        return render_template('tutor_view.html',
                               fullName=session.get('fullName'),
                               tutor=tutor,
                               courses=[{'courseCode': c[0], 'courseName': c[1]} for c in courses],
                               has_completed_session=has_completed_session,
                               already_rated=already_rated)
    except Exception as e:
        flash(f'Error loading tutor profile: {str(e)}', 'error')
        print(f"Error in view_tutor: {e}")
        return redirect('/student-dashboard')
    
@app.route('/rate-tutor', methods=['POST'])
def rate_tutor():
    if 'userID' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    tutor_id = request.form.get('tutorID', type=int)
    stars = request.form.get('stars', type=int)
    comment = request.form.get('comment', '').strip()

    if not tutor_id or not stars or stars < 1 or stars > 5:
        flash('Invalid rating.', 'error')
        return redirect(request.referrer or '/student-dashboard')

    try:
        cursor = mysql.connection.cursor()
        # Check if student already rated this tutor
        cursor.execute(
            "SELECT ratingID FROM rating WHERE studentID = %s AND tutorID = %s",
            (session['userID'], tutor_id)
        )
        existing = cursor.fetchone()
        if existing:
            flash('You have already rated this tutor.', 'error')
            return redirect(request.referrer or '/student-dashboard')

        # Insert rating (sessionID = NULL)
        cursor.execute(
            "INSERT INTO rating (sessionID, studentID, tutorID, stars, feedbackComment) VALUES (NULL, %s, %s, %s, %s)",
            (session['userID'], tutor_id, stars, comment)
        )
        # Update tutor average rating
        cursor.execute(
            "UPDATE tutor SET averageRating = (SELECT AVG(stars) FROM rating WHERE tutorID = %s) WHERE tutorID = %s",
            (tutor_id, tutor_id)
        )
        mysql.connection.commit()
        cursor.close()
        flash('Thank you for your rating!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error saving rating: {str(e)}', 'error')

    return redirect(request.referrer or '/student-dashboard')

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect('/login')

# ============ Tutor Management Routes ============ #

@app.route('/manage-courses', methods=['GET', 'POST'])
def manage_courses():
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login as a tutor to manage courses.', 'error')
        return redirect('/login')

    tutor_id = session['userID']
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        course_code = request.form.get('courseCode', '').strip()

        if action == 'add':
            if not course_code:
                flash('Please select a course to add.', 'error')
            else:
                cursor.execute(
                    "SELECT tutorCourseID FROM tutorcourse WHERE tutorID = %s AND courseCode = %s",
                    (tutor_id, course_code)
                )
                if cursor.fetchone():
                    flash('You already offer this course.', 'warning')
                else:
                    cursor.execute(
                        "INSERT INTO tutorcourse (tutorID, courseCode, gradeObtained, pricePerSession) VALUES (%s, %s, 'pending', 0.00)",
                        (tutor_id, course_code)
                    )
                    mysql.connection.commit()
                    flash('Course added successfully. Set a price for individual sessions.', 'success')

        elif action == 'remove':
            if not course_code:
                flash('Invalid course.', 'error')
            else:
                cursor.execute(
                    "DELETE FROM tutorcourse WHERE tutorID = %s AND courseCode = %s",
                    (tutor_id, course_code)
                )
                mysql.connection.commit()
                flash('Course removed successfully.', 'success')

        elif action == 'update_price':
            course_code = request.form.get('courseCode', '').strip()
            price = request.form.get('pricePerSession', type=float)
            if not course_code or price is None or price < 0:
                flash('Please enter a valid price (0 or more).', 'error')
            else:
                cursor.execute(
                    "UPDATE tutorcourse SET pricePerSession = %s WHERE tutorID = %s AND courseCode = %s",
                    (price, tutor_id, course_code)
                )
                mysql.connection.commit()
                flash('Price updated successfully.', 'success')

        return redirect('/manage-courses')

    # GET: fetch current courses with price
    cursor.execute("""
        SELECT tc.courseCode, c.courseName, tc.gradeObtained, tc.pricePerSession
        FROM tutorcourse tc
        JOIN course c ON tc.courseCode = c.courseCode
        WHERE tc.tutorID = %s
        ORDER BY c.courseCode
    """, (tutor_id,))
    current_courses = cursor.fetchall()

    # All available courses (not yet offered)
    cursor.execute("""
        SELECT courseCode, courseName
        FROM course
        WHERE courseCode NOT IN (
            SELECT courseCode FROM tutorcourse WHERE tutorID = %s
        )
        ORDER BY courseCode
    """, (tutor_id,))
    available_courses = cursor.fetchall()

    cursor.close()

    return render_template('manage_courses.html',
                           fullName=session.get('fullName'),
                           current_courses=current_courses,
                           available_courses=available_courses)

@app.route('/search', methods=['GET'])
def search():
    """Search for tutors by course code - shows all tutors regardless of verification status"""
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student to search for tutors.', 'error')
        return redirect('/login')
        
    course_code = request.args.get('courseCode', '').strip().upper()  # Convert to uppercase for consistency
    if not course_code:
        flash('Please enter a course code to search.', 'error')
        return redirect('/student-dashboard')

    try:
        cursor = mysql.connection.cursor()
        
        # Get all tutors for the searched course
        cursor.execute("""
            SELECT DISTINCT 
                u.userID, 
                u.fullName, 
                u.profilePicture, 
                t.verificationStatus,
                COALESCE(t.averageRating, 0) as averageRating,
                COALESCE(t.bio, '') as bio,
                tc.courseCode
            FROM tutorcourse tc 
            JOIN tutor t ON tc.tutorID = t.tutorID 
            JOIN user u ON tc.tutorID = u.userID 
            WHERE UPPER(tc.courseCode) = %s 
            ORDER BY 
                CASE t.verificationStatus 
                    WHEN 'approved' THEN 1 
                    WHEN 'pending' THEN 2 
                    ELSE 3 
                END,
                t.averageRating DESC, 
                u.fullName ASC
        """, (course_code,))
        
        tutors_raw = cursor.fetchall()
        
        # Get additional courses for each tutor
        tutors = []
        for row in tutors_raw:
            tutor_id = row[0]
            
            # Get all courses this tutor teaches
            cursor.execute("""
                SELECT c.courseCode 
                FROM tutorcourse tc 
                JOIN course c ON tc.courseCode = c.courseCode 
                WHERE tc.tutorID = %s
            """, (tutor_id,))
            
            all_courses = cursor.fetchall()
            additional_courses = [c[0] for c in all_courses if c[0] != course_code]
            
            tutors.append({
                'tutorID': tutor_id,
                'fullName': row[1],
                'profilePicture': row[2],
                'verificationStatus': row[3],
                'averageRating': float(row[4]) if row[4] else 0.0,
                'bio': row[5] if row[5] else '',
                'courseCode': row[6],
                'additional_courses': additional_courses[:2]  # Show up to 2 additional courses
            })
        
        cursor.close()
        
        # Also suggest similar courses if no tutors found
        similar_courses = []
        if not tutors:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT courseCode, courseName 
                FROM course 
                WHERE courseCode LIKE %s OR courseName LIKE %s
                LIMIT 5
            """, (f'%{course_code}%', f'%{course_code}%'))
            similar_courses = cursor.fetchall()
            cursor.close()
        
        # Count tutors by verification status for display
        approved_count = len([t for t in tutors if t['verificationStatus'] == 'approved'])
        pending_count = len([t for t in tutors if t['verificationStatus'] == 'pending'])
        rejected_count = len([t for t in tutors if t['verificationStatus'] == 'rejected'])
        
        return render_template('search_results.html', 
                             fullName=session.get('fullName'),
                             tutors=tutors, 
                             course_code=course_code,
                             similar_courses=similar_courses,
                             approved_count=approved_count,
                             pending_count=pending_count,
                             rejected_count=rejected_count)
                             
    except Exception as e:
        print(f"Search error: {e}")
        flash(f'Search error: {str(e)}', 'error')
        return redirect('/student-dashboard')

@app.route('/admin')
def admin_dashboard():
    """Admin main dashboard page"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Login to access this dashboard.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM student")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tutor")
        total_tutors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM `session`")
        total_sessions = cursor.fetchone()[0]
        
        # Get pending verifications count
        cursor.execute("SELECT COUNT(*) FROM tutor WHERE verificationStatus = 'pending'")
        pending_tutors_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM verificationdocument WHERE approvalStatus = 'pending'")
        pending_docs_count = cursor.fetchone()[0]
        pending_verifications = pending_tutors_count + pending_docs_count
        
        # Calculate total earnings (example: $50 per completed session)
        cursor.execute("SELECT COUNT(*) FROM `session` WHERE status = 'completed'")
        completed_sessions = cursor.fetchone()[0]
        total_earnings = completed_sessions * 50
        
        # Get recent sessions
        cursor.execute("""
            SELECT s.sessionID, s.courseCode, s.scheduledDate, s.scheduledTime, s.status,
                   u1.fullName as studentName, u2.fullName as tutorName
            FROM `session` s
            JOIN user u1 ON s.studentID = u1.userID
            JOIN user u2 ON s.tutorID = u2.userID
            ORDER BY s.scheduledDate DESC, s.scheduledTime DESC
            LIMIT 20
        """)
        recent_sessions_raw = cursor.fetchall()
        
        recent_sessions = []
        for row in recent_sessions_raw:
            recent_sessions.append({
                'sessionID': row[0],
                'courseCode': row[1],
                'scheduledDate': row[2].strftime('%Y-%m-%d') if hasattr(row[2], 'strftime') else str(row[2]),
                'scheduledTime': str(row[3]) if row[3] else 'N/A',
                'status': row[4],
                'studentName': row[5],
                'tutorName': row[6]
            })
        
        cursor.close()
        
        return render_template('admin_dashboard_main.html', 
                             fullName=session.get('fullName'),
                             total_users=total_users,
                             total_students=total_students,
                             total_tutors=total_tutors,
                             total_sessions=total_sessions,
                             pending_verifications=pending_verifications,
                             total_earnings=total_earnings,
                             recent_sessions=recent_sessions)
                             
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        flash(f'Unable to load admin dashboard: {str(e)}', 'error')
        return redirect('/login')


@app.route('/admin/users')
def admin_users():
    """Admin manage users page"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        
        # Get all tutors with their details
        cursor.execute("""
            SELECT t.tutorID, u.fullName, u.email, t.verificationStatus, 
                   IFNULL(t.averageRating, 0) as averageRating, 
                   COUNT(DISTINCT tc.courseCode) as course_count,
                   COUNT(DISTINCT s.sessionID) as session_count
            FROM tutor t
            JOIN user u ON t.tutorID = u.userID
            LEFT JOIN tutorcourse tc ON t.tutorID = tc.tutorID
            LEFT JOIN `session` s ON t.tutorID = s.tutorID
            GROUP BY t.tutorID
            ORDER BY u.fullName
        """)
        all_tutors_raw = cursor.fetchall()
        
        all_tutors_list = []
        for row in all_tutors_raw:
            all_tutors_list.append({
                'tutorID': row[0],
                'fullName': row[1],
                'email': row[2],
                'verificationStatus': row[3],
                'averageRating': float(row[4]) if row[4] else 0.0,
                'course_count': row[5],
                'session_count': row[6]
            })
        
        # Get all students
        cursor.execute("""
            SELECT s.studentID, u.fullName, u.email, p.programName,
                   COUNT(DISTINCT s2.sessionID) as session_count
            FROM student s
            JOIN user u ON s.studentID = u.userID
            LEFT JOIN program p ON s.programID = p.programID
            LEFT JOIN `session` s2 ON s.studentID = s2.studentID
            GROUP BY s.studentID
            ORDER BY u.fullName
        """)
        all_students_raw = cursor.fetchall()
        
        all_students = []
        for row in all_students_raw:
            all_students.append({
                'studentID': row[0],
                'fullName': row[1],
                'email': row[2],
                'programName': row[3] if row[3] else 'Not assigned',
                'session_count': row[4]
            })
        
        cursor.close()
        
        return render_template('admin_users.html', 
                             fullName=session.get('fullName'),
                             all_tutors_list=all_tutors_list,
                             all_students=all_students)
                             
    except Exception as e:
        print(f"Error loading admin users: {e}")
        flash(f'Unable to load users: {str(e)}', 'error')
        return redirect('/admin')


@app.route('/admin/verification')
def admin_verification():
    """Admin tutor verification page"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        
        # Get pending tutor verifications
        cursor.execute("""
            SELECT t.tutorID, u.fullName, t.verificationStatus, 
                   COALESCE(v.uploadDate, 'N/A') as uploadDate,
                   (SELECT COUNT(*) FROM verificationdocument WHERE tutorID = t.tutorID) as doc_count
            FROM tutor t
            JOIN user u ON t.tutorID = u.userID
            LEFT JOIN verificationdocument v ON t.tutorID = v.tutorID AND v.approvalStatus = 'pending'
            WHERE t.verificationStatus = 'pending'
            GROUP BY t.tutorID
            ORDER BY v.uploadDate DESC
        """)
        pending_tutors_raw = cursor.fetchall()
        
        pending_tutors = []
        for row in pending_tutors_raw:
            pending_tutors.append({
                'tutorID': row[0],
                'fullName': row[1],
                'verificationStatus': row[2],
                'uploadDate': row[3].strftime('%Y-%m-%d') if hasattr(row[3], 'strftime') else str(row[3]),
                'doc_count': row[4]
            })
        
        # Get pending documents
        cursor.execute("""
            SELECT v.documentID, v.tutorID, v.filePath, v.documentType, v.uploadDate, 
                   u.fullName, t.verificationStatus
            FROM verificationdocument v
            JOIN tutor t ON v.tutorID = t.tutorID
            JOIN user u ON v.tutorID = u.userID
            WHERE v.approvalStatus = 'pending'
            ORDER BY v.uploadDate DESC
        """)
        pending_docs_raw = cursor.fetchall()
        
        pending_docs = []
        for row in pending_docs_raw:
            pending_docs.append({
                'documentID': row[0],
                'tutorID': row[1],
                'filePath': row[2],
                'documentType': row[3] or 'Document',
                'uploadDate': row[4].strftime('%Y-%m-%d %H:%M') if hasattr(row[4], 'strftime') else str(row[4]),
                'fullName': row[5],
                'verificationStatus': row[6]
            })
        
        cursor.close()
        
        return render_template('admin_verification.html', 
                             fullName=session.get('fullName'),
                             pending_tutors=pending_tutors,
                             pending_docs=pending_docs)
                             
    except Exception as e:
        print(f"Error loading admin verification: {e}")
        flash(f'Unable to load verification data: {str(e)}', 'error')
        return redirect('/admin')


@app.route('/admin/courses')
def admin_courses():
    """Admin course manager page"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        
        # Get all courses with tutor counts
        cursor.execute("""
            SELECT c.courseCode, c.courseName, s.schoolName, 
                   COUNT(DISTINCT tc.tutorID) as tutor_count
            FROM course c
            JOIN school s ON c.schoolID = s.schoolID
            LEFT JOIN tutorcourse tc ON c.courseCode = tc.courseCode
            GROUP BY c.courseCode, c.courseName, s.schoolName
            ORDER BY c.courseCode
        """)
        all_courses_raw = cursor.fetchall()
        
        all_courses = []
        for row in all_courses_raw:
            all_courses.append({
                'courseCode': row[0],
                'courseName': row[1],
                'schoolName': row[2],
                'tutor_count': row[3]
            })
        
        cursor.close()
        
        return render_template('admin_courses.html', 
                             fullName=session.get('fullName'),
                             all_courses=all_courses)
                             
    except Exception as e:
        print(f"Error loading admin courses: {e}")
        flash(f'Unable to load courses: {str(e)}', 'error')
        return redirect('/admin')


@app.route('/admin/profile')
def admin_profile():
    """Admin profile page"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        
        # Get admin details from database
        cursor.execute("""
            SELECT fullName, email FROM user WHERE userID = %s
        """, (session['userID'],))
        admin_info = cursor.fetchone()
        
        cursor.close()
        
        return render_template('admin_profile.html', 
                             fullName=admin_info[0] if admin_info else session.get('fullName'),
                             admin_email=admin_info[1] if admin_info else session.get('email', 'admin@zitconnect.com'))
                             
    except Exception as e:
        print(f"Error loading admin profile: {e}")
        return render_template('admin_profile.html', 
                             fullName=session.get('fullName'),
                             admin_email=session.get('email', 'admin@zitconnect.com'))

@app.route('/session/complete/<int:sessionID>', methods=['POST'])
def complete_session(sessionID):
    """Tutor marks a confirmed session as completed."""
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Only tutors can complete sessions.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        # Update session status to 'completed'
        cursor.execute(
            "UPDATE `session` SET status = 'completed' WHERE sessionID = %s AND tutorID = %s AND status = 'confirmed'",
            (sessionID, session['userID'])
        )
        if cursor.rowcount == 0:
            flash('Session not found or not confirmed.', 'error')
            return redirect('/tutor-dashboard')

        # Get student ID and course code for notification
        cursor.execute(
            "SELECT studentID, courseCode FROM `session` WHERE sessionID = %s",
            (sessionID,)
        )
        sess = cursor.fetchone()
        if sess:
            student_id = sess[0]
            course_code = sess[1]
            # Notify student that session is completed and they can rate
            cursor.execute(
                "INSERT INTO notification (userID, message) VALUES (%s, %s)",
                (student_id, f'Your session for {course_code} has been marked as completed. You can now rate the tutor.')
            )
        mysql.connection.commit()
        cursor.close()
        flash('Session marked as completed. Student can now rate.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error completing session: {str(e)}', 'error')

    return redirect('/tutor-dashboard')


@app.route('/admin/approve-tutor/<int:tutorID>', methods=['POST'])
def admin_approve_tutor(tutorID):
    """Approve a tutor's verification"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE tutor SET verificationStatus = 'approved' WHERE tutorID = %s", (tutorID,))
        mysql.connection.commit()
        cursor.close()
        flash('Tutor has been approved successfully.', 'success')
    except Exception as e:
        flash(f'Approval failed: {str(e)}', 'error')

    # Redirect back to the page that made the request
    referer = request.referrer
    if referer and '/admin/verification' in referer:
        return redirect('/admin/verification')
    return redirect('/admin')


@app.route('/admin/reject-tutor/<int:tutorID>', methods=['POST'])
def admin_reject_tutor(tutorID):
    """Reject a tutor's verification"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE tutor SET verificationStatus = 'rejected' WHERE tutorID = %s", (tutorID,))
        mysql.connection.commit()
        cursor.close()
        flash('Tutor has been rejected.', 'success')
    except Exception as e:
        flash(f'Rejection failed: {str(e)}', 'error')

    referer = request.referrer
    if referer and '/admin/verification' in referer:
        return redirect('/admin/verification')
    return redirect('/admin')


@app.route('/admin/approve-doc/<int:documentID>', methods=['POST'])
def admin_approve_doc(documentID):
    """Approve a verification document"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        
        # Get the tutorID from the document
        cursor.execute("SELECT tutorID FROM verificationdocument WHERE documentID = %s", (documentID,))
        result = cursor.fetchone()
        
        if result:
            tutorID = result[0]
            # Update document status
            cursor.execute("UPDATE verificationdocument SET approvalStatus = 'approved' WHERE documentID = %s", (documentID,))
            
            # Check if tutor has any approved documents
            cursor.execute("""
                SELECT COUNT(*) FROM verificationdocument 
                WHERE tutorID = %s AND approvalStatus = 'approved'
            """, (tutorID,))
            approved_count = cursor.fetchone()[0]
            
            # Check if tutor has added courses
            cursor.execute("""
                SELECT COUNT(*) FROM tutorcourse WHERE tutorID = %s
            """, (tutorID,))
            course_count = cursor.fetchone()[0]
            
            # If tutor has approved documents AND courses, update tutor status to approved
            if approved_count >= 1 and course_count >= 1:
                cursor.execute("UPDATE tutor SET verificationStatus = 'approved' WHERE tutorID = %s", (tutorID,))
                flash('Document approved and tutor is now fully verified!', 'success')
            elif approved_count >= 1:
                # If they have documents but no courses yet, keep pending
                flash('Document approved. Tutor needs to add courses before full verification.', 'warning')
            
            mysql.connection.commit()
        else:
            flash('Document not found.', 'error')
            
        cursor.close()
    except Exception as e:
        flash(f'Approval failed: {str(e)}', 'error')

    referer = request.referrer
    if referer and '/admin/verification' in referer:
        return redirect('/admin/verification')
    return redirect('/admin')


@app.route('/admin/reject-doc/<int:documentID>', methods=['POST'])
def admin_reject_doc(documentID):
    """Reject a verification document"""
    if 'userID' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE verificationdocument SET approvalStatus = 'rejected' WHERE documentID = %s", (documentID,))
        mysql.connection.commit()
        cursor.close()
        flash('Document rejected.', 'success')
    except Exception as e:
        flash(f'Rejection failed: {str(e)}', 'error')

    referer = request.referrer
    if referer and '/admin/verification' in referer:
        return redirect('/admin/verification')
    return redirect('/admin')


@app.route('/admin/tutor-details/<int:tutorID>')
def admin_tutor_details(tutorID):
    """Get tutor details for modal view"""
    if 'userID' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor()
        
        # Get tutor basic info
        cursor.execute("""
            SELECT u.fullName, u.userName, u.email, t.verificationStatus, 
                   IFNULL(t.averageRating, 0), IFNULL(t.bio, '')
            FROM user u
            JOIN tutor t ON u.userID = t.tutorID
            WHERE t.tutorID = %s
        """, (tutorID,))
        tutor = cursor.fetchone()
        
        if not tutor:
            return jsonify({'error': 'Tutor not found'}), 404
        
        # Get tutor courses
        cursor.execute("""
            SELECT c.courseCode, c.courseName
            FROM tutorcourse tc
            JOIN course c ON tc.courseCode = c.courseCode
            WHERE tc.tutorID = %s
        """, (tutorID,))
        courses = cursor.fetchall()
        
        # Get tutor documents
        cursor.execute("""
            SELECT documentID, filePath, documentType, approvalStatus, uploadDate
            FROM verificationdocument
            WHERE tutorID = %s
        """, (tutorID,))
        documents = cursor.fetchall()
        
        cursor.close()
        
        return jsonify({
            'fullName': tutor[0],
            'userName': tutor[1],
            'email': tutor[2],
            'verificationStatus': tutor[3],
            'averageRating': float(tutor[4]) if tutor[4] else 0.0,
            'bio': tutor[5] if tutor[5] else 'No bio provided',
            'courses': [{'courseCode': c[0], 'courseName': c[1]} for c in courses],
            'documents': [{'documentID': d[0], 'filePath': d[1], 'documentType': d[2] or 'Document', 'approvalStatus': d[3]} for d in documents]
        })
    except Exception as e:
        print(f"Error in admin_tutor_details: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/availability', methods=['GET'])
def availability_page():
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login as a tutor.', 'error')
        return redirect('/login')

    tutor_id = session['userID']
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT dayOfWeek, timeSlot FROM availability WHERE tutorID = %s",
        (tutor_id,)
    )
    slots = cursor.fetchall()
    cursor.close()

    # Build a dict for easy frontend pre-selection
    selected = {}
    for day, time in slots:
        if day not in selected:
            selected[day] = []
        selected[day].append(time)

    return render_template('availability.html',
                           fullName=session.get('fullName'),
                           selected=selected)

@app.route('/book-session', methods=['GET', 'POST'])
def book_session():
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student to book a session.', 'error')
        return redirect('/login')

    # --- POST: Handle individual booking (unchanged) ---
    if request.method == 'POST':
        tutor_id = request.form.get('tutorID')
        course_code = request.form.get('courseCode', '').strip()
        scheduled_date = request.form.get('scheduledDate')
        scheduled_time = request.form.get('timeSlot')
        session_type = request.form.get('sessionType', 'individual')

        if not tutor_id or not course_code or not scheduled_date or not scheduled_time:
            flash('Please complete all booking fields.', 'error')
            return redirect('/book-session')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO `session` (studentID, tutorID, courseCode, sessionType, scheduledDate, scheduledTime, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'pending')",
                (session['userID'], tutor_id, course_code, session_type, scheduled_date, scheduled_time)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Session request submitted successfully.', 'success')
            return redirect('/student-dashboard')
        except Exception as e:
            flash(f'Booking failed: {str(e)}', 'error')
            return redirect('/book-session')

    # --- GET: Show booking form ---
    tutor_id = request.args.get('tutorID', type=int)
    if not tutor_id:
        flash('Please select a tutor first.', 'error')
        return redirect('/student-dashboard')

    cursor = mysql.connection.cursor()

    # 1. Get tutor details (name)
    cursor.execute("SELECT fullName FROM user WHERE userID = %s", (tutor_id,))
    tutor = cursor.fetchone()
    if not tutor:
        flash('Tutor not found.', 'error')
        return redirect('/student-dashboard')
    tutor_name = tutor[0]

    # 2. Get courses this tutor teaches
    cursor.execute("""
        SELECT c.courseCode, c.courseName
        FROM tutorcourse tc
        JOIN course c ON tc.courseCode = c.courseCode
        WHERE tc.tutorID = %s
    """, (tutor_id,))
    courses = cursor.fetchall()

    # 3. Get available group sessions for this tutor
    cursor.execute("""
        SELECT s.sessionID, s.courseCode, c.courseName,
               s.scheduledDate, s.scheduledTime,
               g.maxCapacity, g.enrolledCount, g.pricePerStudent,
               g.meetingPlatform, g.accessLink
        FROM session s
        JOIN groupsession g ON s.sessionID = g.groupSessionID
        JOIN course c ON s.courseCode = c.courseCode
        WHERE s.tutorID = %s
          AND g.enrolledCount < g.maxCapacity
          AND s.scheduledDate >= CURDATE()
          AND s.status = 'pending'
        ORDER BY s.scheduledDate ASC, s.scheduledTime ASC
    """, (tutor_id,))
    group_sessions_raw = cursor.fetchall()
    cursor.close()

    # Format group sessions into a list of dictionaries
    group_sessions = []
    for gs in group_sessions_raw:
        # gs[3] = scheduledDate, gs[4] = scheduledTime
        formatted_date = gs[3].strftime('%Y-%m-%d') if gs[3] and hasattr(gs[3], 'strftime') else str(gs[3]) if gs[3] else ''
        formatted_time = gs[4].strftime('%H:%M') if gs[4] and hasattr(gs[4], 'strftime') else str(gs[4]) if gs[4] else ''
        group_sessions.append({
            'sessionID': gs[0],
            'courseCode': gs[1],
            'courseName': gs[2],
            'scheduledDate': formatted_date,
            'scheduledTime': formatted_time,
            'maxCapacity': gs[5],
            'enrolledCount': gs[6],
            'pricePerStudent': float(gs[7]) if gs[7] else 0.0,
            'meetingPlatform': gs[8],
            'accessLink': gs[9]
        })

    return render_template('book_session.html',
                           fullName=session.get('fullName'),
                           tutor_id=tutor_id,
                           tutor_name=tutor_name,
                           courses=courses,
                           group_sessions=group_sessions)


@app.route('/set-availability', methods=['POST'])
def set_availability():
    if 'userID' not in session or session.get('role') != 'tutor':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data or 'slots' not in data:
        return jsonify({'error': 'Missing slots data'}), 400

    tutor_id = session['userID']
    slots = data['slots']   # expected: list of {"day": "Monday", "time": "09:00-10:00"}

    try:
        cursor = mysql.connection.cursor()
        # Delete existing slots for this tutor
        cursor.execute("DELETE FROM availability WHERE tutorID = %s", (tutor_id,))
        # Insert new slots
        for slot in slots:
            day = slot.get('day')
            time_slot = slot.get('time')
            if day and time_slot:
                cursor.execute(
                    "INSERT INTO availability (tutorID, dayOfWeek, timeSlot) VALUES (%s, %s, %s)",
                    (tutor_id, day, time_slot)
                )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Availability updated'})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    

@app.route('/create-group-session', methods=['GET', 'POST'])
def create_group_session():
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login as a tutor.', 'error')
        return redirect('/login')

    # Check if tutor is approved
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT verificationStatus FROM tutor WHERE tutorID = %s", (session['userID'],))
    status = cursor.fetchone()
    cursor.close()
    if not status or status[0] != 'approved':
        flash('Your account must be approved to create group sessions.', 'error')
        return redirect('/tutor-dashboard')

    if request.method == 'POST':
        course_code = request.form.get('courseCode', '').strip()
        scheduled_date = request.form.get('scheduledDate')
        scheduled_time = request.form.get('scheduledTime')
        max_capacity = request.form.get('maxCapacity', type=int)
        price = request.form.get('pricePerStudent', type=float)
        meeting_platform = request.form.get('meetingPlatform', '').strip()
        access_link = request.form.get('accessLink', '').strip()

        # Validate required fields
        if not all([course_code, scheduled_date, scheduled_time, max_capacity, price]):
            flash('All fields are required.', 'error')
            return redirect('/my-sessions?tab=create-group')

        try:
            cursor = mysql.connection.cursor()
            # Insert into session table (studentID is NULL for group sessions)
            cursor.execute(
                """INSERT INTO `session` 
                   (studentID, tutorID, courseCode, sessionType, scheduledDate, scheduledTime, status)
                   VALUES (%s, %s, %s, 'group', %s, %s, 'pending')""",
                (None, session['userID'], course_code, scheduled_date, scheduled_time)
            )
            session_id = cursor.lastrowid

            # Insert into groupsession
            cursor.execute(
                """INSERT INTO groupsession 
                   (groupSessionID, maxCapacity, enrolledCount, pricePerStudent, meetingPlatform, accessLink, accessLinkUnlocked)
                   VALUES (%s, %s, 0, %s, %s, %s, 0)""",
                (session_id, max_capacity, price, meeting_platform, access_link)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Group session created successfully!', 'success')
            return redirect('/my-sessions?tab=my-groups')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating session: {str(e)}', 'error')
            return redirect('/my-sessions?tab=create-group')

    # GET request – redirect to the My Sessions page with the create-group tab active
    return redirect('/my-sessions?tab=create-group')

@app.route('/group-sessions')
def group_sessions():
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        # Select group sessions that are not full and scheduled in the future
        cursor.execute("""
            SELECT s.sessionID, s.courseCode, c.courseName, s.scheduledDate, s.scheduledTime,
                   u.fullName AS tutorName, g.maxCapacity, g.enrolledCount, g.pricePerStudent,
                   g.meetingPlatform, g.accessLink, g.accessLinkUnlocked
            FROM session s
            JOIN groupsession g ON s.sessionID = g.groupSessionID
            JOIN tutor t ON s.tutorID = t.tutorID
            JOIN user u ON t.tutorID = u.userID
            JOIN course c ON s.courseCode = c.courseCode
            WHERE g.enrolledCount < g.maxCapacity
              AND s.scheduledDate >= CURDATE()
              AND s.status = 'pending'   -- group sessions are pending until payment?
              -- Actually status might be 'confirmed' once tutor creates it? We'll treat as 'pending' initially.
              -- For group sessions, we can consider them 'available' if not full.
            ORDER BY s.scheduledDate ASC, s.scheduledTime ASC
        """)
        rows = cursor.fetchall()
        cursor.close()

        sessions = []
        for row in rows:
            sessions.append({
                'sessionID': row[0],
                'courseCode': row[1],
                'courseName': row[2],
                'scheduledDate': row[3].strftime('%Y-%m-%d') if row[3] else '',
                'scheduledTime': str(row[4]) if row[4] else '',
                'tutorName': row[5],
                'maxCapacity': row[6],
                'enrolledCount': row[7],
                'pricePerStudent': float(row[8]) if row[8] else 0.0,
                'meetingPlatform': row[9],
                'accessLink': row[10],
                'accessLinkUnlocked': row[11]
            })
        return render_template('group_sessions.html', sessions=sessions)
    except Exception as e:
        flash(f'Error loading group sessions: {str(e)}', 'error')
        return redirect('/student-dashboard')
    
@app.route('/join-session/<int:groupSessionID>', methods=['POST'])
def join_session(groupSessionID):
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student.', 'error')
        return redirect('/login')

    student_id = session['userID']

    try:
        cursor = mysql.connection.cursor()
        # Check if session exists and not full
        cursor.execute(
            "SELECT maxCapacity, enrolledCount, pricePerStudent FROM groupsession WHERE groupSessionID = %s",
            (groupSessionID,)
        )
        group = cursor.fetchone()
        if not group:
            flash('Group session not found.', 'error')
            return redirect('/group-sessions')

        max_cap, enrolled, price = group
        if enrolled >= max_cap:
            flash('This session is fully booked.', 'error')
            return redirect('/group-sessions')

        # Check if student already has a pending or successful payment for this session
        cursor.execute(
            "SELECT paymentID FROM payment WHERE groupSessionID = %s AND studentID = %s AND paymentStatus IN ('pending','successful')",
            (groupSessionID, student_id)
        )
        existing = cursor.fetchone()
        if existing:
            flash('You have already joined this session or have a pending payment.', 'error')
            return redirect('/group-sessions')

        # Create a pending payment record
        cursor.execute(
            "INSERT INTO payment (groupSessionID, studentID, amount, paymentStatus) VALUES (%s, %s, %s, 'pending')",
            (groupSessionID, student_id, price)
        )
        payment_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()

        print(f"Payment created with ID: {payment_id}")  # Debug

        # Redirect to payment page
        return redirect(f'/payment/{payment_id}')

    except Exception as e:
        mysql.connection.rollback()
        print(f" Error in join_session: {e}")  # Debug
        flash(f'Error joining session: {str(e)}', 'error')
        return redirect('/group-sessions')
    
@app.route('/payment/<int:paymentID>', methods=['GET', 'POST'])
def payment_page(paymentID):
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login.', 'error')
        return redirect('/login')

    cursor = mysql.connection.cursor()
    # Single-line string to avoid stray % characters
    cursor.execute("""
        SELECT p.paymentID, p.amount, p.paymentStatus, p.transactionID,
               s.sessionID, s.courseCode, c.courseName, s.scheduledDate, s.scheduledTime,
               u.fullName AS tutorName, g.meetingPlatform, g.accessLink,
               g.groupSessionID, g.pricePerStudent, g.accessLinkUnlocked
        FROM payment p
        JOIN groupsession g ON p.groupSessionID = g.groupSessionID
        JOIN session s ON g.groupSessionID = s.sessionID
        JOIN course c ON s.courseCode = c.courseCode
        JOIN tutor t ON s.tutorID = t.tutorID
        JOIN user u ON t.tutorID = u.userID
        WHERE p.paymentID = %s AND p.studentID = %s
    """, (paymentID, session['userID']))
    row = cursor.fetchone()
    cursor.close()

    if not row:
        flash('Payment record not found.', 'error')
        return redirect('/student-dashboard')
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print("STATUS CODE:", response.status_code)
    print("RAW RESPONSE:", repr(response.text))
    result = response.json()

    payment = {
        'paymentID': row[0],
        'amount': row[1],
        'paymentStatus': row[2],
        'transactionID': row[3],
        'sessionID': row[4],
        'courseCode': row[5],
        'courseName': row[6],
        'scheduledDate': row[7],
        'scheduledTime': row[8],
        'tutorName': row[9],
        'meetingPlatform': row[10],
        'accessLink': row[11],
        'groupSessionID': row[12],
        'pricePerStudent': row[13],
        'accessLinkUnlocked': row[14]
    }

    # If already successful, show the link directly
    if payment['paymentStatus'] == 'successful':
        return render_template('group_payment.html', payment=payment, payment_success=True)

    if request.method == 'POST':
        # --- SIMULATION MODE (bypass Lenco) ---
        if SIMULATE_PAYMENT:
            try:
                cursor = mysql.connection.cursor()
                # Mark payment successful
                cursor.execute(
                    "UPDATE payment SET paymentStatus = 'successful', transactionID = %s WHERE paymentID = %s",
                    (f"SIM-{uuid.uuid4().hex[:8].upper()}", paymentID)
                )
                # Unlock session and increment enrollment
                cursor.execute("""
                    UPDATE groupsession 
                    SET enrolledCount = enrolledCount + 1, accessLinkUnlocked = 1 
                    WHERE groupSessionID = %s
                """, (payment['groupSessionID'],))
                mysql.connection.commit()
                cursor.close()

                flash('Payment successful! You can now join the session.', 'success')
                return render_template('group_payment.html', payment=payment, payment_success=True)
            except Exception as e:
                flash(f'Simulation error: {str(e)}', 'error')
                return render_template('group_payment.html', payment=payment)

        if request.method == 'POST':
    # --- REAL PAYMENT (SIMULATE_PAYMENT is False) ---
            phone_number = request.form.get('phone_number', '').strip()
            operator = request.form.get('operator', '').strip()

    if not phone_number or not operator:
        flash('Please enter your mobile money number and select your network.', 'error')
        return render_template('group_payment.html', payment=payment)

    if not re.match(r'^(09|07)\d{8}$', phone_number):
        flash('Please enter a valid Zambian mobile number (e.g., 0977123456).', 'error')
        return render_template('group_payment.html', payment=payment)

    try:
        reference = f"ZIT-{uuid.uuid4().hex[:8].upper()}"
        url = f"{LENCO_BASE_URL}collections/mobile-money"

        # Headers – only what's required
        headers = {
            'Authorization': f'Bearer {LENCO_SECRET_KEY}',
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        payload = {
            "reference": reference,
            "amount": float(payment['amount']),
            "currency": "ZMW",
            "operator": operator,          # 'airtel', 'mtn', or 'zamtel'
            "phone": phone_number,
            "country": "zm",
            "bearer": "customer"
        }

        # --- Debug output ---
        print("\n🔍 Sending to Lenco:")
        print(f"   URL: {url}")
        print(f"   Headers: {headers}")
        print(f"   Payload: {payload}")

        # Send request
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        # --- Debug the raw response ---
        print(f"\n📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {response.headers}")
        print(f"📡 Raw response (first 1000 chars):\n{response.text[:1000]}")

        # Try to parse JSON
        try:
            result = response.json()
        except json.JSONDecodeError:
            # Not JSON – show the raw error
            flash('Payment service returned an invalid response. Please try again later.', 'error')
            print("❌ Response was NOT JSON.")
            return render_template('group_payment.html', payment=payment)

        # Process JSON response
        if response.status_code == 200 and result.get('status'):
            data = result.get('data', {})
            if data.get('status') in ['pending', 'pay-offline']:
                # Payment initiated – save reference
                cursor = mysql.connection.cursor()
                cursor.execute(
                    "UPDATE payment SET transactionID = %s, paymentStatus = 'pending' WHERE paymentID = %s",
                    (reference, paymentID)
                )
                mysql.connection.commit()
                cursor.close()

                flash('Payment request sent to your phone. Please confirm on your mobile money app.', 'success')
                return render_template('group_payment.html', payment=payment, payment_initiated=True)
            else:
                flash(f'Payment status: {data.get("status")}. Please try again.', 'error')
        else:
            # API returned error
            error_msg = result.get('message', result.get('error', 'Unknown error from payment service'))
            flash(f'Payment failed: {error_msg}', 'error')
            print(f"❌ Lenco error: {error_msg}")

    except requests.exceptions.Timeout:
        flash('Payment request timed out. Please try again.', 'error')
    except requests.exceptions.ConnectionError as e:
        flash('Cannot connect to payment service. Please check your internet connection.', 'error')
        print(f"❌ Connection error: {e}")
    except Exception as e:
        flash(f'Payment processing error: {str(e)}', 'error')
        print(f"❌ Unexpected error: {e}")

    return render_template('group_payment.html', payment=payment)

@app.route('/webhook/lenco', methods=['POST'])
def lenco_webhook():
    """
    Receive real-time payment status updates from Lenco.
    Expected JSON payload includes: reference, status, amount, etc.
    """
    try:
        # Get raw JSON payload
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid payload'}), 400

        print(f" Webhook received: {data}")

        # Extract fields (adjust names based on Lenco's actual payload)
        reference = data.get('reference')
        status = data.get('status')
        # Sometimes status is nested: data.data.status
        if not status and 'data' in data:
            status = data['data'].get('status')

        if not reference or not status:
            print("Missing reference or status")
            return jsonify({'error': 'Missing fields'}), 400

        # ✅ Only process successful payments
        if status.lower() == 'successful':
            cursor = mysql.connection.cursor()
            # Find payment by transactionID (which stores the reference)
            cursor.execute(
                "SELECT paymentID, groupSessionID, studentID FROM payment WHERE transactionID = %s AND paymentStatus != 'successful'",
                (reference,)
            )
            payment = cursor.fetchone()

            if payment:
                payment_id = payment[0]
                group_session_id = payment[1]
                student_id = payment[2]

                # Update payment status
                cursor.execute(
                    "UPDATE payment SET paymentStatus = 'successful' WHERE paymentID = %s",
                    (payment_id,)
                )
                # Increment enrolled count and unlock access link
                cursor.execute("""
                    UPDATE groupsession 
                    SET enrolledCount = enrolledCount + 1, accessLinkUnlocked = 1 
                    WHERE groupSessionID = %s
                """, (group_session_id,))

                # Create notification for student
                cursor.execute(
                    "INSERT INTO notification (userID, message) VALUES (%s, %s)",
                    (student_id, 'Your payment was successful! You can now join the session.')
                )

                mysql.connection.commit()
                cursor.close()

                print(f" Webhook processed: Payment {payment_id} marked successful")
                return jsonify({'status': 'ok'}), 200
            else:
                print(f" Payment not found for reference: {reference}")
                return jsonify({'error': 'Payment not found'}), 404
        else:
            # Optional: handle failed or pending status if needed
            print(f"ℹ Ignoring status: {status}")
            return jsonify({'status': 'ignored'}), 200

    except Exception as e:
        print(f" Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/payment/verify/<int:paymentID>', methods=['GET'])
def verify_payment(paymentID):
    if 'userID' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT transactionID, paymentStatus FROM payment WHERE paymentID = %s AND studentID = %s",
        (paymentID, session['userID'])
    )
    payment = cursor.fetchone()
    cursor.close()

    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    transaction_id, status = payment[0], payment[1]

    if status == 'successful':
        return jsonify({'status': 'successful'})

    if not transaction_id:
        return jsonify({'status': 'pending'})

    try:
        # ✅ Correct endpoint
        url = f"{LENCO_BASE_URL}collections/status/{transaction_id}"
        headers = {
            'Authorization': f'Bearer {LENCO_SECRET_KEY}',
            'accept': 'application/json'
            # x-signature is NOT needed for outgoing API calls – drop it
        }
        response = requests.get(url, headers=headers, timeout=15)
        result = response.json()

        if result.get('status') and result.get('data', {}).get('status') == 'successful':
            # Update DB and unlock
            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE payment SET paymentStatus = 'successful' WHERE paymentID = %s",
                (paymentID,)
            )
            cursor.execute("""
                UPDATE groupsession g
                JOIN payment p ON p.groupSessionID = g.groupSessionID
                SET g.enrolledCount = g.enrolledCount + 1,
                    g.accessLinkUnlocked = 1
                WHERE p.paymentID = %s
            """, (paymentID,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'successful'})
        elif result.get('data', {}).get('status') == 'failed':
            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE payment SET paymentStatus = 'failed' WHERE paymentID = %s",
                (paymentID,)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'failed'})
        else:
            return jsonify({'status': 'pending'})
    except Exception as e:
        print(f"Verify error: {e}")
        return jsonify({'status': 'pending', 'error': str(e)})


@app.route('/rate-session/<int:sessionID>', methods=['GET', 'POST'])
def rate_session(sessionID):
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login as a student.', 'error')
        return redirect('/login')

    # Check if session exists, is completed, and belongs to this student
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT s.sessionID, s.tutorID, s.courseCode, u.fullName AS tutorName FROM session s "
        "JOIN tutor t ON s.tutorID = t.tutorID JOIN user u ON t.tutorID = u.userID "
        "WHERE s.sessionID = %s AND s.studentID = %s AND s.status = 'completed'",
        (sessionID, session['userID'])
    )
    session_data = cursor.fetchone()
    if not session_data:
        flash('Session not found or not completed.', 'error')
        return redirect('/student-dashboard')

    if request.method == 'POST':
        stars = request.form.get('stars', type=int)
        comment = request.form.get('feedback', '').strip()

        if not stars or stars < 1 or stars > 5:
            flash('Please provide a rating between 1 and 5 stars.', 'error')
            return render_template('rate_session.html', session=session_data)

        try:
            cursor.execute(
                "INSERT INTO rating (sessionID, studentID, tutorID, stars, feedbackComment) VALUES (%s, %s, %s, %s, %s)",
                (sessionID, session['userID'], session_data[1], stars, comment)
            )
            # Recalculate tutor average rating
            cursor.execute(
                "UPDATE tutor SET averageRating = (SELECT AVG(stars) FROM rating WHERE tutorID = %s) WHERE tutorID = %s",
                (session_data[1], session_data[1])
            )
            mysql.connection.commit()
            cursor.close()
            flash('Thank you for your rating!', 'success')
            return redirect('/student-dashboard')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error saving rating: {str(e)}', 'error')
            return render_template('rate_session.html', session=session_data)

    # GET - show rating form
    return render_template('rate_session.html', session=session_data)

@app.route('/wallet')
def wallet():
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login as a tutor.', 'error')
        return redirect('/login')

    tutor_id = session['userID']
    cursor = mysql.connection.cursor()
    
    # Get wallet balance
    cursor.execute(
        "SELECT availableBalance, totalWithdrawn FROM wallet WHERE tutorID = %s",
        (tutor_id,)
    )
    wallet = cursor.fetchone()
    if not wallet:
        cursor.execute(
            "INSERT INTO wallet (tutorID, availableBalance, totalWithdrawn) VALUES (%s, 0, 0)",
            (tutor_id,)
        )
        mysql.connection.commit()
        available = 0
        total_withdrawn = 0
    else:
        available = float(wallet[0])
        total_withdrawn = float(wallet[1])

    # Get recent earnings (10% platform commission deducted)
    cursor.execute("""
        SELECT p.paymentDate, s.courseCode, p.amount, 
               (p.amount * 0.9) AS tutor_earnings
        FROM payment p
        JOIN groupsession g ON p.groupSessionID = g.groupSessionID
        JOIN session s ON g.groupSessionID = s.sessionID
        WHERE s.tutorID = %s AND p.paymentStatus = 'successful'
        ORDER BY p.paymentDate DESC
        LIMIT 20
    """, (tutor_id,))
    transactions = cursor.fetchall()
    cursor.close()

    transaction_list = []
    for t in transactions:
        transaction_list.append({
            'date': t[0].strftime('%Y-%m-%d %H:%M') if t[0] else '',
            'course': t[1],
            'amount': float(t[2]),
            'earned': float(t[3])
        })

    return render_template('wallet.html', 
                           availableBalance=available,
                           totalWithdrawn=total_withdrawn,
                           transactions=transaction_list)

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'userID' not in session or session.get('role') != 'tutor':
        return jsonify({'error': 'Unauthorized'}), 401

    amount = request.form.get('amount', type=float)
    if not amount or amount <= 0:
        flash('Invalid amount.', 'error')
        return redirect('/wallet')

    tutor_id = session['userID']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT availableBalance FROM wallet WHERE tutorID = %s", (tutor_id,))
    row = cursor.fetchone()
    if not row or float(row[0]) < amount:
        flash('Insufficient balance.', 'error')
        return redirect('/wallet')

    try:
        # Simulate payout request to Lenco
        # In production, call Lenco API to initiate payout
        # Assume success
        new_balance = float(row[0]) - amount
        cursor.execute(
            "UPDATE wallet SET availableBalance = %s, totalWithdrawn = totalWithdrawn + %s WHERE tutorID = %s",
            (new_balance, amount, tutor_id)
        )
        # Create notification for tutor
        cursor.execute(
            "INSERT INTO notification (userID, message) VALUES (%s, %s)",
            (tutor_id, f'Your withdrawal of K{amount:.2f} has been processed.')
        )
        mysql.connection.commit()
        cursor.close()
        flash('Withdrawal successful!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Withdrawal failed: {str(e)}', 'error')
    return redirect('/wallet')

@app.route('/notifications')
def notifications():
    if 'userID' not in session:
        flash('Please login.', 'error')
        return redirect('/login')
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT notificationID, message, isRead, createdAt FROM notification WHERE userID = %s ORDER BY createdAt DESC",
        (session['userID'],)
    )
    rows = cursor.fetchall()
    cursor.close()
    notifs = []
    for row in rows:
        notifs.append({
            'id': row[0],
            'message': row[1],
            'isRead': bool(row[2]),
            'createdAt': row[3].strftime('%Y-%m-%d %H:%M') if row[3] else ''
        })
    return render_template('notifications.html', notifications=notifs)

@app.route('/notifications/mark-read/<int:notificationID>', methods=['POST'])
def mark_notification_read(notificationID):
    if 'userID' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE notification SET isRead = 1 WHERE notificationID = %s AND userID = %s",
        (notificationID, session['userID'])
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({'success': True})

@app.route('/session/accept/<int:sessionID>', methods=['POST'])
def accept_session(sessionID):
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Only tutors can accept sessions.', 'error')
        return redirect('/login')
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE `session` SET status = 'confirmed' WHERE sessionID = %s AND tutorID = %s",
            (sessionID, session['userID'])
        )
        # Get student ID and course code
        cursor.execute(
            "SELECT studentID, courseCode FROM `session` WHERE sessionID = %s",
            (sessionID,)
        )
        sess = cursor.fetchone()
        if sess:
            student_id = sess[0]
            course_code = sess[1]
            # Notify student
            cursor.execute(
                "INSERT INTO notification (userID, message) VALUES (%s, %s)",
                (student_id, f'Your session request for {course_code} has been accepted.')
            )
        mysql.connection.commit()
        cursor.close()
        flash('Session request accepted.', 'success')
    except Exception as e:
        flash(f'Error accepting session: {str(e)}', 'error')
    
    return redirect('/tutor-dashboard')

@app.route('/api/availability/<int:tutorID>')
def api_availability(tutorID):
    """
    Return available time slots for a tutor on a specific date.
    Query params: date (YYYY-MM-DD)
    """
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date required'}), 400

    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = dt.strftime('%A')  # Monday, Tuesday, etc.
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT timeSlot FROM availability WHERE tutorID = %s AND dayOfWeek = %s ORDER BY timeSlot",
        (tutorID, day_of_week)
    )
    slots = [row[0] for row in cursor.fetchall()]
    cursor.close()

    return jsonify({'slots': slots})

@app.route('/api/unread-count')
def unread_count():
    if 'userID' not in session:
        return jsonify({'count': 0})
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM notification WHERE userID = %s AND isRead = 0",
        (session['userID'],)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    return jsonify({'count': count})

@app.route('/session/decline/<int:sessionID>', methods=['POST'])
def decline_session(sessionID):
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Only tutors can decline sessions.', 'error')
        return redirect('/login')
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE `session` SET status = 'declined' WHERE sessionID = %s AND tutorID = %s AND status = 'pending'",
            (sessionID, session['userID'])
        )
        # Get student ID and course code
        cursor.execute(
            "SELECT studentID, courseCode FROM `session` WHERE sessionID = %s",
            (sessionID,)
        )
        sess = cursor.fetchone()
        if sess:
            student_id = sess[0]
            course_code = sess[1]
            cursor.execute(
                "INSERT INTO notification (userID, message) VALUES (%s, %s)",
                (student_id, f'Your session request for {course_code} has been declined.')
            )
        mysql.connection.commit()
        cursor.close()
        flash('Session request declined.', 'success')
    except Exception as e:
        flash(f'Error declining session: {str(e)}', 'error')
    
    return redirect('/tutor-dashboard')

@app.route('/my-sessions')
def my_sessions():
    """Tutor's dedicated page to view all sessions and manage group sessions."""
    if 'userID' not in session or session.get('role') != 'tutor':
        flash('Please login as a tutor.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()

        # --- 1. All sessions (individual + group) for this tutor ---
        cursor.execute("""
            SELECT s.sessionID, s.courseCode, s.scheduledDate, s.scheduledTime,
                   s.sessionType, s.status, u.fullName as studentName,
                   s.studentID
            FROM `session` s
            JOIN user u ON s.studentID = u.userID
            WHERE s.tutorID = %s
            ORDER BY
                CASE s.status
                    WHEN 'pending' THEN 1
                    WHEN 'confirmed' THEN 2
                    WHEN 'completed' THEN 3
                    WHEN 'cancelled' THEN 4
                    WHEN 'declined' THEN 5
                    ELSE 6
                END,
                s.scheduledDate ASC, s.scheduledTime ASC
        """, (session['userID'],))
        rows = cursor.fetchall()

        all_sessions = []
        for row in rows:
            scheduled_date = row[2]
            formatted_date = scheduled_date.strftime('%Y-%m-%d') if scheduled_date and hasattr(scheduled_date, 'strftime') else str(scheduled_date) if scheduled_date else 'N/A'
            scheduled_time = row[3]
            formatted_time = scheduled_time.strftime('%H:%M') if scheduled_time and hasattr(scheduled_time, 'strftime') else str(scheduled_time) if scheduled_time else 'N/A'
            all_sessions.append({
                'sessionID': row[0],
                'courseCode': row[1],
                'scheduledDate': formatted_date,
                'scheduledTime': formatted_time,
                'sessionType': row[4] if row[4] else 'individual',
                'status': row[5] if row[5] else 'pending',
                'studentName': row[6] if row[6] else 'Unknown Student',
                'studentID': row[7]
            })

        # --- 2. Group sessions created by this tutor ---
        cursor.execute("""
            SELECT s.sessionID, s.courseCode, c.courseName,
                   s.scheduledDate, s.scheduledTime,
                   g.maxCapacity, g.enrolledCount, g.pricePerStudent,
                   g.meetingPlatform, g.accessLink, g.accessLinkUnlocked
            FROM session s
            JOIN groupsession g ON s.sessionID = g.groupSessionID
            JOIN course c ON s.courseCode = c.courseCode
            WHERE s.tutorID = %s
            ORDER BY s.scheduledDate DESC, s.scheduledTime DESC
        """, (session['userID'],))
        group_rows = cursor.fetchall()
        cursor.close()

        my_group_sessions = []
        for row in group_rows:
            scheduled_date = row[3]
            formatted_date = scheduled_date.strftime('%Y-%m-%d') if scheduled_date and hasattr(scheduled_date, 'strftime') else str(scheduled_date) if scheduled_date else 'N/A'
            scheduled_time = row[4]
            formatted_time = scheduled_time.strftime('%H:%M') if scheduled_time and hasattr(scheduled_time, 'strftime') else str(scheduled_time) if scheduled_time else 'N/A'
            my_group_sessions.append({
                'sessionID': row[0],
                'courseCode': row[1],
                'courseName': row[2],
                'scheduledDate': formatted_date,
                'scheduledTime': formatted_time,
                'maxCapacity': row[5],
                'enrolledCount': row[6],
                'pricePerStudent': float(row[7]) if row[7] else 0.0,
                'meetingPlatform': row[8],
                'accessLink': row[9],
                'accessLinkUnlocked': bool(row[10])
            })

        # --- 3. Courses the tutor teaches (for the creation form) ---
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT c.courseCode, c.courseName
            FROM tutorcourse tc
            JOIN course c ON tc.courseCode = c.courseCode
            WHERE tc.tutorID = %s
        """, (session['userID'],))
        tutor_courses = cursor.fetchall()
        cursor.close()

        return render_template('my_sessions.html',
                             fullName=session.get('fullName'),
                             sessions=all_sessions,
                             my_group_sessions=my_group_sessions,
                             tutor_courses=tutor_courses)
    except Exception as e:
        flash(f'Error loading sessions: {str(e)}', 'error')
        return redirect('/tutor-dashboard')


@app.route('/upcoming-sessions')
def upcoming_sessions():
    """Show student's upcoming sessions (future and approved/pending)"""
    if 'userID' not in session or session.get('role') != 'student':
        flash('Please login to view upcoming sessions.', 'error')
        return redirect('/login')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT s.sessionID, s.courseCode, s.scheduledDate, s.scheduledTime, s.status, u.fullName "
            "FROM `session` s "
            "JOIN user u ON s.tutorID = u.userID "
            "WHERE s.studentID = %s AND s.scheduledDate >= CURDATE() "
            "ORDER BY s.scheduledDate ASC, s.scheduledTime ASC",
            (session['userID'],)
        )
        rows = cursor.fetchall()
        cursor.close()

        sessions = [
            {
                'sessionID': r[0],
                'courseCode': r[1],
                'scheduledDate': r[2],
                'scheduledTime': r[3],
                'status': r[4],
                'tutorName': r[5]
            }
            for r in rows
        ]
    except Exception as e:
        flash(f'Error loading upcoming sessions: {str(e)}', 'error')
        sessions = []

    return render_template('upcoming_sessions.html', fullName=session.get('fullName'), sessions=sessions)


@app.errorhandler(404)
def page_not_found(error):
    if request.path == '/favicon.ico':
        return '', 204  # silent ignore
    flash('Page not found. Redirecting to your dashboard.', 'error')
    return _redirect_on_error()

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors by redirecting to the appropriate dashboard"""
    flash('An internal error occurred. Redirecting to your dashboard.', 'error')
    return _redirect_on_error()

# ============ Main ============

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/browse')
def browse():
    return render_template('browse_sessions.html')


if __name__ == '__main__':
    app.run(debug=True)