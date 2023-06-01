import pytest
from unittest.mock import patch
from flask import session
from form_checks import check_payment, can_use_draft, get_balance, get_transactions, convert_currency, \
    check_registration, setup_merchant, check_merchant_payment_info, check_login, check_security_answer, check_deposit


@pytest.fixture
def mock_session():
    session['email'] = 'test@example.com'
    session['balance'] = 100.0
    yield session
    session.pop('email', None)
    session.pop('balance', None)


def test_check_payment(mock_session):
    # Test case where new_balance >= 0
    payment_info = [50.0, 'USD']
    expected_result = "True"
    assert check_payment(payment_info) == expected_result

    # Test case where 0 > new_balance >= 0 - (current_balance * 0.1)
    payment_info = [200.0, 'EUR']
    expected_result = "True"
    assert check_payment(payment_info) == expected_result

    # Test case where new_balance < 0 - (current_balance * 0.1)
    payment_info = [500.0, 'JPY']
    expected_result = "Není dostatečný zůstatek pro provedení platby"
    assert check_payment(payment_info) == expected_result

    # Test case where orig_payment_amount <= 0
    payment_info = [0.0, 'USD']
    expected_result = "Nesprávná částka"
    assert check_payment(payment_info) == expected_result


def test_can_use_draft():
    current_balance = 100.0

    # Test case where new_balance >= 0 - (current_balance * 0.1)
    payment_amount = 10.0
    assert can_use_draft(current_balance, payment_amount) is True

    # Test case where new_balance < 0 - (current_balance * 0.1)
    payment_amount = 150.0
    assert can_use_draft(current_balance, payment_amount) is False


def test_get_balance(mock_session):
    expected_balance = 100.0
    assert get_balance() == expected_balance


def test_get_transactions():
    # Assuming a setup with test transactions in the database
    expected_transactions = [('test@example.com', 'payment', 50.0, 'USD', 50.0),
                             ('test@example.com', 'deposit', 100.0, 'EUR', 150.0)]
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchall.return_value = expected_transactions
        assert get_transactions() == expected_transactions


def test_convert_currency():
    # Test case where conversion is successful
    from_currency = 'USD'
    to_currency = 'EUR'
    amount = 50.0
    with patch('form_checks.CurrencyConverter') as mock_currency_converter:
        mock_converter = mock_currency_converter.return_value
        mock_converter.convert.return_value = 40.0
        assert convert_currency(from_currency, to_currency, amount) == 40.0

    # Test case where conversion fails
    from_currency = 'JPY'
    to_currency = 'EUR'
    amount = 100.0
    with patch('form_checks.CurrencyConverter') as mock_currency_converter:
        mock_converter = mock_currency_converter.return_value
        mock_converter.convert.side_effect = Exception("Conversion error")
        with patch('form_checks.CurrencyRates') as mock_currency_rates:
            mock_rates = mock_currency_rates.return_value
            mock_rates.convert.return_value = 120.0
            assert convert_currency(from_currency, to_currency, amount) == 120.0


def test_check_registration():
    # Test case where registration info is for a new user
    registration_info = ['John', 'Doe', 'john@example.com', 'password', 'USD', 'answer']
    expected_result = True
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = None
        assert check_registration(registration_info) == expected_result

    # Test case where registration info is for an existing user
    registration_info = ['John', 'Doe', 'john@example.com', 'password', 'USD', 'answer']
    expected_result = False
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = ('John', 'Doe', 'john@example.com')
        assert check_registration(registration_info) == expected_result


def test_setup_merchant(mock_session):
    merchant_setup_info = ['EUR', 'account_number']
    setup_merchant(merchant_setup_info)
    assert session['merchant_currency'] == 'EUR'
    assert session['merchant_account'] == 'account_number'


def test_check_merchant_payment_info():
    merchant_info = [50.0, 'test@example.com', 'password']

    # Test case where provided email and password match a user in the database
    expected_result = "True"
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = ('John', 'Doe', 'test@example.com', 'password',
                                             'USD', 'answer', 100.0)
        assert check_merchant_payment_info(merchant_info) == expected_result

    # Test case where provided email and password do not match any user in the database
    expected_result = "Přihlašovací údaje jsou nesprávné"
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = None
        assert check_merchant_payment_info(merchant_info) == expected_result


def test_check_login():
    login_info = ['test@example.com', 'password']

    # Test case where provided email and password match a user in the database
    expected_result = True
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = ('John', 'Doe', 'test@example.com', 'password',
                                             'USD', 'answer', 100.0)
        assert check_login(login_info) == expected_result
        assert session['firstName'] == 'John'
        assert session['lastName'] == 'Doe'
        assert session['email'] == 'test@example.com'
        assert session['password'] == 'password'
        assert session['currency'] == 'USD'
        assert session['securityAnswer'] == 'answer'
        assert session['balance'] == 100.0

    # Test case where provided email and password do not match any user in the database
    expected_result = False
    with patch('form_checks.sqlite3') as mock_sqlite3:
        mock_connection = mock_sqlite3.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = None
        assert check_login(login_info) == expected_result


def test_check_security_answer():
    security_answer = 'answer'

    # Test case where provided security answer matches the user's security answer in the session
    expected_result = True
    with patch('form_checks.session') as mock_session:
        mock_session.get.return_value = 'answer'
        assert check_security_answer(security_answer) == expected_result

    # Test case where provided security answer does not match the user's security answer in the session
    expected_result = False
    with patch('form_checks.session') as mock_session:
        mock_session.get.return_value = 'different_answer'
        assert check_security_answer(security_answer) == expected_result


def test_check_deposit(mock_session):
    # Test case where deposit amount is greater than 0
    deposit_info = ['100.0', 'USD']
    expected_result = "True"
    assert check_deposit(deposit_info) == expected_result

    # Test case where deposit amount is not a positive number
    deposit_info = ['-50.0', 'USD']
    expected_result = "Nesprávná částka"
    assert check_deposit(deposit_info) == expected_result

    # Test case where deposit amount is not a valid number
    deposit_info = ['abc', 'USD']
    expected_result = "Nesprávná částka"
    assert check_deposit(deposit_info) == expected_result

    # Test case where deposit amount is 0
    deposit_info = ['0.0', 'USD']
    expected_result = "Nesprávná částka"
    assert check_deposit(deposit_info) == expected_result



def test_main():
    # result = main()
    # assert result == render_template('main.html')
    pass


def test_check_registration():
    # result = check_registration(['Timotej', 'Fasiang', 'timotej.fasiang@tul.cz',
    # '~9Dw3f#)ti4aEgV', 'CZK', 'Otazka', 'Odpoved']) assert result is False result =
    # check_registration(['Ti', 'Fa', 'timo.fasg@tu', 'i4aEgV', 'CZK', 'Odp']) assert result is True
    pass


def test_check_merchant_payment_info():
    # result = check_merchant_payment_info([100, 'email', 'password'])
    # assert result == "Přihlašovací údaje jsou nesprávné"
    # result = check_merchant_payment_info([0, 'timotej.fasiang@tul.cz', '~9Dw3f#)ti4aEgV'])
    # assert result == "Nesprávná částka"
    pass


def test_check_login():
    # result = check_login(['email', 'password'])
    # assert result is False
    # result = check_login(['timotej.fasiang@tul.cz', '~9Dw3f#)ti4aEgV'])
    # assert result is True
    pass


def test_check_security_answer():
    # result = check_security_answer(['randomAnswer'])
    # assert result is False
    pass


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
