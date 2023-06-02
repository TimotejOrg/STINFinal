from flask import g
from app import app

def test_payment_post_success(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/account/payment/', data={'amount': '100', 'currency': 'USD',
                                                      'paymentAccount': 'test@example.com'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Úspěšná platba'


def test_payment_post_failure(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/account/payment/', data={'amount': '2000', 'currency': 'USD',
                                                      'paymentAccount': 'test@example.com'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Není dostatečný zůstatek pro provedení platby'


def test_deposit_post_success(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/account/deposit/', data={'amount': '500', 'currency': 'czk'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Úspěšný vklad'


def test_deposit_post_failure(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/account/deposit/', data={'amount': '-500', 'currency': 'czk'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Nesprávná částka'


def test_register_post_existing_account(client):
    response = client.post('/register/', data={'firstName': 'John', 'lastName': 'Doe',
                                               'email': 'user@example.com', 'password': 'password',
                                               'currency': 'czk', 'securityAnswer': 'Odpoved'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Váš účet již existuje, přihlaste se, prosím'


def test_register_post_new_account(client):
    response = client.post('/register/', data={'firstName': 'Jane', 'lastName': 'Doe',
                                               'email': 'newuser@example.com',
                                               'password': 'password',
                                               'currency': 'czk', 'securityAnswer': 'Odpoved'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Úspěšně zaregistrováno'


def test_merchant_payment_post_fail_not_enough_money(client):
    with client.session_transaction() as session:
        session['merchant_currency'] = 'usd'

    response = client.post('/merchant-setup/merchant-payment/',
                           data={'amount': '200', 'email': 'test@example.com',
                                 'password': 'password123'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Není dostatečný zůstatek pro provedení platby'


def test_merchant_payment_post_fail_wrong_login(client):
    with client.session_transaction() as session:
        session['merchant_currency'] = 'usd'

    response = client.post('/merchant-setup/merchant-payment/',
                           data={'amount': '10', 'email': 'user@example.com',
                                 'password': 'password'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Přihlašovací údaje jsou nesprávné'


def test_merchant_payment_post_success(client):
    with client.session_transaction() as session:
        session['merchant_currency'] = 'czk'
    response = client.post('/merchant-setup/merchant-payment/',
                           data={'amount': '1', 'email': 'test@example.com',
                                 'password': 'password123'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Úspěšná platba'


def test_merchant_setup_post(client):
    response = client.post('/merchant-setup/',
                           data={'currency': 'usd', 'merchantAccount': 'example@example.com'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/merchant-setup/merchant-payment/'


def test_webhook_wrong_event_type(client):
    response = client.get('/update_server')
    assert response.status_code == 405


def test_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Hlavní stránka</title>" in response.data.decode("utf-8")


def test_register(client):
    response = client.get("/register/")
    assert response.status_code == 200
    assert "<title>Registrační stránka</title>" in response.data.decode("utf-8")


def test_login_correct_login(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/login/', data={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_login_fail_wrong_login(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/login/', data={'email': 'test@example.com', 'password': 'testpasswordwrong'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Přihlašovací údaje jsou nesprávné'


def test_login(client):
    response = client.get("/login/")
    assert response.status_code == 200
    assert "<title>Login Page</title>" in response.data.decode("utf-8")


def test_security_question_right_question(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100
    response = client.post('/security-question/', data={'securityAnswer': 'answer123'})
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_security_question_wrong_question(client):
    with client.session_transaction() as session:
        session['firstName'] = 'John'
        session['lastName'] = 'Doe'
        session['email'] = 'test@example.com'
        session['password'] = 'password123'
        session['currency'] = 'USD'
        session['securityAnswer'] = 'answer123'
        session['balance'] = 100

    response = client.post('/security-question/', data={'securityAnswer': 'random'})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == 'Nesprávná bezpečnostní odpověď'



def test_security_question_no_session(client):
    response = client.get("/security-question/")
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_security_question(client):
    with client.session_transaction() as session:
        session['currency'] = 'czk'
        session['securityAnswer'] = 'Odpoved'
        session['balance'] = 0

    with app.app_context():
        g.currency = 'czk'
        g.securityAnswer = 'Odpoved'
        g.balance = 0

        response = client.get("/security-question/")
        assert response.status_code == 200
        assert "<title>Bezpečnostní otázka</title>" in response.data.decode("utf-8")


def test_account_post(client):
    response = client.post("/account/")
    assert response.status_code == 405


def test_account_no_session(client):
    response = client.get("/account/")
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_account(client):
    with client.session_transaction() as session:
        session['currency'] = 'czk'
        session['securityAnswer'] = 'Odpoved'
        session['balance'] = 0

    with app.app_context():
        g.currency = 'czk'
        g.securityAnswer = 'Odpoved'
        g.balance = 0

        response = client.get("/account/")
        assert response.status_code == 200
        assert "<title>Účet</title>" in response.data.decode("utf-8")


def test_bank_statement_no_session(client):
    response = client.get("/account/bank-statement/")
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_bank_statement_2_transactions(client, monkeypatch):
    def mock_get_transactions():
        # Return a list of dummy transactions for testing
        return [
            (1, "user@example.com", "payment", 100, "czk", 1000, "2023-06-01 10:00:00"),
            (2, "user@example.com", "withdrawal", 50, "czk", 950, "2023-06-02 12:00:00"),
        ]
    monkeypatch.setattr("app.get_transactions", mock_get_transactions)
    with client.session_transaction() as session:
        session['currency'] = 'czk'
        session['securityAnswer'] = 'Odpoved'
        session['balance'] = 0
    with app.app_context():
        g.currency = 'czk'
        g.securityAnswer = 'Odpoved'
        g.balance = 0
        response = client.get("/account/bank-statement/")
        assert response.status_code == 200
        assert "<title>Bankovní výpis</title>" in response.data.decode("utf-8")


def test_bank_statement_no_transactions(client, monkeypatch):
    def mock_get_transactions():
        # Return a list of dummy transactions for testing
        return []
    monkeypatch.setattr("app.get_transactions", mock_get_transactions)
    with client.session_transaction() as session:
        session['currency'] = 'czk'
        session['securityAnswer'] = 'Odpoved'
        session['balance'] = 0
    with app.app_context():
        g.currency = 'czk'
        g.securityAnswer = 'Odpoved'
        g.balance = 0
        response = client.get("/account/bank-statement/")
        assert response.status_code == 200
        assert "<title>Bankovní výpis</title>" in response.data.decode("utf-8")


def test_deposit_post(client):
        with client.session_transaction() as session:
            session['firstName'] = 'John'
            session['lastName'] = 'Doe'
            session['email'] = 'test@example.com'
            session['password'] = 'password123'
            session['currency'] = 'USD'
            session['securityAnswer'] = 'answer123'
            session['balance'] = 100
        response = client.post("/account/deposit/", data={'amount': '100', 'currency': 'USD', })
        assert response.status_code == 200
        assert response.data.decode("utf-8") == 'Úspěšný vklad'



def test_deposit_no_session(client):
    response = client.get("/account/deposit/")
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_deposit(client):
    with client.session_transaction() as session:
        session['currency'] = 'czk'
        session['securityAnswer'] = 'Odpoved'
        session['balance'] = 0
    with app.app_context():
        g.currency = 'czk'
        g.securityAnswer = 'Odpoved'
        g.balance = 0
        response = client.get("/account/deposit/")
        assert response.status_code == 200
        assert "<title>Vkládat na účet</title>" in response.data.decode("utf-8")


def test_payment_no_session(client):
    response = client.get("/account/payment/")
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_payment(client):
    with client.session_transaction() as session:
        session['currency'] = 'czk'
        session['securityAnswer'] = 'Odpoved'
        session['balance'] = 0
    with app.app_context():
        g.currency = 'czk'
        g.securityAnswer = 'Odpoved'
        g.balance = 0
        response = client.get("/account/payment/")
        assert response.status_code == 200
        assert "<title>Platba</title>" in response.data.decode("utf-8")


def test_merchant_payment_no_session(client):
    response = client.get("/merchant-setup/merchant-payment/")
    assert response.status_code == 302
    assert "<title>Redirecting...</title>" in response.data.decode("utf-8")


def test_merchant_payment(client):
    with client.session_transaction() as session:
        session['merchant_currency'] = 'czk'
    with app.app_context():
        g.merchant_currency = 'czk'
        response = client.get("/merchant-setup/merchant-payment/")
        assert response.status_code == 200
        assert "<title>Platba u obchodníka</title>" in response.data.decode("utf-8")


def test_merchant_setup(client):
    response = client.get("/merchant-setup/")
    assert response.status_code == 200
    assert "<title>Platba u obchodníka</title>" in response.data.decode("utf-8")
