from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/merchant-payment/')
def merchant_payment():
    return render_template('merchant-payment.html')


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/security-question/')
def security_question():
    return render_template('security-question.html')


@app.route('/account/')
def account():
    return render_template('account.html')


@app.route('/account/deposit/')
def deposit():
    return render_template('deposit.html')


@app.route('/account/bank-statement/')
def bank_statement():
    return render_template('bank-statement.html')


app.run()
