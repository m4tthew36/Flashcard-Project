from flask import Flask, render_template, request, redirect, url_for
from database.database_handler import DatabaseHandler
from database.database_exceptions import nonUniqueUsername
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from models.user_models import UserType


app = Flask(__name__)
# initializes the Flask application and sets up the login manager for handling user authentication and session management.
app.config["SECRET_KEY"] = "temporary_secret"
# set up the login manager
lm = LoginManager(app)
# define the route for un logged in users
lm.login_view = "signin"


@lm.user_loader
def load_user(user_id):
    # method of checking logged in user by id
    dbh = DatabaseHandler()
    return dbh.getUserById(user_id)


@app.route("/")  # redirect for dashboard for logged in
def home():
    return redirect(url_for("dashboard"))


@app.route("/signin")  # signin page
def signin():
    return render_template("signin.html")  # returns the signin page


@app.route("/signout")  # signout page
@login_required
def signout():
    logout_user()  # logout user using flask login
    return redirect(url_for("signin"))  # redirect to signin page after signing out


@app.route("/signup")  # signup page
def signup():
    return render_template("signup.html")  # returns the signup page


@app.route("/dashboard")  # dashboard page
@login_required
def dashboard():
    # check the current user type from the user stored by flask login
    if current_user.usertype == UserType.STUDENT.value:
        # for student
        print("im a student ")
        pass
    elif current_user.usertype == UserType.TEACHER.value:
        # for teacher
        print("im a teacher ")
        pass
    else:
        redirect(url_for("signout"))
        pass
    return render_template("dashboard.html")  # returns the dashboard page


@app.route("/learn")  # learn page
@login_required
def learn():
    # list available decks to learn from
    dbh = DatabaseHandler()
    # placeholder user id
    decks = dbh.get_decks(user_id=1)  #
    return render_template(
        "learn.html", decks=decks
    )  # returns the learn page with the decks available to learn from for this user


@app.route("/edit-cards")  # edit cards page
@login_required
def edit_cards():
    dbh = DatabaseHandler()  #
    decks = dbh.get_decks(user_id=1)  # placeholder user id
    return render_template(
        "edit_cards.html", decks=decks
    )  # returns the edit cards page with the decks available to edit for this user


@app.route("/classes")  # classes page
@login_required
def classes():
    dbh = DatabaseHandler()
    decks = dbh.get_decks(user_id=1)
    return render_template(
        "classes.html", decks=decks
    )  # returns the classes page with the users not with usertype of teacher


@app.route("/auth/createuser", methods=["POST"])
def create_user():  # used for creating a user
    formDetials = request.form  # retrieve inputs from form
    username = formDetials.get("username")  # retreived username
    password = formDetials.get("password")  # retreived password
    repassword = formDetials.get("repassword")  # retreived repassword
    teacher = (
        formDetials.get("teacher") == "on"
    )  # retreived usertype for teacher or student settings
    if teacher:
        usertype = UserType.TEACHER  # set usertype to teacher if teacher box is checked
    else:
        usertype = (
            UserType.STUDENT
        )  # set usertype to student if teacher box is not checked

    if (
        len(username) > 5
        and len(password) > 7
        and len(repassword) > 7
        and password == repassword
    ):  # validation for username and password
        db = DatabaseHandler()
        try:
            db.createUser(
                username, password, usertype.value
            )  # db function to create the user paramters are values for each field
        except nonUniqueUsername:
            return "Username already exists."  # user feedback message returned if the username is not unique
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while creating the user."  # user feedback message returned if there is an error during user creation

        return redirect(
            url_for("dashboard")
        )  # return redirect for dashbaord if successfull
    elif len(username) <= 5:
        return "username must be more than 5 characters"
    elif len(password) <= 7:
        return "password must be more than 7 characters"
    elif password != repassword:
        return "passwords and repassword do not match"  # user feedback based upon invalid form received

    return "failed to create user..."




