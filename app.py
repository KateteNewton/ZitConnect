from flask import Flask, render_template 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('register1.html')

@app.route('/tutor_verification')
def tutor_verification():
    return render_template('tutor_Verification.html')


@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/browse')
def browse():
    return render_template('browse_sessions.html')


if __name__ == '__main__':
    app.run(debug=True)

