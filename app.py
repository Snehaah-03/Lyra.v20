# 📁 app.py (Updated)

from flask import Flask, render_template, request, redirect, url_for, session
import os
from utils.voice import speak, listen
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user storage
users = {}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            session['user'] = user['name']
            speak(f"Welcome back, {user['name']}!")
            return redirect('/dashboard')
        else:
            speak("Login failed. Please try again.")
            return render_template('login.html', error="Invalid login")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        users[email] = {'name': name, 'password': password}
        speak(f"Hello {name}, welcome to Lyra!")
        return redirect('/login')
    return render_template('signup.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    result = None
    if request.method == 'POST':
        try:
            height = float(request.form['height']) / 100
            weight = float(request.form['weight'])
            bmi = round(weight / (height * height), 2)
            result = generate_health_tip(bmi)
            speak(result)
        except:
            result = "Please enter valid height and weight."
            speak(result)

    return render_template('dashboard.html', name=session['user'], result=result)

def generate_health_tip(bmi):
    if bmi < 18.5:
        return f"Your BMI is {bmi}. You're underweight. Consider a nutrient-rich diet."
    elif 18.5 <= bmi < 25:
        return f"Your BMI is {bmi}. Great! You're at a healthy weight."
    elif 25 <= bmi < 30:
        return f"Your BMI is {bmi}. You're overweight. Try a balanced diet and regular exercise."
    else:
        return f"Your BMI is {bmi}. You are in the obese range. It's best to consult a doctor."

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

