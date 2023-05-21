from flask import Flask, render_template, request, redirect
from formChecks import *

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        registration_info = [request.form['firstName'], request.form['lastName'], request.form['email'],
                             request.form['password'], request.form['currency'], request.form['securityAnswer']]
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        currency = request.form['currency']
        security_answer = request.form['securityAnswer']
        print(registration_info)
        if checkRegistration(registration_info):
            return redirect('/login/')
        else:
            return "Registration error"
    else:
        return render_template('register.html')


@app.route('/merchant-payment/', methods=['GET', 'POST'])
def merchant_payment():
    if request.method == 'POST':
        merchant_info = [request.form['amount'], request.form['currency'], request.form['merchantAccount'],
                         request.form['email'], request.form['password']]
        amount = request.form['amount']
        currency = request.form['currency']
        merchant_account = request.form['merchantAccount']
        email = request.form['email']
        password = request.form['password']
        print(merchant_info)
        if checkMerchantInfo(merchant_info):
            return redirect('/')
        else:
            return "Merchant info error"
    else:
        return render_template('merchant-payment.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_info = [request.form['email'], request.form['password']]
        email = request.form['email']
        password = request.form['password']
        print(login_info)
        if checkLogin(login_info):
            return redirect('/login/')
        else:
            return "Login error"
    else:
        return render_template('login.html')


@app.route('/security-question/', methods=['GET', 'POST'])
def security_question():
    if request.method == 'POST':
        security_answer_info = [request.form['securityAnswer']]
        security_answer = request.form['securityAnswer']
        print(security_answer_info)
        if checkSecurityAnswer(security_answer_info):
            return redirect('/login/')
        else:
            return "Security answer error"
    else:
        return render_template('security-question.html')


@app.route('/account/')
def account():
    return render_template('account.html')


@app.route('/account/deposit/', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        deposit_info = [request.form['amount'], request.form['currency']]
        amount = request.form['amount']
        currency = request.form['currency']
        print(deposit_info)
        if checkDeposit(deposit_info):
            return redirect('/account/')
        else:
            return "Deposit error"
    else:
        return render_template('deposit.html')


@app.route('/account/bank-statement/')
def bank_statement():
    return render_template('bank-statement.html')


app.run()