@app.route("/auth/signin", methods=["POST"])  # signin user
def signin_user():
    formDetials = request.form
    username = formDetials.get("username")  # retrieve username from form
    password = formDetials.get("password")  # retrieve password from form

    db1 = DatabaseHandler()
    user = db1.getUser(username, password)
    print(user.username)
    print(user.usertype)
    if user:
        login_user(user)  # login user using flask login
        return redirect(url_for("dashboard"))

    return "failed to signin..."


@app.route("/auth/signout")  # signout user
@login_required
def signout_user():
    logout_user()  # logout user using flask login
    return redirect(url_for("signin"))  # redirect to signin page after signing out


@app.route("/learn/<int:deck_id>")
# route for learning 
def learn_deck(deck_id):
    dbh = DatabaseHandler()
    # retreieve all flashcards 
    cards = dbh.get_flashcards(deck_id)
    try:
        # retrieve the index of the card to be displayed from the query parameters
        index = int(request.args.get("i", 0))
    except ValueError:
        index = 0
    if not cards:
        return "No cards in this deck."
    
    # use the modulus of the operator to loop back to start 
    index = index % len(cards) 
    # retrieve the card at the current index to be displayed on the learn page
    card = cards[index]
    
    return render_template(
        # return the learn page with deck and correct number of flashcards and current card
        "learn_deck.html", card=card, deck_id=deck_id, index=index, total=len(cards)
    )


@app.route(
    "/edit-cards/<int:deck_id>", methods=["GET", "POST"]
)  # edit cards for a specific deck
def manage_deck(deck_id):
    dbh = DatabaseHandler()
    if request.method == "POST":
        # add new card
        question = request.form.get("question")
        answer = request.form.get("answer")
        dbh.add_flashcard(deck_id, question, answer, user_id=1)
        return redirect(url_for("manage_deck", deck_id=deck_id))
    cards = dbh.get_flashcards(deck_id)
    deck = dbh.get_deck(deck_id)
    return render_template("edit_deck.html", cards=cards, deck=deck)

# route for deleting a specific card from a specific deck
@app.route( 
    "/edit-cards/<int:deck_id>/delete/<int:card_id>", methods=["POST"]
)  # delete a specific card from a specific deck
def delete_card(deck_id, card_id):
    #connect to database so card can be retrieved and altered 
    dbh = DatabaseHandler()
    #function to delete the card 
    dbh.delete_flashcard(card_id)
    return redirect(url_for("manage_deck", deck_id=deck_id))


@app.route(
    "/classes/create", methods=["POST"]
)  # create a new class (deck) for the user
def create_class():
    dbh = DatabaseHandler()
    name = request.form.get("name")  # retrieve the name of the deck from the form
    subject = request.form.get(
        "subject"
    )  # retrieve the subject of the deck from the form
    dbh.create_deck(name, subject, user_id=1)
    return redirect(url_for("classes"))


# account management stuff

@app.route("/management", methods=["GET"])
# route for account management page 
@login_required
def management():
    # return the webpage
    return render_template("management.html")


@app.route("/auth/reset-password", methods=["POST"])
@login_required
# reset password function 
def reset_password():
    dbh = DatabaseHandler()
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

# comparing the two password and repassword in the form 
    if new_password != confirm_password:
        return "passwords do not match"
    success = dbh.update_password(current_user.id, current_password, new_password)
    if success:
        # if the password update is successful return this message to the user
        return "password updated successfully"
    else:
        # if the password update is not successful return this message to the user
        return "incorrect current password"


@app.route("/auth/delete-account", methods=["POST"])
@login_required
def delete_account():
    dbh = DatabaseHandler()
    # retrieve the password from the form to confirm account deletion
    password = request.form.get("delete_password")

    success = dbh.delete_account(current_user.id, password)
    if success:
        # logout so session ends 
        logout_user()
        # sent back to signin page after account deletion
        return redirect(url_for("signin"))
    else:
        # if account deletion is unsuccessful 
        return "incorrect password"


db = DatabaseHandler()

app.run(debug=True)
