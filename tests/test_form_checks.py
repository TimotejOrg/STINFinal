import pytest
from form_checks import *
from flask import g, Flask, session
from app import app


@pytest.fixture()
def create_app():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS transactions")
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                firstName text, 
                lastName text,
                email text,
                password text,
                currency text,
                securityAnswer text,
                balance integer
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userEmail TEXT,
                transactionType TEXT,
                amount REAL,
                currency TEXT,
                balance REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
    c.execute(
        "INSERT INTO users (firstName, lastName, email, password, currency, securityAnswer, "
        "balance)"
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ['John', 'Doe', 'test@example.com', 'password123', 'USD', 'answer123', 100])
    c.execute("INSERT INTO transactions (userEmail, transactionType, amount, currency, balance) "
              "VALUES (?, ?, ?, ?, ?)", ['test@example.com', 'deposit', 100, 'USD', 100])
    c.execute("INSERT INTO transactions (userEmail, transactionType, amount, currency, balance) "
              "VALUES (?, ?, ?, ?, ?)", ['test@example.com', 'withdraw', 50, 'USD', 50])
    conn.commit()
    app = Flask(__name__)
    app.secret_key = "my_secret_key"
    yield app


@pytest.fixture()
def client(create_app):
    with create_app.test_client() as client:
        with create_app.app_context():
            yield client


def test_check_payment(client):
    with client.session_transaction() as session:
        session['email'] = 'test@example.com'
        session['balance'] = 100
        session['currency'] = 'USD'
    # Send a dummy request to trigger the Flask request context
    client.get('/')
    # Test case 1: Successful payment with sufficient funds
    payment_info = ['10', 'USD']
    with app.app_context():
        result = check_payment(payment_info)
    assert result == "True"  # The payment should be successful
    # Test case 2: Successful payment with sufficient funds (10% overdraft allowed)
    payment_info = ['99', 'USD']
    with app.app_context():
        result = check_payment(payment_info)
    assert result == "True"  # The payment should be successful
    # Test case 3: Failed payment due to insufficient funds
    payment_info = ['200', 'USD']
    with app.app_context():
        result = check_payment(payment_info)
    assert result == "Není dostatečný zůstatek pro provedení platby"  # The payment should fail due to insufficient funds
    # Test case 4: Failed payment due to invalid payment amount
    payment_info = ['-50', 'USD']
    with app.app_context():
        result = check_payment(payment_info)
    assert result == "Nesprávná částka"  # The payment should fail due to an invalid payment amount

def test_check_registration(client):
    # Test case 1: Successful registration
    registration_info = ['New', 'Prson', 'random@example.com', 'password', 'USD', 'Answer']
    with app.app_context():
        result = check_registration(registration_info)
    assert result is True  # The registration should be successful
    # Test case 2: Failed registration due to existing user with the same name
    registration_info = ['John', 'Doe', 'some@example.com', 'password', 'USD', 'Answer']
    with app.app_context():
        result = check_registration(registration_info)
    assert result is False  # The registration should fail due to an existing user with the same name
    # Test case 3: Failed registration due to existing user with the same email
    registration_info = ['random', 'testsa', 'test@example.com', 'password', 'USD', 'Answer']
    with app.app_context():
        result = check_registration(registration_info)
    assert result is False  # The registration should fail due to an existing user with the same email


def test_check_merchant_payment_info(client):
    # Test case 1: Successful payment
    merchant_info = ['10', 'test@example.com', 'password123']
    with client.session_transaction() as session:
        session['merchant_currency'] = 'USD'
    # Send a dummy request to trigger the Flask request context
    client.get('/')
    with app.app_context():
        result = check_merchant_payment_info(merchant_info)
    assert result == "True"  # The payment should be successful
    # Test case 2: Failed payment due to incorrect credentials
    merchant_info = ['100', 'test@example.com', 'wrong_password']
    with app.app_context():
        result = check_merchant_payment_info(merchant_info)
    assert result == "Přihlašovací údaje jsou nesprávné"  # The payment should fail with incorrect credentials
    # Test case 3: Failed payment due to insufficient funds
    merchant_info = ['200', 'test@example.com', 'password123']
    with app.app_context():
        result = check_merchant_payment_info(merchant_info)
    assert result == "Není dostatečný zůstatek pro provedení platby"  # The payment should fail due to insufficient funds
    # Test case 4: Failed payment due to an invalid amount
    merchant_info = ['-50', 'test@example.com', 'password123']
    with app.app_context():
        result = check_merchant_payment_info(merchant_info)
    assert result == "Nesprávná částka"  # The payment should fail with an invalid amount
    # Test case 6: Successful payment triggering the 10% interest condition
    merchant_info = ['99', 'test@example.com', 'password123']
    with app.app_context():
        result = check_merchant_payment_info(merchant_info)
    assert result == "True"  # The payment should be successful with a 10% interest applied to the new balance


