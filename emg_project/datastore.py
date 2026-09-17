from sqlite3 import connect, IntegrityError
from hashlib import pbkdf2_hmac
from os import urandom

def create_database():
    connection = connect("user_database.db")
    cursor_object = connection.cursor()

    cursor_object.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "username TEXT UNIQUE NOT NULL,"
        "hashed_password TEXT NOT NULL,"
        "recent_login_datetime TEXT)")
    # commit saves the transaction, permanently
    connection.commit()
    connection.close()
    return

def hash_password(inputted_password):
    password_bytes = inputted_password.encode("utf-8")
    salt = urandom(16)

    key_stretch = pbkdf2_hmac("sha256", password_bytes, salt, 600000)
    # `hashlib.pbkdf2_hmac`produces 256 bits, bcs of sha256 method...
    store_value = salt.hex() + key_stretch.hex()
    # 32 hex chars salt + 64 hex chars k-stretch
    return store_value

def verify_password(stored_hex_value, inputted_password):
    stored_salt  = stored_hex_value[:32]
    stored_value = stored_hex_value[32:]

    salt_bytes = bytes.fromhex(stored_salt)
    password_bytes = inputted_password.encode("utf-8")

    key_stretch = pbkdf2_hmac("sha256", password_bytes, salt_bytes, 600000)

    if key_stretch.hex() != stored_value:
        flag = False
    else:
        flag = True
    return flag

def create_user(username, inputted_password):
    password_hash = hash_password(inputted_password)

    connection = connect("user_database.db")
    cursor_object = connection.cursor()
    try:
        cursor_object.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (username, password_hash))
        connection.commit()
        flag = True
    except IntegrityError: # triggered if `insert` violates a database constraint ie. if the `username` is not `unique`
        flag = False
    connection.close()
    return flag

def get_all_users():
    connection = connect("user_database.db")
    cursor_object = connection.execute("SELECT username FROM users")

    usernames = []
    for row in cursor_object:
        usernames.append(row[0])

    connection.close()
    return usernames

def authenticate_user(username, inputted_password):
    connection = connect("user_database.db")
    cursor_object = connection.cursor()
    cursor_object.execute("SELECT username, hashed_password FROM users WHERE username = ?", (username,))
    # intentional tuple, to avoid input mistaken as a list of characters...

    user_info = None
    
    for row in cursor_object:
        user_info = row
    connection.close()

    if user_info is None:
        return None
    
    stored_password = user_info[1]
    valid_check = verify_password(stored_password, inputted_password)

    if valid_check == True:
        return user_info[0] 
    # returns; username str
    else:
        return None

def update_login_time(recent_login, username):
    connection = connect("user_database.db")
    cursor_object = connection.cursor()
    cursor_object.execute("UPDATE users SET recent_login_datetime=? WHERE username = ?", (recent_login, username))

    connection.commit()
    connection.close()
    return