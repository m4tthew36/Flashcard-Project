from flask import Flask, render_template, request, redirect, url_for
from database import DatabaseHandler


app = Flask(__name__)

@app.route("/") #signin page
def home():
    return render_template("signin.html")


@app.route("/signup") #signup page
def signup():
    return render_template("signup.html")


@app.route("/dashboard") #dashboard page
def dashboard():
    return render_template("dashboard.html")


@app.route("/learn") #learn page
def learn():
    # list available decks to learn from
    dbh = DatabaseHandler()
    # placeholder user id 
    decks = dbh.get_decks(user_id=1)
    return render_template("learn.html", decks=decks)


@app.route("/edit-cards") #edit cards page
def edit_cards():
    dbh = DatabaseHandler()
    decks = dbh.get_decks(user_id=1)
    return render_template("edit_cards.html", decks=decks)


@app.route("/classes") #classes page
def classes():
    dbh = DatabaseHandler()
    decks = dbh.get_decks(user_id=1)
    return render_template("classes.html", decks=decks)

@app.route("/auth/authoriseuser", methods = ["POST"]) #authorise user
def authorize_user():
    formDetials = request.form
    username = formDetials.get("username")
    password = formDetials.get("password")

    db1 = DatabaseHandler()
    Success = db1.getUser(username, password)
    if Success:
        return redirect(url_for("dashboard"))
    
    return "failed to authorise user..."


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
    elif len(username) <= 5:
        return "username must be more than 5 characters"
    elif len(password) <= 7:
        return "password must be more than 7 characters"
    elif password != repassword:
        return "passwords and repassword do not match"
    
    


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
    cards = dbh.get_flashcards(deck_id)
    # simple index-based navigation
    try:
        index = int(request.args.get('i', 0))
    except ValueError:
        index = 0
    if not cards:
        return "No cards in this deck."
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