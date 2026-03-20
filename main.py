from flask import Flask, render_template, request, redirect, url_for
from database import DatabaseHandler

app = Flask(__name__)

@app.route("/") #signin page
def home():
    return render_template("signin.html") #returns the signin page 


@app.route("/signup") #signup page
def signup():
    return render_template("signup.html") #returns the signup page 


@app.route("/dashboard") #dashboard page
def dashboard():
    return render_template("dashboard.html") # returns the dashboard page 


@app.route("/learn") #learn page
def learn():
    # list available decks to learn from
    dbh = DatabaseHandler()
    # placeholder user id 
    decks = dbh.get_decks(user_id=1)  #
    return render_template("learn.html", decks=decks) #returns the learn page with the decks available to learn from for this user 


@app.route("/edit-cards") #edit cards page
def edit_cards():
    dbh = DatabaseHandler()
    decks = dbh.get_decks(user_id=1) # placeholder user id
    return render_template("edit_cards.html", decks=decks) #returns the edit cards page with the decks available to edit for this user


@app.route("/classes") #classes page
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
       success = db.createUser(username, password, teacher) #db function to create the user paramters are values for each field
       if success: 
           return redirect(url_for("dashboard")) #return redirect for dashbaord if successfull 
    elif len(username) <= 5:
        return "username must be more than 5 characters"
    elif len(password) <= 7:
        return "password must be more than 7 characters"
    elif password != repassword:
        return "passwords and repassword do not match"  # user feedback based upon invalid form received 
    
    


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


@app.route('/learn/<int:deck_id>')
def learn_deck(deck_id):
    dbh = DatabaseHandler()
    cards = dbh.get_flashcards(deck_id) #retrieve the decks available for a user 
    # simple index-based navigation
    try:
        index = int(request.args.get('i', 0)) 
    except ValueError:
        index = 0
    if not cards:
        return "No cards in this deck." #validation if there are no cards inside of the deck return feedbac to user 
    card = cards[index % len(cards)]
    return render_template('learn_deck.html', card=card, deck_id=deck_id, index=index, total=len(cards))


@app.route('/edit-cards/<int:deck_id>', methods=['GET', 'POST'])
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


@app.route('/edit-cards/<int:deck_id>/delete/<int:card_id>', methods=['POST'])
def delete_card(deck_id, card_id):
    dbh = DatabaseHandler()
    dbh.delete_flashcard(card_id)
    return redirect(url_for('manage_deck', deck_id=deck_id))


@app.route('/classes/create', methods=['POST'])
def create_class():
    dbh = DatabaseHandler()
    name = request.form.get('name')
    subject = request.form.get('subject')
    dbh.create_deck(name, subject, user_id=1)
    return redirect(url_for('classes'))


db = DatabaseHandler()

app.run(debug = True)