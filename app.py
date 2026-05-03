from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from datetime import timedelta

app = Flask(__name__)

# Session configuration
app.secret_key = 'zitconnect_secret_key_2024'
app.permanent_session_lifetime = timedelta(minutes=30)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'zitconnect_db'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('register1.html')

# Register Step 1 Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['username'] = request.form['username']
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        session['confirm_password'] = request.form['confirm_password']
        
        return redirect('/register/step2')
    return render_template('register1.html')

# Register Step 2 Route
@app.route('/register/step2', methods=['GET'])
def register_step2():
    # Check if user has completed step 1
    if 'email' not in session:
        return redirect('/register')
    
    # Fetch programs and schools from database
    try:
        cursor = mysql.connection.cursor()
        
        # Fetch programs
        cursor.execute("SELECT programID, programName FROM program ORDER BY programName")
        programs = cursor.fetchall()
        
        # Fetch schools
        cursor.execute("SELECT schoolID, schoolName FROM school ORDER BY schoolName")
        schools = cursor.fetchall()
        
        cursor.close()
        
        return render_template('register2.html', programs=programs, schools=schools)
    except Exception as e:
        print(f"Error fetching programs/schools: {e}")
        # If tables don't exist, return empty lists
        return render_template('register2.html', programs=[], schools=[])

# Complete Registration Route
@app.route('/register/complete', methods=['POST'])
def register_complete():
    # Check if step 1 data exists
    if 'email' not in session:
        return redirect('/register')
    
    # Get data from session and step 2 form
    full_name = session.get('name')
    user_name = session.get('username')
    email = session.get('email')
    password = session.get('password')
    program = request.form.get('program')
    school = request.form.get('school')
    role = request.form['role']
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO user (fullName, userName, email, password, role, program, school) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (full_name, user_name, email, password, role, program, school)
        )
        mysql.connection.commit()
        cursor.close()
        
        # Clear session and flash success message
        session.clear()
        flash('User registered successfully! Please login.', 'success')
        
        return redirect('/login')
    except Exception as e:
        flash(f'Registration error: {str(e)}', 'error')
        print(f"Error: {e}")
        return redirect('/register')

# Login Route
@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True) 

