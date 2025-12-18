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
                            username cahr(16) NOT NULL UNIQUE,
                            Password_hash CHAR(64) NOT NULL ,
                            UserType BOOLEAN NOT NULL
                            );""")
        

    def createUser(self, username, password_hash, userType):
        with self.connect() as conn:
            conn.execute("INSERT INTO users (username, Password_hash, UserType) VALUES (?, ?, ?);",(username, password_hash, userType))
            conn.commit()
            
        
    def createTable_Flashcards(self):
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS flashcards (
                            Flashcard_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            Deck_id INTEGER,
                            answer CHAR(255) NOT NULL,
                            question CHAR(255) NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                            FOREIGN KEY (Deck_id) REFERENCES decks(Deck_id))
                            ;""")
            
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
            