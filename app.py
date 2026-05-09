from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from datetime import timedelta
import re

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

# ============ Helper Functions ============
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

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

# ============ Routes ============

@app.route('/')
def home():
    """Home route - redirect to register"""
    return render_template('register1.html')

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

@app.route('/register/complete', methods=['POST'])
def register_complete():
    """Complete registration - Save to database"""
    # Verify step 1 data exists
    if 'email' not in session:
        flash('Session expired. Please register again.', 'error')
        return redirect('/register')
    
    try:
        # Get data from session and step 2 form
        full_name = session.get('name', '')
        user_name = session.get('username', '')
        email = session.get('email', '')
        password = session.get('password', '')
        program = request.form.get('program', '').strip()
        school = request.form.get('school', '').strip()
        role = request.form.get('role', '').strip()
        
        # Validate step 2 data
        if not all([program, school, role]):
            flash('Please select program, school, and role', 'error')
            return redirect('/register/step2')
        
        # Insert into database
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO user (fullName, userName, email, password, role, program, school) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (full_name, user_name, email, password, role, program, school)
        )
        mysql.connection.commit()
        cursor.close()
        
        # Clear session
        session.clear()
        flash('User registered successfully! Please login.', 'success')
        return redirect('/login')
        
    except Exception as e:
        flash(f'Registration error: {str(e)}', 'error')
        print(f"Registration Error: {e}")
        return redirect('/register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        # TODO: Implement login logic
        pass
    return render_template('login.html')

# ============ Error Handlers ============

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# ============ Main ============

if __name__ == '__main__':
    app.run(debug=True)

