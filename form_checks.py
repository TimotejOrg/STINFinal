import sqlite3
from flask import session
from forex_python.converter import CurrencyRates
from currency_converter import CurrencyConverter


def check_payment(payment_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # update user's balance
    c.execute("SELECT balance FROM users WHERE email=?", [session['email']])
    session['balance'] = c.fetchone()[0]
    orig_payment_amount = float(payment_info[0])
    currency = payment_info[1]
    current_balance = session['balance']
    try:
        payment_amount = convert_currency(currency, session['currency'], float(orig_payment_amount))
    except:
        return "Směnné kurzy měn v současné době nejsou k dispozici, zkuste to později"
    new_balance = current_balance - payment_amount
    if orig_payment_amount > 0:
        if new_balance >= 0:
            # Update the user's balance in the database
            c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, session['email']))
            c.execute("INSERT INTO transactions (userEmail, transactionType, amount, currency, "
                      "balance) "
                      "VALUES (?, 'payment', ?, ?, ?)",
                      (session['email'], orig_payment_amount, currency, round(new_balance, 2)))
            conn.commit()
            return "True"  # Funds successfully removed
        if new_balance >= 0 - (current_balance * 0.1):
            # Update the user's balance in the database
            c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, session['email']))
            c.execute("INSERT INTO transactions (userEmail, transactionType, amount, currency, "
                      "balance) "
                      "VALUES (?, 'payment', ?, ?, ?)",
                      (session['email'], orig_payment_amount, currency, round(new_balance, 2)))
            conn.commit()
            return "True"  # Funds successfully removed
        return "Není dostatečný zůstatek pro provedení platby"  # False  # Insufficient funds
    return "Nesprávná částka"


def can_use_draft(current_balance, payment_amount):
    new_balance = current_balance - payment_amount
    return bool(new_balance >= 0 - (current_balance * 0.1))


def get_balance():
    return session['balance']


def get_transactions():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE userEmail=?", [session['email']])
    return c.fetchall()


def convert_currency(from_currency, to_currency, amount):
    try:
        c = CurrencyConverter()
        return c.convert(amount, from_currency.upper(), to_currency.upper())
    except:
        c = CurrencyRates()
        return c.convert(from_currency.upper(), to_currency.upper(), amount)


def check_registration(registration_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    first_name = registration_info[0]
    last_name = registration_info[1]
    email = registration_info[2]

    # Check if a user with the same first and last name already exists in the database
    c.execute("SELECT * FROM users WHERE firstName=? AND lastName=? AND email=?", (first_name,
                                                                                   last_name,
                                                                                   email))
    existing_user = c.fetchone()

    if existing_user:
        return False  # User with the same name already exists
    # Insert the new user into the database
    c.execute("INSERT INTO users (firstName, lastName, email, password, currency, "
              "securityAnswer, balance) "
              "VALUES (?, ?, ?, ?, ?, ?, 0)", registration_info)
    conn.commit()
    return True  # User registration successful


def setup_merchant(merchant_setup_info):
    session['merchant_currency'] = merchant_setup_info[0]
    session['merchant_account'] = merchant_setup_info[1]


def check_merchant_payment_info(merchant_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    orig_payment_amount = float(merchant_info[0])
    email = merchant_info[1]
    password = merchant_info[2]
    # Check if the provided email and password match a user in the database
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    if user is not None:  # email and password match a specific user
        user_currency = user[4]
        current_balance = user[6]
        try:
            payment_amount = convert_currency(session['merchant_currency'], user_currency,
                                              float(orig_payment_amount))
        except:
            return "Směnné kurzy měn v současné době nejsou k dispozici, zkuste to později"
        new_balance = current_balance - payment_amount
        if orig_payment_amount > 0:
            if new_balance >= 0:
                # Update the user's balance in the database
                c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, email))
                c.execute("INSERT INTO transactions (userEmail, transactionType, amount, "
                          "currency, balance) "
                          "VALUES (?, 'payment', ?, ?, ?)",
                          (email, orig_payment_amount, session['merchant_currency'],
                           round(new_balance, 2)))
                conn.commit()
                return "True"  # Funds successfully removed
            if new_balance >= 0 - (current_balance * 0.1):
                new_balance = new_balance * 1.1
                # Update the user's balance in the database
                c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, email))
                c.execute("INSERT INTO transactions (userEmail, transactionType, amount, "
                          "currency, balance) "
                          "VALUES (?, 'payment', ?, ?, ?)",
                          (email, orig_payment_amount, session['merchant_currency'],
                           round(new_balance, 2)))
                conn.commit()
                return "True"

            return "Není dostatečný zůstatek pro provedení platby"
        return "Nesprávná částka"
    return "Přihlašovací údaje jsou nesprávné"


def check_login(login_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    email = login_info[0]
    password = login_info[1]

    # Check if the provided login (email) and password match a user in the database
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    if user:
        # Get all account info for current session
        session['firstName'] = user[0]
        session['lastName'] = user[1]
        session['email'] = user[2]
        session['password'] = user[3]
        session['currency'] = user[4]
        session['securityAnswer'] = user[5]
        session['balance'] = user[6]
        return True  # Login successful
    return False  # Login failed


def check_security_answer(security_answer_info):
    # Check if the provided security answer matches the one associated with the current session
    return bool(session['securityAnswer'] == security_answer_info[0])


def check_deposit(deposit_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # update user's balance
    c.execute("SELECT balance FROM users WHERE email=?", [session['email']])
    session['balance'] = c.fetchone()[0]

    orig_deposit_amount = deposit_info[0]
    deposit_currency = deposit_info[1]
    try:
        deposit_amount = convert_currency(deposit_currency, session['currency'],
                                          float(orig_deposit_amount))
    except:
        return "Směnné kurzy měn v současné době nejsou k dispozici, zkuste to později"
    new_balance = session['balance'] + deposit_amount
    if float(deposit_info[0]) > 0:
        # Update the user's balance in the database
        c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, session['email']))
        c.execute("INSERT INTO transactions (userEmail, transactionType, amount, currency, balance)"
                  "VALUES (?, 'deposit', ?, ?, ?)",
                  (session['email'], orig_deposit_amount, deposit_currency, round(new_balance, 2)))
        conn.commit()
        return "True"
    return "Nesprávná částka"
