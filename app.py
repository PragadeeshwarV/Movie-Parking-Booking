from flask import Flask, render_template, request, session, jsonify, url_for, redirect
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Configure Flask-Session properly
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True  
app.config["SESSION_USE_SIGNER"] = True  
app.config["SESSION_FILE_DIR"] = "./flask_session"  
Session(app)

# ✅ MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Vijay@2004"
app.config["MYSQL_DB"] = "movie_booking"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/free")
def free():
    return render_template("free.html")


# ✅ Home Page
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

# ✅ Login Page
@app.route('/login', methods=['GET'])
def login():
    return render_template("login1.html")
@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400
    
    hashed_password = generate_password_hash(password)

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return jsonify({"status": "error", "message": "Email already registered!"}), 400

            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                        (name, email, hashed_password))
            mysql.connection.commit()

        return jsonify({"status": "success", "message": "Registered successfully!"}), 200

    except Exception as e:
        print("Registration Error:", str(e))
        return jsonify({"status": "error", "message": "Server error, try again later!"}), 500


# ✅ Login Post Route
@app.route('/login_post', methods=['POST'])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    with mysql.connection.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

    if user and check_password_hash(user['password'], password):
        session["user_id"] = user['id']
        session["user_name"] = user['name']
        session["logged_in"] = True
        session.modified = True  # ✅ Forces session update
        return jsonify({"status": "success", "message": "Login successful!", "redirect": url_for('index')})
    
    return jsonify({"status": "error", "message": "Invalid credentials!"})

# ✅ Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ✅ Function to enforce login before accessing movie pages
def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ✅ Movie pages - Only accessible after login
routes = [
    "coolie1", "coolie2", "coolie3", "coolie4",
    "thug1", "thug2", "thug3", "thug4",
    "jana1", "jana2", "jana3", "jana4",
    "GBU1", "GBU2", "GBU3", "GBU4",
    "Retro1", "Retro2", "Retro3", "Retro4",
    "IDLY1", "IDLY2", "IDLY3", "IDLY4","officialpark",
   
]

for route in routes:
    if route != "officialpark":  # Skip officialpark to avoid duplicate route issue
        app.add_url_rule(f"/{route}", route, login_required(lambda route=route: render_template(f"{route}.html")))


@app.route("/officialpark")
def officialpark():
    return render_template("officialpark.html")

# ✅ Ticket Booking - Ensures only logged-in users can book
@app.route("/book_ticket", methods=["POST"])
def book_ticket():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Please log in to book tickets!"})

    movie_name = request.form.get("movie_name")
    seat_number = request.form.get("seat_number")

    if not movie_name or not seat_number:
        return jsonify({"status": "error", "message": "Movie and seat selection required!"})

    user_id = session.get("user_id")

    with mysql.connection.cursor() as cur:
        cur.execute("INSERT INTO bookings (user_id, movie_name, seat_number) VALUES (%s, %s, %s)", 
                    (user_id, movie_name, seat_number))
        mysql.connection.commit()

    return jsonify({"status": "success", "message": "Ticket booked successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
