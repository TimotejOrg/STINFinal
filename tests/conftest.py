import sqlite3
import pytest
from flask import Flask
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
    return app.test_client()
