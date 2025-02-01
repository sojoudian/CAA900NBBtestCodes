from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'flask_auth'

mysql = MySQL(app)

@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cursor.fetchone()

        if account:
            # account fields: (id, username, email, password, reset_token)
            stored_password = account[3]
            if check_password_hash(stored_password, password_candidate):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                flash('You are now logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password.', 'danger')
        else:
            flash('Email not found.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username         = request.form['username']
        email            = request.form['email']
        password         = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cursor.fetchone()
        if account:
            flash("Account already exists with that email.", "warning")
            return render_template('register.html')

        cursor.execute(
            "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
            (username, email, hashed_password)
        )
        mysql.connection.commit()
        flash("You have successfully registered! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cursor.fetchone()
        if account:
            # Generate a unique reset token
            token = str(uuid.uuid4())
            cursor.execute("UPDATE users SET reset_token = %s WHERE email = %s", (token, email))
            mysql.connection.commit()
            # In production, you would email the reset link.
            reset_link = url_for('reset_password', token=token, _external=True)
            flash(f"Password reset link (demo): {reset_link}", "info")
        else:
            flash("Email not found.", "danger")
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE reset_token = %s", (token,))
    account = cursor.fetchone()
    if not account:
        flash("Invalid or expired reset token.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        password         = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('reset_password.html', token=token)

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "UPDATE users SET password = %s, reset_token = NULL WHERE reset_token = %s",
            (hashed_password, token)
        )
        mysql.connection.commit()
        flash("Your password has been updated! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
