import sqlite3
from flask import Flask, render_template, request, redirect
from form_checks import *
import git

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

conn.commit()

app = Flask(__name__)
app.secret_key = "my_secret_key"


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/timotej')

        origin = repo.remotes.origin
        origin.set_url('https://github.com/TimotejOrg/STINFinal.git')

        origin.fetch()
        origin.pull()

        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        registration_info = [request.form['firstName'], request.form['lastName'],
                             request.form['email'], request.form['password'],
                             request.form['currency'], request.form['securityAnswer']]
        if check_registration(registration_info):
            return "Úspěšně zaregistrováno"
        return "Váš účet již existuje, přihlaste se, prosím"
    return render_template('register.html')


@app.route('/merchant-setup/', methods=['GET', 'POST'])
def merchant_setup():
    if request.method == 'POST':
        merchant_setup_info = [request.form['currency'], request.form['merchantAccount']]
        setup_merchant(merchant_setup_info)
        return redirect('/merchant-setup/merchant-payment/')
    return render_template('merchant-setup.html')


@app.route('/merchant-setup/merchant-payment/', methods=['GET', 'POST'])
def merchant_payment():
    if 'merchant_currency' in session:
        if request.method == 'POST':
            merchant_info = [request.form['amount'], request.form['email'],
                             request.form['password']]
            if check_merchant_payment_info(merchant_info) == "True":
                return "Úspěšná platba"
            return check_merchant_payment_info(merchant_info)
        return render_template('merchant-payment.html')
    return redirect('/merchant-setup/')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_info = [request.form['email'], request.form['password']]
        if check_login(login_info):
            return redirect('/security-question/')
        return "Přihlašovací údaje jsou nesprávné"
    return render_template('login.html')


@app.route('/security-question/', methods=['GET', 'POST'])
def security_question():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        if request.method == 'POST':
            security_answer_info = [request.form['securityAnswer']]
            if check_security_answer(security_answer_info):
                return redirect('/account/')
            return "Nesprávná bezpečnostní odpověď"
        return render_template('security-question.html')
    return redirect('/login/')


@app.route('/account/')
def account():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        return render_template('account.html')
    return redirect('/login/')


@app.route('/account/payment/', methods=['GET', 'POST'])
def payment():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        if request.method == 'POST':
            payment_info = [request.form['amount'], request.form['currency'],
                            request.form["paymentAccount"]]
            if check_payment(payment_info) == "True":
                return "Úspěšná platba"
            return check_payment(payment_info)
        return render_template('payment.html')
    return redirect('/login/')


@app.route('/account/deposit/', methods=['GET', 'POST'])
def deposit():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        if request.method == 'POST':
            deposit_info = [request.form['amount'], request.form['currency']]
            if check_deposit(deposit_info) == "True":
                return "Úspěšný vklad"
            return check_deposit(deposit_info)
        return render_template('deposit.html')
    return redirect('/login/')


@app.route('/account/bank-statement/')
def bank_statement():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        # Retrieve the transaction history from the "transactions" table for the current user
        transactions = get_transactions()
        return render_template('bank-statement.html', transactions=transactions)
    return redirect('/login/')


#app.run()
