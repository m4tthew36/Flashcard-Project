import sqlite3 as sql


class DatabaseHandler:
    def __init__(self, dbName="flashcard_app.db"):
        self.dbName = dbName

    def connect(self):
        return sql.connect(self.dbName)
    


    def createTable_users(self):
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username CHAR(16) NOT NULL UNIQUE, 
                            Password_hash CHAR(64) NOT NULL,
                            UserType BOOLEAN NOT NULL
                            );""") #creates the user table with specific constraints for fields to fit the websites needs 
        

    def createUser(self, username, password_hash, userType):
        with self.connect() as conn:
            conn.execute("INSERT INTO users (username, Password_hash, UserType) VALUES (?, ?, ?);",(username, password_hash, userType))
            conn.commit() #inserts a new user into the user table 
            
        
    def createTable_Flashcards(self):
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS flashcards (
                            Flashcard_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            Deck_id INTEGER,
                            answer CHAR(255) NOT NULL,
                            question CHAR(255) NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (Deck_id) REFERENCES decks(Deck_id)
                            );""")
            
    def createTable_Decks(self):
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS decks (
                            Deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            Deck_name CHAR(64) NOT NULL,
                            subject CHAR(36) NOT NULL,
                            user_id INTEGER,
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                            );""")        


    def createTable_Progress(self):
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS progress (
                            Progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            Flashcard_id INTEGER,
                            correct BOOLEAN NOT NULL,
                            incorrect BOOLEAN NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                            FOREIGN KEY (Flashcard_id) REFERENCES flashcards(Flashcard_id)
                            );""")
    

    def getUser(self, username, password_hash):
        with self.connect() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE username = ? AND Password_hash = ?;", (username, password_hash))
            user = cursor.fetchone()
            return user

    def authoriseuser(self, username, password_hash):
        try:
            with self.connect() as conn:
                cursor = conn.execute("SELECT * FROM users WHERE username = ? AND Password_hash = ?;", (username, password_hash))
                userdetails = cursor.fetchone()
                print(userdetails)
                return True

        except:
            return False
    
    def get_decks(self, user_id=None):
        with self.connect() as conn:
            if user_id:
                cursor = conn.execute("SELECT * FROM decks WHERE user_id = ?;", (user_id,))
            else:
                cursor = conn.execute("SELECT * FROM decks;")
            return cursor.fetchall()

    def get_deck(self, deck_id):
        with self.connect() as conn:
            cursor = conn.execute("SELECT * FROM decks WHERE Deck_id = ?;", (deck_id,))
            return cursor.fetchone()

    def create_deck(self, deck_name, subject, user_id=None):
        with self.connect() as conn:
            cursor = conn.execute("INSERT INTO decks (Deck_name, subject, user_id) VALUES (?, ?, ?);", (deck_name, subject, user_id))
            conn.commit()
            return cursor.lastrowid

    def get_flashcards(self, deck_id):
        with self.connect() as conn:
            cursor = conn.execute("SELECT * FROM flashcards WHERE Deck_id = ?;", (deck_id,))
            return cursor.fetchall()

    def add_flashcard(self, deck_id, question, answer, user_id=None):
        with self.connect() as conn:
            cursor = conn.execute("INSERT INTO flashcards (user_id, Deck_id, answer, question) VALUES (?, ?, ?, ?);", (user_id, deck_id, answer, question))
            conn.commit()
            return cursor.lastrowid

    def update_flashcard(self, flashcard_id, question, answer):
        with self.connect() as conn:
            conn.execute("UPDATE flashcards SET question = ?, answer = ? WHERE Flashcard_id = ?;", (question, answer, flashcard_id))
            conn.commit()

    def delete_flashcard(self, flashcard_id):
        with self.connect() as conn:
            conn.execute("DELETE FROM flashcards WHERE Flashcard_id = ?;", (flashcard_id,))
            conn.commit()
            