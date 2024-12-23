from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3
import os


app = Flask(__name__)
app.secret_key = "a1ac66107551bf930811b6ea52ed381a51dadefc424fd6e8"  # Replace with a secure random key

# Initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # Add a default admin user
        conn.execute("INSERT OR IGNORE INTO admins (admin_name, username, password) VALUES (?, ?, ?)",
                     ('Admin#001', 'admin', 'password123'))
        conn.execute("INSERT OR IGNORE INTO admins (admin_name, username, password) VALUES (?, ?, ?)",
                     ('Owden', 'admin@owdenmagnusen', 'Commando1+'))  # Replace with a hashed password for production
    print("Database initialized!")

# Route for admin login
@app.route("/admin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin_name = request.form["admin_name"]
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE admin_name = ? AND username = ? AND password = ? ", 
                           (admin_name, username, password))
            admin = cursor.fetchone()

        if admin:
            session["admin_logged_in"] = True
            session["admin_name"] = admin_name
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.")

    return render_template("admin_login.html")

# Route for admin logout
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

# Route for client form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)", 
                           (name, phone, email))
            conn.commit()

        return redirect(url_for("index"))

    return render_template("index.html")

# Route for dashboard 
@app.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    
    admin_name = session.get("admin_name")

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
    return render_template("dashboard.html", clients=clients, admin_name=admin_name)

#Route for delete function
@app.route("/delete/<int:client_id>", methods=["POST"])
def delete(client_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the entry exists
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Entry not found'}), 404

        # Delete the entry
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()

        # Reset IDs after deletion
        cursor.execute("SELECT id FROM clients ORDER BY id ASC")
        rows = cursor.fetchall()

        #Reassign IDs
        for idx, row in enumerate(rows, start=1):
            cursor.execute("UPDATE clients SET id = ? WHERE id = ?", (idx, row[0]))
            conn.commit()

        return jsonify({'message': 'Entry deleted successfully.'})

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return jsonify({'error': 'Error deleting entry. Please try again.'}), 500

    finally:
        if conn:
            conn.close()

def reset_ids():

    conn = None
    try:
        conn = sqlite3.connet('database.db')
        cursor = conn.cursor

        cursor.execute("SELECT * FROM clients ORDER BY id ASC")
        rows = cursor.fetchall()

        cursor.execute("DROP TABLE IF EXITST clients")
        cursor.execute("""
            CREATE TABLE client (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       phone TEXT NOT NULL,
                       email TEXT NOT NULL
                    )
                """)
        
        for index, row in enumerate(rows,start=1):
            cursor.execute(
                "INSERT INTO client (id, name, phone, email) VALUES (?,?,?,?)",
                (index, row[1], row[2], row[3],)
            )

        conn.commit()

    finally:
        if conn:
            conn.close

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
