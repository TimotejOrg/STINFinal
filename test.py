from forex_python.converter import CurrencyRates


def convertCurrency(from_currency, to_currency, amount):
    # Create an instance of the CurrencyRates class
    c = CurrencyRates()
    return c.convert(from_currency.upper(), to_currency.upper(), amount)



print(convertCurrency('eur', 'czk', 100))
