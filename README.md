ZitConnect: Student Academic Support System

The Copperbelt University - School of ICT (Group 18)

ZitConnect is a centralized, verification-driven academic marketplace designed for CBU students. It facilitates peer-to-peer tutoring matching, secure group session payments via Lenco, and institutional analytics.

🛠 Tech Stack
Backend: Python 3.10+ (Flask Framework)
Database: MySQL (via XAMPP)
Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript
Payments: Lenco API Integration
Server Environment: Localhost (Development) / Linux (Production)


📋 Prerequisites
Ensure you have the following installed on your PC:
Python 3.x: Download here
XAMPP: (To run the MySQL Database) Download here
Git: (Optional, for version control)


🚀 Installation & Setup
1. Clone or Extract the Project
If using Git, clone the repository. Otherwise, extract the project folder to your desired location.
code
cd ZitConnect

2. Set Up the Virtual Environment
It is recommended to use a virtual environment to manage dependencies.
# Create the environment
python -m venv venv

# Activate the environment (Windows)
venv\Scripts\activate

# Activate the environment (Mac/Linux)
source venv/bin/activate


3. Install Dependencies
Install all required libraries including Flask, SQLAlchemy, and Requests.
pip install -r requirements.txt

4. Database Configuration (XAMPP)
Open XAMPP Control Panel and start Apache and MySQL.
Open your browser and go to http://localhost/phpmyadmin/.
Create a new database named zitconnect_db.
Import the provided database/zitconnect_schema.sql file.


🏃 Running the Application
Once the database is set up and dependencies are installed, run the server:
code
Bash
python app.py
The system will be live at: http://127.0.0.1:5000

📂 Project Structure
/app - Core Flask logic and routes.
/static - CSS, JavaScript, and Brand images.
/templates - HTML UI views (Dashboards, Booking, Payments).
/migrations - Database version control.

⚠️ Troubleshooting
MySQL Connection Failed: Ensure XAMPP MySQL is running on port 3306.
Port 5000 in Use: If another app is using port 5000, run Flask on a different port: python app.py --port 5001.
Lenco Links Not Unlocking: Ensure Ngrok is running and the Webhook route /payment/webhook is correctly configured in the Lenco dashboard.
Developed by Group 18:
Newton Katete (23132323)
Mwape Cecilia (23135032)
Kabila Nicodemus (22175424)
Chali Henry Pm (23126269)
Supervisor: Mrs. Banda