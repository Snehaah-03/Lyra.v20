from flask import Flask, render_template, request, redirect, session, jsonify
import re
from werkzeug.security import generate_password_hash, check_password_hash

# Assuming utils.voice with speak() and listen()
from utils.voice import speak, listen

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

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
            try:
                speak(f"Welcome back, {user['name']}!")
            except RuntimeError:
                print("Voice speak skipped due to runtime error")

            # Redirect to chat page instead of dashboard
            return redirect('/mode')
        else:
            speak("Login failed. Please try again.")
            return render_template('login.html', error="Invalid login")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if email in users:
            return render_template('signup.html', error="Email already registered")
        password = generate_password_hash(request.form['password'])
        users[email] = {'name': name, 'password': password}
        speak(f"Hello {name}, welcome to Lyra!")
        return redirect('/login')
    return render_template('signup.html')

# Optional: Keep dashboard route if you want a separate BMI page accessible anytime
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    result = None

    if request.method == 'POST':
        try:
            # Read the inputs safely and convert to float
            height = request.form.get('height', type=float)
            weight = request.form.get('weight', type=float)

            # Check if either input is missing
            if height is None or weight is None:
                raise ValueError("Missing input")

            height_m = height / 100  # convert cm to meters

            # Calculate BMI
            bmi = round(weight / (height_m * height_m), 2)

            # Generate health tip based on BMI
            result = generate_health_tip(bmi)

            # Optional: Speak result without crashing
            try:
                speak(result)
            except RuntimeError:
                pass

        except Exception:
            result = "Please enter valid height and weight."

    # Send name and result back to dashboard.html
    return render_template('dashboard.html', name=session['user'], result=result)

@app.route('/speak', methods=['POST'])
def speak_input():
    if 'user' not in session:
        return redirect('/login')

    command = listen()

    # Extract height and weight numbers from the voice command
    height_match = re.search(r'height.*?(\d+)', command)
    weight_match = re.search(r'weight.*?(\d+)', command)

    if not height_match or not weight_match:
        speak("Sorry, I couldn't understand your height or weight.")
        return redirect('/dashboard')

    height = float(height_match.group(1))
    weight = float(weight_match.group(1))
    bmi = round(weight / ((height / 100) ** 2), 2)
    result = generate_health_tip(bmi)
    speak(result)

    return render_template('dashboard.html', name=session['user'], result=result)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect('/login')
    return render_template('chat.html', name=session['user'])
@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user' not in session:
        return jsonify({'reply': "Please login to chat with Lyra."})

    data = request.get_json()
    user_msg = data.get('message', '').lower()

    if not user_msg:
        return jsonify({'reply': "Please enter a message to chat."})

    # Basic response logic
    if 'weight loss' in user_msg or 'reduce weight' in user_msg:
        reply = (
            "To reduce weight:\n"
            "- Eat high-fiber, low-calorie meals like oats, salads, fruits, boiled eggs.\n"
            "- Avoid fried and sugary food.\n"
            "- Exercise daily (30 mins walk, yoga, or home workout).\n"
            "- Drink 2-3 liters of water a day."
        )
    elif 'weight gain' in user_msg or 'increase weight' in user_msg:
        reply = (
            "To gain weight:\n"
            "- Eat more frequently with protein-rich food (milk, nuts, eggs, paneer).\n"
            "- Add calorie-dense foods like banana, peanut butter, dry fruits.\n"
            "- Avoid junk food.\n"
            "- Do strength training to build healthy weight."
        )
    elif 'meal plan' in user_msg:
        reply = (
            "Here's a basic healthy meal plan:\n"
            "- Breakfast: Oats + Fruit + Boiled Egg\n"
            "- Lunch: Brown Rice + Veg Curry + Curd\n"
            "- Evening: Fruits/Nuts + Tea\n"
            "- Dinner: Chapati + Grilled Vegetables\n"
            "- Drink water throughout the day."
        )
    elif 'sleep' in user_msg or 'sleep tips' in user_msg:
        reply = (
            "Healthy Sleep Tips:\n"
            "- Aim for 7–9 hours of sleep.\n"
            "- Sleep and wake up at the same time daily.\n"
            "- Avoid screens 1 hour before bed.\n"
            "- Reduce caffeine after evening.\n"
            "- Create a calm, dark sleep environment."
        )
    elif 'bmi' in user_msg:
        reply = "To know your BMI, go to the dashboard and enter your height and weight. Lyra will calculate and guide you!"
    else:
        reply = (
            "Hi! I'm Lyra 🌸 You can ask me about:\n"
            "- How to reduce/increase weight\n"
            "- Meal plans\n"
            "- Sleep advice\n"
            "- Water intake\n"
            "- Or how to use the BMI tool"
        )

    return jsonify({'reply': reply})
@app.route('/mode')
def mode():
    if 'user' not in session:
        return redirect('/login')
    return render_template('mode.html', name=session['user'])
def generate_health_tip(bmi):
    if bmi < 18.5:
        return f"Your BMI is {bmi}. You're underweight. Consider a nutrient-rich diet."
    elif 18.5 <= bmi < 25:
        return f"Your BMI is {bmi}. Great! You're at a healthy weight."
    elif 25 <= bmi < 30:
        return f"Your BMI is {bmi}. You're overweight. Try a balanced diet and regular exercise."
    else:
        return f"Your BMI is {bmi}. You are in the obese range. It's best to consult a doctor."

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

