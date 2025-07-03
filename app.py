from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
from flask import g

app = Flask(__name__)
DATABASE = 'farmers.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            name TEXT,
            location TEXT,
            farm_size TEXT,
            crops TEXT,
            livestock TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS crop_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            crop TEXT,
            quantity TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS livestock_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            animal TEXT,
            count TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

init_db()

@app.route('/', methods=['GET'])
def index():
    return "Smart Inclusion USSD System Running"

@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.form.get("sessionId", "")
    service_code = request.form.get("serviceCode", "")
    phone_number = request.form.get("phoneNumber", "")
    text = request.form.get("text", "")
    steps = text.split("*") if text else []

    if text == "":
        response = "CON Welcome to Smart Inclusion System\n"
        response += "1. Register as Farmer\n"
        response += "2. Report Crop Production\n"
        response += "3. Report Livestock\n"
        response += "4. Check Market Prices\n"
        response += "5. Farming Tips\n"
        response += "6. Weather Update"
    elif steps[0] == "1":
        if len(steps) == 1:
            response = "CON Enter your name:"
        elif len(steps) == 2:
            response = "CON Enter your location:"
        elif len(steps) == 3:
            response = "CON Enter your farm size (e.g., 2 hectares):"
        elif len(steps) == 4:
            response = "CON Enter main crops (comma separated):"
        elif len(steps) == 5:
            response = "CON Enter livestock (comma separated, or 'none'):"
        elif len(steps) == 6:
            name = steps[1]
            location = steps[2]
            farm_size = steps[3]
            crops = steps[4]
            livestock = steps[5]
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("INSERT INTO farmers (phone, name, location, farm_size, crops, livestock) VALUES (?, ?, ?, ?, ?, ?)",
                    (phone_number, name, location, farm_size, crops, livestock))
                db.commit()
                response = "END Registration successful!"
            except Exception as e:
                response = "END Registration failed. Please try again."
        else:
            response = "END Invalid input."
    elif steps[0] == "2":
        # Crop Production Reporting
        if len(steps) == 1:
            response = "CON Enter crop name:"
        elif len(steps) == 2:
            response = "CON Enter quantity harvested (e.g., 100kg):"
        elif len(steps) == 3:
            crop = steps[1]
            quantity = steps[2]
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("INSERT INTO crop_reports (phone, crop, quantity) VALUES (?, ?, ?)", (phone_number, crop, quantity))
                db.commit()
                response = "END Crop production reported successfully!"
            except Exception as e:
                response = "END Crop reporting failed. Please try again."
        else:
            response = "END Invalid input."
    elif steps[0] == "3":
        # Livestock Reporting
        if len(steps) == 1:
            response = "CON Enter animal type (e.g., Goats):"
        elif len(steps) == 2:
            response = "CON Enter number of animals (e.g., 10):"
        elif len(steps) == 3:
            animal = steps[1]
            count = steps[2]
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("INSERT INTO livestock_reports (phone, animal, count) VALUES (?, ?, ?)", (phone_number, animal, count))
                db.commit()
                response = "END Livestock reported successfully!"
            except Exception as e:
                response = "END Livestock reporting failed. Please try again."
        else:
            response = "END Invalid input."
    elif text == "4":
        response = "END Tip: Rotate crops to improve soil fertility."
    elif text == "5":
        response = "END Weather: Light rains expected tomorrow."
    else:
        response = "END Invalid option"

    return response

@app.route('/dashboard')
def dashboard():
    db = get_db()
    cursor = db.cursor()
    # Fetch farmers
    cursor.execute('SELECT * FROM farmers')
    farmers = cursor.fetchall()
    # Fetch crop reports
    cursor.execute('SELECT * FROM crop_reports')
    crops = cursor.fetchall()
    # Fetch livestock reports
    cursor.execute('SELECT * FROM livestock_reports')
    livestock = cursor.fetchall()
    html = '''
    <h1>Smart Inclusion Dashboard</h1>
    <h2>Farmers</h2>
    <table border="1"><tr><th>ID</th><th>Phone</th><th>Name</th><th>Location</th><th>Farm Size</th><th>Crops</th><th>Livestock</th></tr>
    {% for f in farmers %}<tr>{% for v in f %}<td>{{v}}</td>{% endfor %}</tr>{% endfor %}</table>
    <h2>Crop Reports</h2>
    <table border="1"><tr><th>ID</th><th>Phone</th><th>Crop</th><th>Quantity</th><th>Date</th></tr>
    {% for c in crops %}<tr>{% for v in c %}<td>{{v}}</td>{% endfor %}</tr>{% endfor %}</table>
    <h2>Livestock Reports</h2>
    <table border="1"><tr><th>ID</th><th>Phone</th><th>Animal</th><th>Count</th><th>Date</th></tr>
    {% for l in livestock %}<tr>{% for v in l %}<td>{{v}}</td>{% endfor %}</tr>{% endfor %}</table>
    <h2>Broadcast Message</h2>
    <form method="post" action="/broadcast">
      <input type="text" name="message" placeholder="Enter message" required>
      <button type="submit">Send to All Farmers</button>
    </form>
    {% if sent %}<p style="color:green;">Message sent to all farmers!</p>{% endif %}
    '''
    sent = request.args.get('sent', False)
    return render_template_string(html, farmers=farmers, crops=crops, livestock=livestock, sent=sent)

@app.route('/broadcast', methods=['POST'])
def broadcast():
    # Simulate sending a message to all farmers (no SMS integration, just confirmation)
    message = request.form.get('message')
    # In a real system, you would send this message via SMS/USSD push
    # For now, just redirect to dashboard with a confirmation
    return redirect(url_for('dashboard', sent=True))

if __name__ == "__main__":
    app.run(debug=True)
