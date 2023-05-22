import sqlite3


def checkRegistration(registration_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    first_name = registration_info[0]
    last_name = registration_info[1]

    # Check if a user with the same first and last name already exists in the database
    c.execute("SELECT * FROM users WHERE firstName=? AND lastName=?", (first_name, last_name))
    existing_user = c.fetchone()

    if existing_user:
        return False  # User with the same name already exists
    else:
        # Insert the new user into the database
        c.execute("INSERT INTO users (firstName, lastName, email, password, currency, securityAnswer, balance) "
                  "VALUES (?, ?, ?, ?, ?, ?, 0)", registration_info)
        conn.commit()
        return True  # User registration successful


def checkMerchantInfo(merchant_info):
    # TODO: add currency constraints
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    amount = int(merchant_info[0])
    email = merchant_info[3]
    password = merchant_info[4]
    # Check if the provided email and password match a user in the database
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()

    if user:
        current_balance = user[6]
        new_balance = current_balance - amount

        if new_balance >= 0:
            # Update the user's balance in the database
            c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, email))
            conn.commit()
            return True  # Funds successfully removed
        else:
            return "Insufficient funds"  # False  # Insufficient funds
    else:
        return "Login credentials are incorrect"  # False  # Login credentials are incorrect


def checkLogin(login_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    email = login_info[0]
    password = login_info[1]

    # Check if the provided login (email) and password match a user in the database
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()

    if user:
        return True  # Login successful
    else:
        return False  # Login failed


def checkSecurityAnswer(security_answer_info):
    # TODO: this will return true for anyone's security answer, not just the user's security answer
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Check if the provided security answer matches the one associated with the user's email in the database
    c.execute("SELECT * FROM users WHERE securityAnswer=?", security_answer_info)
    user = c.fetchone()

    if user:
        return True  # Security answer is correct
    else:
        return False  # Security answer is incorrect


def checkDeposit(deposit_info):
    # TODO: add currency constraints
    # TODO: add other deposit errors like too many decimals etc.
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if int(deposit_info[0]) > 0:
        return True
    else:
        return False
