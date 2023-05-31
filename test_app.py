import pytest
from form_checks import *


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
