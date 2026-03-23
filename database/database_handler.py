import sqlite3 as sql
from database.database_exceptions import nonUniqueUsername
from models.user_models import User


class DatabaseHandler:
    def __init__(self, dbName="flashcard_app.db"):
        self.dbName = dbName

    def connect(self):
        return sql.connect(self.dbName)

    def createTable_users(self):
        with self.connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username CHAR(16) NOT NULL UNIQUE, 
                            Password_hash CHAR(64) NOT NULL,
                            UserType STRING NOT NULL
                            );"""
            )  # creates the user table with specific constraints for fields to fit the websites needs

    def createUser(self, username, password_hash, userType):
        with self.connect() as conn:
            try:
                # This could throw IntegrityError if the username already exists due to the UNIQUE constraint
                conn.execute(
                    "INSERT INTO users (username, Password_hash, UserType) VALUES (?, ?, ?);",
                    (username, password_hash, userType),
                )
                # raise Exception("Simulated database error")  # Simulate a database error for testing purposes
            except sql.IntegrityError as e:
                # if username is not unique, raise a custom exception to be handled by the calling code
                raise nonUniqueUsername()

            conn.commit()  # inserts a new user into the user table

    def createTable_Flashcards(self):
        with self.connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS flashcards (
                            Flashcard_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            Deck_id INTEGER,
                            answer CHAR(255) NOT NULL,
                            question CHAR(255) NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (Deck_id) REFERENCES decks(Deck_id)
                            );"""
            )

    def createTable_Decks(self):
        with self.connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS decks (
                            Deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            Deck_name CHAR(64) NOT NULL,
                            subject CHAR(36) NOT NULL,
                            user_id INTEGER,
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                            );"""
            )

    def createTable_Progress(self):
        with self.connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS progress (
                            Progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            Flashcard_id INTEGER,
                            correct BOOLEAN NOT NULL,
                            incorrect BOOLEAN NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                            FOREIGN KEY (Flashcard_id) REFERENCES flashcards(Flashcard_id)
                            );"""
            )

    def getUser(self, username, password_hash):
        with self.connect() as conn:
            # execute a query to find a user with the provided username and password hash; this is used for authentication during signin
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND Password_hash = ?;",
                (username, password_hash),
            )
            # fetch one row from the result set; if a user is found, this will contain their details; if not, it will be None
            row = cursor.fetchone()
            # if a user is found with the provided username and password hash, return a User object; otherwise, return None
            return User(row[0], row[1], row[2], row[3]) if row else None

    def getUserById(self, user_id):
        with self.connect() as conn:
            # execute a query to find a user with the provided user_id; this is used for authentication during signin
            cursor = conn.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,))
            # fetch one row from the result set; if a user is found, this will contain their details; if not, it will be None
            row = cursor.fetchone()
            # if a user is found with the provided user_id, return a User object; otherwise, return None
            return User(row[0], row[1], row[2], row[3]) if row else None

    def authoriseuser(self, username, password_hash):
        try:
            with self.connect() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username = ? AND Password_hash = ?;",
                    (username, password_hash),
                )
                userdetails = cursor.fetchone()
                print(userdetails)
                return True

        except:
            return False

    def get_decks(self, user_id=None):
        with self.connect() as conn:
            if user_id:
                cursor = conn.execute(
                    "SELECT * FROM decks WHERE user_id = ?;", (user_id,)
                )
            else:
                cursor = conn.execute("SELECT * FROM decks;")
            return cursor.fetchall()


    #function to retrieve a specific deck using its id 
    def get_deck(self, deck_id):
        #connects to databse and uses sql to fetch the deck with assoicated id 
        with self.connect() as conn:
            cursor = conn.execute("SELECT * FROM decks WHERE Deck_id = ?;", (deck_id,))
            return cursor.fetchone()

    # functions for creating a deck 
    def create_deck(self, deck_name, subject, user_id=None):
        with self.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO decks (Deck_name, subject, user_id) VALUES (?, ?, ?);",
                (deck_name, subject, user_id),
            )
            conn.commit()
            return cursor.lastrowid

    #retrieve all flashcards inside a deck using deck_id 
    def get_flashcards(self, deck_id):
        #connects to database and uses sql to fetch all flashcards with assoicated deck_id
        with self.connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM flashcards WHERE Deck_id = ?;", (deck_id,)
            )
            return cursor.fetchall()


    def add_flashcard(self, deck_id, question, answer, user_id=None):
        with self.connect() as conn:
            #
            cursor = conn.execute(
                "INSERT INTO flashcards (user_id, Deck_id, answer, question) VALUES (?, ?, ?, ?);",
                (user_id, deck_id, answer, question),
            )
            conn.commit()
            return cursor.lastrowid

    def update_flashcard(self, flashcard_id, question, answer):
        with self.connect() as conn:
            conn.execute(
                "UPDATE flashcards SET question = ?, answer = ? WHERE Flashcard_id = ?;",
                (question, answer, flashcard_id),
            )
            conn.commit()

    # functions for deletion of a flashcard - will be used in complete edit cards page 
    def delete_flashcard(self, flashcard_id):
        # connects to the database and executes a delete statement
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM flashcards WHERE Flashcard_id = ?;", (flashcard_id,)
            )
            # commits transaction
            conn.commit()

    # utility functions for managing the database, including creating tables, adding users, retrieving users, and managing flashcards and decks.

    def delete_user(self, username):
        with self.connect() as conn:
            conn.execute("DELETE FROM users WHERE username = ?;", (username,))
            conn.commit()
            # deletes a user from the user table based on the provided username

    def reset_usertable(self):
        with self.connect() as conn:
            conn.execute("DROP TABLE IF EXISTS users;")
            self.createTable_users()
            # utility function to reset the user table by dropping it if it exists and then recreating it

    def delete_deck(self, deck_id):
        with self.connect() as conn:
            conn.execute("DELETE FROM decks WHERE Deck_id = ?;", (deck_id,))
            conn.commit()
            # deletes a deck from the decks table based on the provided deck_id


# account management 

    def update_password(self, user_id, current_password, new_password):
        with self.connect() as conn:
            # check the current password matches what is stored
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ? AND Password_hash = ?;",
                (user_id, current_password),
            )
            row = cursor.fetchone()
            if not row:
                return False  # current password is incorrect
            # update to the new password
            conn.execute(
                "UPDATE users SET Password_hash = ? WHERE user_id = ?;",
                (new_password, user_id),
            )
            conn.commit()
            return True

    def delete_account(self, user_id, password):
        with self.connect() as conn:
            # verify the password before deleting
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ? AND Password_hash = ?;",
                (user_id, password),
            )
            row = cursor.fetchone()
            if not row:
                return False  # password is incorrect
            # delete all flashcards belonging to the user first due to foreign key constraints
            conn.execute("DELETE FROM flashcards WHERE user_id = ?;", (user_id,))
            # delete all decks belonging to the user
            conn.execute("DELETE FROM decks WHERE user_id = ?;", (user_id,))
            # delete the user account
            conn.execute("DELETE FROM users WHERE user_id = ?;", (user_id,))
            conn.commit()
            return True