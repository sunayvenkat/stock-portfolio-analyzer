

class Portfolio:
    def __init__(self, name):
        self.name = name
        self.positions = {}

    
    def add_position(self, ticker, shares, purchase_price):

        #Validates that the ticker is a string
        if not isinstance(ticker, str):
            raise TypeError("Ticker symbol must be a string.")

        ticker = ticker.upper().strip()

        if not ticker:
                raise ValueError("Ticker symbol cannot be empty.")

        #Validates that shares is a number bigger than 0
        if not isinstance(shares, (int, float)):
            raise TypeError("Number of shares must be a number.")
        
        if shares <= 0:
            raise ValueError("Number of shares must be greater than zero.")

        #Validates that purchase price is a number bigger than 0
        if not isinstance(purchase_price, (int, float)):
            raise TypeError("Purchase price must be a number.")

        if purchase_price <= 0:
            raise ValueError("Purchase price must be greater than zero.")


        #Takes stock name, number of shares, and purchase price, adding it to the dictionary
        if ticker in self.positions:
            self.positions[ticker]['shares'] += shares
            self.positions[ticker]['purchase_price'] = purchase_price
        else:
            self.positions[ticker] = {
                'shares': shares, 
                'purchase_price': purchase_price
            }

    #Removes a given position
    def remove_position(self, ticker):
        ticker = ticker.upper()
        if ticker in self.positions:
            del self.positions[ticker]
        else:
            print("Position for " + ticker + " does not exist in the portfolio.")

    #Returns dictionary of all stocks in portfolio
    def get_all_positions(self):
        return self.positions

    #Returns indivdual position given a stock ticker
    def get_position(self, ticker):
        ticker = ticker.upper()
        return self.positions.get(ticker)

    #Calculates total cost of portfolio by mutliplying stocks by their purchasing price
    def total_cost(self):
        total = 0
        for position in self.positions.values():
            total += position['shares'] * position['purchase_price']
        return total

    
    
