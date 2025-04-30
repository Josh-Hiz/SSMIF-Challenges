# Name: Joshua Hizgiaev

# You may not import any additional libraries for this challenge besides the following
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf

class PortfolioAnalysis:
    """
    Create a constructor that reads in the excel file and calls all necessary methods
    You may set the output of these methods to be attributes of the class that you may
    access later on in other challenges.

    Create a method called `clean_data` which accurately deals with any discrepancies
    in the input data and returns usable data that you can access for the rest of your tasks
    You must have comments explaining why you chose to make any of the changes you did. Any
    missing (NA) values must be calculated for or found from yfinance accordingly.
    The cleaned data should be exported to an excel file with 3 sheets, all of the same format
    as the original data. The file name should be called `cleaned_data.xlsx`.
    
    #NOTE:
    You may import and use this cleaned data file for any of the optional challenges, as needed.
    You may also import this file and create an instance of the PortfolioAnalysis class to use
    in any of the optional challenges, as needed.

    Create a method called `asset_value` that calculates the total market value of each equity
    in the portfolio at the end of the month, with tickers in the rows and dates in the columns
    as well as another row that keeps track of the portfolio's Net Asset Value (NAV) at the end
    of each month. If there is no position for a certain equity during a given month, its value
    should be 0. This data should be kept track of from the end of June to the end of September

    Create a method called `unrealized_returns` that calculates the unrealized returns of each stock.
    The output should be a dataframe that has tickers in the rows, dates in the columns, and the
    unrealized gain/loss of each ticker at the end of each month.
    If there is no unrealized loss to be calculated for a given stock during a given month, its
    value should be 0.

    Create a method called `plot_portfolio` that builds a plot of the portfolio's value over time,
    from the end of June to the end of September

    Create a method called `plot_liquidity` that builds a plot of the ratio between the cash on
    hand and the portfolio's total value, from the end of June to the end of September
    """  
    
    # Before begining I want to lay out all assumptions I am making for a given data set so its better to understand my code from a programming perspective:
    # Firstly is I am assuming that all quantities are valid integers as otherwise the row would need to be removed
    # Secondly is I am assuming the cash row will always be at the bottom of a given excel sheet
    # Thirdly is I am assuming that the unit and market for cash will always be 1
    # Fourth is I am assuming that when plotting the portfolio and liquidity ratio that a PNG file must be generated.
    # Due to some of the assumptions above, I did not find the use of numpy or datetime to be necessary.
    
    # I also want to make an additonal note, due to ease of codability I simply used the portfolio's inital value for the end of june for only
    # the plotting functions, the reason I did this was for pure simplicity, the universal strategy would be in the clean_data function just add
    # a new sheet to the excel file that simply consisted of the cash row and the inital value of the portfolio.
    
    def __init__(self,data):
        # Read in the excel file and convert it to a dictionary of dataframes
        self.data = pd.read_excel(data, sheet_name=None)
        # Clean the data
        self.clean_data()
        # Calculate the asset values and store in a attribute
        self.asset_values = self.asset_value()
        # Calculate the unrealized returns and store in a attribute
        self.unrealized_pnl = self.unrealized_returns()

    def clean_data(self):
        """
        Clean data will go through every sheet in the excel file that was converted to a dataframe dictionary 
        and inspect all data in the quantity, MarketPrice, and UnitCost columns. If there is a string in any value
        then it will be appropriatly stripped and converted to a floating point value. If there is an NA value in the 
        MarketPrice column then it will be replaced with the current price of the stock using yfinance. If there is an
        NA value in the UnitCost column then it will be replaced with the calculated unit cost. The formula used to calculate
        the unit cost is (MarketPrice / Quantity) * 100. After all the data is cleaned, the dictionary will be exported to an excel file
        "cleaned_data.xlsx". 
        """
        for sheet in self.data:
            for i in range(len(self.data[sheet])):
                for j in range(2, 4):
                    # If a value is found to have a string in it, strip the string and convert it to a float rounded to 2 digits
                    # to normalize all values in the data set and reduce the rounding error as much as possible, the problem with 
                    # converting to float is sometimes it will produce small a rounding error that can be discounted. The reason
                    # I do not check quantity for errors is because if quantity is any value other than a valid integer then it 
                    # would not be in the portfolio in the first place, the only other option would be to delete that row entirely
                    # but I am assuming that all quantities will be valid.
                    if isinstance(self.data[sheet].iloc[i, j], str) and self.data[sheet].iloc[i, j] != "NA":
                        self.data[sheet].iloc[i, j] = float(self.data[sheet].iloc[i, j].strip('"').strip('+'))
                    # Check if its NA and the column is MarketPrice
                    elif pd.isna(self.data[sheet].iloc[i, j]) and j == 3:
                        # Get the current price of the stock using yfinance to be used as the most recent market price
                        self.data[sheet].iloc[i, j] = yf.Ticker(self.data[sheet].iloc[i, 0]).history(period='1d')['Close'].iloc[0]
                    # Check if its NA and the column is UnitCost
                    elif pd.isna(self.data[sheet].iloc[i,j]) and j == 2:
                        # Calculate the unit cost by dividing the market price by the total number of shares and then multiplying by 100
                        self.data[sheet].iloc[i, j] = (self.data[sheet].iloc[i, 3] / self.data[sheet].iloc[i, 1]) * 100
                    self.data[sheet].iloc[i, j] = round(self.data[sheet].iloc[i, j], 2)
                        
        # export the dictionary to an excel file
        with pd.ExcelWriter('cleaned_data.xlsx') as writer:
            for sheet in self.data:
                self.data[sheet].to_excel(writer, sheet_name=sheet, index=False)
    
    def asset_value(self):
        """
        asset_value will go through every sheet in the excel file that was converted to a dataframe dictionary 
        and calculate the market value of each stock present in the portfolio. It will then calculate the net asset value
        and store it sequentially by date in a dataFrame. The dataFrame will then be returned. All nan values are zero.
        """
        # Have a resulting dataFrame to store a result
        result = pd.DataFrame()
        # Add the default column for end of june to the result dataFrame
        result['2023-06-30'] = 0
        # Go through every excel sheet in data
        for sheet in self.data:
            # Go from 0 to len of sheet - 1 because the last row is the cash row
            for i in range(len(self.data[sheet])-1):
                # market_value = quantity * market_price
                market_value_of_stock = self.data[sheet].iloc[i, 1] * self.data[sheet].iloc[i, 3]
                # get the name of the current stock
                curr_stock = self.data[sheet].iloc[i, 0]
                # place the market value of the stock in the result dataFrame
                result.loc[curr_stock, sheet] = market_value_of_stock
                
            # Calculate the net asset value by adding the sum of all the market values of the stocks to the cash on hand and divide by the total quantity
            nav = round((result[sheet].sum() + self.data[sheet].iloc[-1, 1]) / (self.data[sheet]['Quantity'].sum()),2)
            # Place the net asset value in the result dataFrame
            result.loc['Net Asset Value', sheet] = nav
        # Set a index name for the result dataFrame
        result.index.name = 'Ticker'
        # Fill all nan values with 0
        result.fillna(0, inplace=True)
        return result
    
    def unrealized_returns(self):
        """
        unrealized_returns will go through every sheet in the excel file that was converted to a dataframe dictionary and 
        calculate the unrealized returns of each stock. It will then store the result in a dataFrame and return it. All nan
        values will be zero.
        """
        # Have a resulting dataFrame to store a result
        result = pd.DataFrame()

        # Go through every excel sheet in data
        for sheet in self.data:
            # Go from 0 to len of sheet - 1 because the last row is the cash row
            for i in range(len(self.data[sheet]) - 1):
                # unrealized_return = market_price - unit_cost, place the result in the result dataFrame
                result.loc[self.data[sheet].iloc[i, 0], sheet] = self.data[sheet].iloc[i, 3] - self.data[sheet].iloc[i, 2]
        # Set a index name for the result dataFrame
        result.index.name = "Ticker"
        # Fill all nan values with 0
        result.fillna(0, inplace=True)
        return result
            
    def plot_portfolio(self):
        """
        plot_portfolio will output and save a matplotlib plot in a PNG file of the portfolio value over time. The portfolio
        value is simply calculated as the sum of all the market values of the stocks without the net asset value. Whilst the 
        x-axis is just the date of the month for the given portfolio performance.
        """
        # The portfolio starts with 200,000 dollars at the end of june, so that is the starting value of the portfolio
        portfolio_value = [200000]
        # Go through every month in the asset_values dataFrame
        dates = ["2023-06-30"]
        for month in self.asset_values.columns[1:]:
            # Calculate the portfolio value by summing all the market values of the stocks, add the cash on hand, and subtract the net asset value
            portfolio_value.append(self.asset_values[month][:].sum() - self.asset_values[month]['Net Asset Value'] + self.data[month].iloc[-1, 1])
            # Get the date of the month
            dates.append(month)
        # plot the portfolio value over time
        plt.plot(dates, portfolio_value)
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value")
        plt.title("Portfolio Value Over Time")
        plt.grid()
        plt.gcf().set_size_inches(15, 10)
        plt.savefig("portfolio_value_over_time.png")
        plt.cla()
        
    def plot_liquidity(self):
        """
        plot_liquidity will output and save a matplotlib plot in a PNG file of the liquidity value over time. The liquidity
        value is simply calculated as the sum of all assets in the portfolio + cash on hand divided by the current cash on hand. Whilst the 
        x-axis is just the date of the month for the given liquidity.
        """
        # initial portfolio value is ratio of cash to total portfolio value, so 200,000 / 200,000 = 1
        ratio = [1]
        dates = ["2023-06-30"]
        # get a list of all cash on hand values
        cash = []
        for sheet in self.data: 
            cash.append(self.data[sheet].iloc[-1, 1])
        # go through every month in the asset_values dataFrame
        for i in range(1, len(self.asset_values.columns)):
            # calculate the ratio of cash on hand to total portfolio value
            ratio.append((self.asset_values[self.asset_values.columns[i]][:].sum()-self.asset_values[self.asset_values.columns[i]]['Net Asset Value'] + cash[i-1]) / cash[i-1])
            # get the date of the month
            dates.append(self.asset_values.columns[i])
            
        # plot the portfolio value over time
        plt.plot(dates, ratio)
        plt.xlabel("Date")
        plt.ylabel("Liqudiity Ratio")
        plt.title("Liquidty Ratio Over Time")
        plt.grid()
        plt.gcf().set_size_inches(10, 5)
        for xy in zip(dates, ratio):
            plt.annotate(f"({round(xy[1], 3)})", xy=xy)
        plt.savefig("liquidity_ratio_over_time.png")
        plt.cla()
            
if __name__ == "__main__":  # Do not change anything here - this is how we will test your class as well.
    fake_port = PortfolioAnalysis("dummy_data.xlsx")
    print(fake_port.asset_values)
    print(fake_port.unrealized_pnl)
    fake_port.plot_portfolio()
    fake_port.plot_liquidity()