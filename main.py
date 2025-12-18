from flask import Flask, render_template, request, redirect, url_for
from database import DatabaseHandler


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/auth/createuser", methods = ["POST"])
def create_user():  
    formDetials = request.form
    username = formDetials.get("username")
    password = formDetials.get("password")
    repassword = formDetials.get("repassword")
    teacher = formDetials.get("teacher") == "on"

    if len(username) > 5 and len(password) > 7 and len(repassword) > 7 and password == repassword:
       db = DatabaseHandler()
       success = db.createUser(username, password, teacher)
       if success:
           return redirect(url_for("dashboard"))


    return "failed to create user..."


@app.route("/auth/signin", methods = ["POST"])
def signin_user():  
    formDetials = request.form
    username = formDetials.get("username")
    password = formDetials.get("password")

    db1 = DatabaseHandler()
    user = db1.getUser(username, password)
    if user:
        return redirect(url_for("dashboard"))
    
    return "failed to signin..."

db = DatabaseHandler()
db.createTable_users()

app.run(debug = True)