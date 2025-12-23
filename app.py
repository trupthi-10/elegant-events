from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def db():
    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table
conn = db()
conn.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    event_type TEXT,
    event_date TEXT,
    guests INTEGER,
    cost INTEGER
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS admin (
    username TEXT,
    password TEXT
)
""")
conn.execute("INSERT OR IGNORE INTO admin VALUES ('admin','admin123')")
conn.commit()
conn.close()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/book", methods=["GET","POST"])
def book():
    if request.method == "POST":
        guests = int(request.form["guests"])
        cost = guests * 1200
        session["booking"] = dict(request.form)
        session["booking"]["cost"] = cost
        return render_template("confirm.html", cost=cost)
    return render_template("book.html")

@app.route("/confirm", methods=["POST"])
def confirm():
    b = session.get("booking")
    conn = db()
    conn.execute("""
    INSERT INTO bookings (name,email,event_type,event_date,guests,cost)
    VALUES (?,?,?,?,?,?)
    """,(b["name"],b["email"],b["event_type"],b["event_date"],b["guests"],b["cost"]))
    conn.commit()
    conn.close()
    session.pop("booking")
    return "<h2>Thank you! Your event is booked successfully 🎉</h2>"

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin123":
            session["admin"]=True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    conn = db()
    data = conn.execute("SELECT * FROM bookings").fetchall()
    conn.close()
    return render_template("admin.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
