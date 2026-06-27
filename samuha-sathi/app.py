from flask import Flask, render_template, request, redirect
import sqlite3
import os
import json
import google.generativeai as genai
from flask import jsonify

genai.configure(api_key="AQ.Ab8RN6LA4mcdZcArqAFvMOHZoxhoRSRNavPfFCB8AUQea5zCKQ")
model = genai.GenerativeModel("gemini-pro")

LOCATIONS_PATH = os.path.join(os.path.dirname(__file__), "nepal_location.json")

with open(LOCATIONS_PATH) as f:
    nepal_locations = json.load(f)

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

@app.route("/")
def home():
    return render_template("home.html")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            joined_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/members")
def members():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    all_members = cursor.fetchall()
    conn.close()
    return render_template("members.html", members=all_members)

@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        province = request.form["province"]
        district = request.form["district"]
        municipality = request.form["municipality"]
        joined_date = request.form["joined_date"]
        address = f"{municipality}, {district}, {province}"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name, phone, address, joined_date) VALUES (?, ?, ?, ?)",
                       (name, phone, address, joined_date))
        conn.commit()
        conn.close()
        return redirect("/members")
    return render_template("add_member.html", locations=nepal_locations)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    response_text = ""
    if request.method == "POST":
        user_message = request.form["message"]

        # give context about the app
        prompt = f"""
        You are a helpful assistant for Samuha Sathi — a digital management 
        tool for women's community groups in Nepal. 
        Answer in simple English or Nepali based on the question.
        Question: {user_message}
        """
        response = model.generate_content(prompt)
        response_text = response.text

    return render_template("chat.html", response=response_text)

@app.route("/chat_api", methods=["POST"])
def chat_api():
    data = request.get_json()
    user_message = data["message"]
    prompt = f"""
    You are a helpful assistant for Samuha Sathi — a digital management 
    tool for women's community groups in Nepal. Answer briefly and simply.
    Question: {user_message}
    """
    response = model.generate_content(prompt)
    return jsonify({"reply": response.text})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)