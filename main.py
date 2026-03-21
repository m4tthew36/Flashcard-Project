from flask import Flask, render_template, request, redirect, url_for
from database.database_handler import DatabaseHandler
from database.database_exceptions import nonUniqueUsername
from flask_login import LoginManager, login_user, login_required, current_user


app = Flask(__name__) 
# initializes the Flask application and sets up the login manager for handling user authentication and session management.
app.config["SECRET_KEY"] = "temporary_secret"
# set up the login manager
lm = LoginManager(app) 
# define the route for un logged in users 
lm.login_view =  "signin"
@lm.user_loader
def load_user(user_id):
# method of checking logged in user by id 
    dbh = DatabaseHandler() 
    return dbh.getUserById(user_id)    


@app.route("/") #redirect for dashboard for logged in 
def home():
    return redirect(url_for("dashboard"))


@app.route("/signin") #signin page
def signin():
    return render_template("signin.html") #returns the signin page 


@app.route("/signup") #signup page
def signup():
    return render_template("signup.html") #returns the signup page 


@app.route("/dashboard") #dashboard page
@login_required
def dashboard():
    return render_template("dashboard.html") # returns the dashboard page 


@app.route("/learn") #learn page
@login_required
def learn():
    # list available decks to learn from
    dbh = DatabaseHandler()
    # placeholder user id 
    decks = dbh.get_decks(user_id=1)  #
    return render_template("learn.html", decks=decks) #returns the learn page with the decks available to learn from for this user 


@app.route("/edit-cards") #edit cards page
@login_required
def edit_cards():
    dbh = DatabaseHandler() #
    decks = dbh.get_decks(user_id=1) # placeholder user id
    return render_template("edit_cards.html", decks=decks) #returns the edit cards page with the decks available to edit for this user


@app.route("/classes") #classes page
@login_required

def classes():
    dbh = DatabaseHandler()
    decks = dbh.get_decks(user_id=1)
    return render_template("classes.html", decks=decks) #returns the classes page with the users not with usertype of teacher 

@app.route("/auth/authoriseuser", methods = ["POST"]) #authorise user
def authorize_user():
    formDetials = request.form #retrieve details from submitted form by the user 
    username = formDetials.get("username") #retrieved username
    password = formDetials.get("password") #retrievced password 

    db1 = DatabaseHandler()
    Success = db1.getUser(username, password)  #retreve users username and password 
    if Success: #check for success
        return redirect(url_for("dashboard")) #returns redirect for succesfull loging/
    
    return "failed to authorise user..." # user feedback message returned if authorize_user is False


@app.route("/auth/createuser", methods = ["POST"])
def create_user():  #used for creating a user 
    formDetials = request.form #retrieve inputs from form 
    username = formDetials.get("username") #retreived username 
    password = formDetials.get("password") #retreived password 
    repassword = formDetials.get("repassword") #retreived repassword 
    teacher = formDetials.get("teacher") == "on" #retreived usertype for teacher or student settings 

    if len(username) > 5 and len(password) > 7 and len(repassword) > 7 and password == repassword: #validation for username and password 
        db = DatabaseHandler()
        try:
            db.createUser(username, password, teacher) #db function to create the user paramters are values for each field
        except nonUniqueUsername:
            return "Username already exists." # user feedback message returned if the username is not unique
        except Exception as e: 
            print(f"An error occurred: {e}")  
            return "An error occurred while creating the user." # user feedback message returned if there is an error during user creation

        return redirect(url_for("dashboard")) #return redirect for dashbaord if successfull
    elif len(username) <= 5:
        return "username must be more than 5 characters"
    elif len(password) <= 7:
        return "password must be more than 7 characters"
    elif password != repassword:
        return "passwords and repassword do not match"  # user feedback based upon invalid form received 
    

    return "failed to create user..."



@app.route("/auth/signin", methods = ["POST"]) #signin user
def signin_user():  
    formDetials = request.form
    username = formDetials.get("username") #retrieve username from form
    password = formDetials.get("password") #retrieve password from form

    db1 = DatabaseHandler()
    user = db1.getUser(username, password)
    if user:
        login_user(user) #login user using flask login
        return redirect(url_for("dashboard"))
    
    return "failed to signin..."


@app.route('/learn/<int:deck_id>')
@login_required
def learn_deck(deck_id):
    dbh = DatabaseHandler()
    cards = dbh.get_flashcards(deck_id) #retrieve the decks available for a user 
    # simple index-based navigation
    try:
        index = int(request.args.get('i', 0)) #try to retrieve the index from the query parameters, default to 0 if invalid
    except ValueError: 
        index = 0
    if not cards:
        return "No cards in this deck." #validation if there are no cards inside of the deck return feedback to user 
    card = cards[index % len(cards)]
    return render_template('learn_deck.html', card=card, deck_id=deck_id, index=index, total=len(cards))


@app.route('/edit-cards/<int:deck_id>', methods=['GET', 'POST']) #edit cards for a specific deck
def manage_deck(deck_id):
    dbh = DatabaseHandler()
    if request.method == 'POST':
        # add new card
        question = request.form.get('question')
        answer = request.form.get('answer')
        dbh.add_flashcard(deck_id, question, answer, user_id=1)
        return redirect(url_for('manage_deck', deck_id=deck_id))
    cards = dbh.get_flashcards(deck_id)
    deck = dbh.get_deck(deck_id)
    return render_template('edit_deck.html', cards=cards, deck=deck)


@app.route('/edit-cards/<int:deck_id>/delete/<int:card_id>', methods=['POST']) #delete a specific card from a specific deck
def delete_card(deck_id, card_id): 
    dbh = DatabaseHandler()
    dbh.delete_flashcard(card_id)
    return redirect(url_for('manage_deck', deck_id=deck_id))


@app.route('/classes/create', methods=['POST']) #create a new class (deck) for the user
def create_class():
    dbh = DatabaseHandler()
    name = request.form.get('name') #retrieve the name of the deck from the form
    subject = request.form.get('subject') #retrieve the subject of the deck from the form
    dbh.create_deck(name, subject, user_id=1) 
    return redirect(url_for('classes'))   


db = DatabaseHandler()

app.run(debug = True)