def test_check_deposit(client):
    deposit_info = ['100', 'USD']
    with client.session_transaction() as session:
        session['email'] = 'test@example.com'
        session['balance'] = 100
        session['currency'] = 'USD'
    # Send a dummy request to trigger the Flask request context
    client.get('/')
    with app.app_context():
        result = check_deposit(deposit_info)
    assert result == "True"  # The deposit should be successful
    deposit_info = ['10', 'EUR']
    with app.app_context():
        result = check_deposit(deposit_info)
    assert result == "True"  # The deposit should be successful
    # Modify the deposit_info to simulate a failed deposit
    deposit_info = ['-50', 'USD']
    with app.app_context():
        result = check_deposit(deposit_info)
    assert result == "Nesprávná částka"  # The deposit should fail with an incorrect amount


def test_check_login(client):
    login_info = ['test@example.com', 'password123']
    # Send a dummy request to trigger the Flask request context
    client.get('/')
    with app.app_context():
        result = check_login(login_info)
    assert result is True  # The login should be successful
    login_info = ['test@example.com', 'wrong_password']
    with app.app_context():
        result = check_login(login_info)
    assert result is False  # The login should fail


def test_check_security_answer(client):
    security_answer_info = ['my_security_answer']
    with client.session_transaction() as session:
        session['securityAnswer'] = 'correct_answer'
    # Send a dummy request to trigger the Flask request context
    client.get('/')
    with app.app_context():
        result = check_security_answer(security_answer_info)
    assert result is False  # The provided security answer does not match the one in the session
    with client.session_transaction() as session:
        session['securityAnswer'] = 'my_security_answer'
    # Send another dummy request to trigger the Flask request context
    client.get('/')
    with app.app_context():
        result = check_security_answer(security_answer_info)

    assert result is True  # The provided security answer matches the one in the session


def test_setup_merchant(client):
    merchant_setup_info = ['USD', '123456789']
    with client.session_transaction() as session:
        session['merchant_currency'] = 'USD'
        session['merchant_account'] = '123456789'

    # Send a dummy request to trigger the Flask request context
    client.get('/')

    with app.app_context():
        setup_merchant(merchant_setup_info)

        # Assert that the session variables are properly set
        assert session['merchant_currency'] == merchant_setup_info[0]
        assert session['merchant_account'] == merchant_setup_info[1]


def test_get_transactions(client):
    email = 'test@example.com'
    with client.session_transaction() as session:
        session['email'] = email
    # Send a dummy request to trigger the Flask request context
    client.get('/')
    with app.app_context():
        result = get_transactions()
    assert len(result) == 2  # There are 2 transactions for the test user in the DB


def test_draft_check():
    result = can_use_draft(10, 11)
    assert result is True
    result = can_use_draft(10, 12)
    assert result is False
    result = can_use_draft(10, 9)
    assert result is True
    result = can_use_draft(10, 0)
    assert result is True
    result = can_use_draft(0, 0)
    assert result is True
    result = can_use_draft(0, 10)
    assert result is False
    result = can_use_draft(-10, 0)
    assert result is False
    result = can_use_draft(-10, 1)
    assert result is False


def test_currency_conversion():
    result = convert_currency('CZK', 'EUR', 1)
    assert result < 1
    result = convert_currency('CZK', 'USD', 1)
    assert result < 1
    result = convert_currency('CZK', 'CZK', 1)
    assert result == 1
    result = convert_currency('CZK', 'EUR', 0)
    assert result == 0

    result = convert_currency('EUR', 'CZK', 1)
    assert result > 1
    result = convert_currency('EUR', 'USD', 1)
    assert result > 1
    result = convert_currency('EUR', 'EUR', 1)
    assert result == 1
    result = convert_currency('EUR', 'CZK', 0)
    assert result == 0

    result = convert_currency('USD', 'CZK', 1)
    assert result > 1
    result = convert_currency('USD', 'EUR', 1)
    assert result < 1
    result = convert_currency('USD', 'USD', 1)
    assert result == 1
    result = convert_currency('USD', 'CZK', 0)
    assert result == 0
