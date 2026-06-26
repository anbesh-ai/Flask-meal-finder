from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")          # home page
def home():
    return render_template("home.html")

@app.route("/meal")      # meal page
def meal():
    response = requests.get("https://api.freeapi.app/api/v1/public/meals/meal/random")
    data = response.json()["data"]
    return render_template("meal.html", meal=data)

@app.route("/contact")   # contact page
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)