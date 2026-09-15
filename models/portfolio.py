

class portfolio:
    def __init__(self, name):
        self.name = name
        self.positions = {}

    def add_position(self, ticker, shares, purchase_price):
        ticker = ticker.upper()
        if ticker in self.positions:
            self.positions[ticker]['shares'] += shares
            self.positions[ticker]['purchase_price'] = purchase_price
        else:
            self.positions[ticker] = {'shares': shares, 'purchase_price': purchase_price}

    def remove_position(self, ticker):
        ticker = ticker.upper()
        if ticker in self.positions:
            del self.positions[ticker]
        else:
            print("Position for " + ticker + " does not exist in the portfolio.")
    
