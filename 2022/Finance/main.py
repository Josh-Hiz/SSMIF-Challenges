import pandas_datareader as dr
import pandas as pd
import numpy as np
import yfinance as yf
from scipy import stats


yf.pdr_override()

# Names of individual stocks
cocacolaStock = 'KO'
spdrStock = 'SPY'
teslaStock = 'TSLA' 


#Data frame for Coca-Cola
cocaData = dr.get_data_yahoo(cocacolaStock, start='2021-01-01', end='2021-12-31')

#Data frame for Tesla and SPY to use for CAPM
capmData = dr.get_data_yahoo([teslaStock,spdrStock], start='2021-01-01', end='2021-12-31', interval ='m') # We need to set the interval to monthly for beta & alpha values

#Individual data frame for tesla for statistics
teslaData = dr.get_data_yahoo(teslaStock, start='2021-01-01', end='2021-12-31')

def statistics():
    '''statistics will take the mean daily returns and volatility of the stocks for coca cola and tesla and calculate their statistical differences using a t-test'''
    significance_level = 0.05
    
    #Set rolling window size
    window_size = 5
    
    #Make modifiable dataframe variables
    tesla = teslaData
    cc = cocaData
    
    #Get the required data from Coca-Cola
    cc['Daily_Returns'] = cc['Close'].pct_change() 
    cc['Daily_Volatility'] = cc['Daily_Returns'].rolling(window_size).std()
    
    #Get the required data from Tesla
    tesla['Daily_Returns'] = tesla['Close'].pct_change() 
    tesla['Daily_Volatility'] = tesla['Daily_Returns'].rolling(window_size).std() 

    #Drop unneeded data, only keep daily returns and volatility
    cc = cc.drop(['High','Low','Open','Close','Volume','Adj Close'], axis = 1)
    tesla = tesla.drop(['High','Low','Open','Close','Volume','Adj Close'], axis = 1)
    
    #Give ID's to cc and tesla and set thier index
    cc['ID'] = 'KO'
    cc.set_index("ID", inplace=True)
    tesla['ID'] = 'TSLA'
    tesla.set_index("ID", inplace=True)
    
    #Concat the data frames into table
    frames = [cc,tesla]
    table = pd.concat(frames, ignore_index=False,axis=0)
    
    #Drop N/A values
    table = table.dropna()
    
    #Query the data for the daily returns of Coca-Cola and Tesla
    returnKO = table.query('ID == "KO"')['Daily_Returns']
    returnTSLA = table.query('ID == "TSLA"')['Daily_Returns']
    
    #Query the data for the daily volatilities of Coca-Cola and Tesla
    volKO = table.query('ID == "KO"')['Daily_Volatility']
    volTSLA = table.query('ID == "TSLA"')['Daily_Volatility']

    #Reassign table to groupby the ID of the stock and describe the data
    table = table.groupby('ID').describe()
    #Print out the table to display data
    print(table.to_string())

    # Perform a 2 sample T-Test on the mean daily returns assuming equal variance
    ttestReturns, pReturns = stats.ttest_ind(returnKO, returnTSLA, equal_var=True)
    
    #Perform a 2 sample T-Test on the mean daily volitilities assuming equal variance
    ttestVol, pVol = stats.ttest_ind(volKO, volTSLA, equal_var=True)
    

    #Print and explain results
    print("\n a). To test for the significant difference in mean daily returns, I used a 2 sample T-Test with a \n     significance level of 0.05. To do this test, I am assuming that the returns are of equal variance, \n     have a normal distribution, and are independent and identically distributed. \n")
    print("     p-value: " + str(pReturns) + '\n')
    print("     result: due to the fact that the p-value is much greater than the significance level of 0.05, the rejection \n     of the null hypothesis has failed, meaning that there it is extremely likely that there is \n     no significant difference between the mean daily returns of Coca-Cola and Tesla")

    print("\n b). To test for the significant difference in mean daily volatilities, I used a 2 sample T-Test with a \n     significance level of 0.05. To do this test, I am assuming that the returns are of equal variance, \n     have a normal distribution, and are independent and identically distributed. \n")
    print("     p-value: " + str(pVol) + '\n')
    print("     result: due to the fact that the p-value is extremely small compared to the significance level, the rejection \n     of the null hypothesis has succeeded, meaning that there it is extremely likely that there is \n     a significant difference between the mean daily volatilities of Coca-Cola and Tesla")

def metrics():
    '''metrics returns the volatility, VaR, Sharpe Ratio, Downside Deviation, and Maximum Drawdown from the stock Coca-Cola (KO)'''
    #Find annual volatility of coca-cola stock by creating a log returns table to provide a column of logs so we can calculate annual standard deviation
    cocaData['Log returns'] = np.log(cocaData['Close']/cocaData['Close'].shift())
    volatility = cocaData['Log returns'].std() * np.sqrt(252)
    print("a). Volatility is a statistical measure of the dispersion of data around its mean over a certain period of time. \n    It's calculated as the standard deviation multiplied by the square root of the number of trading days (In this case 252). \n    In finance, it represents this dispersion of market prices, on an annualized basis. \n    The volatility for Coca-Cola is: " + str(volatility) + '\n' )

    #Find 95% Value at Risk (VaR) by calculating the daily returns and then call the quantile function at 0.05 for 95% confidence
    cocaData['Daily Returns'] = cocaData.Close.pct_change()
    cocaData.dropna()
    #Sort values in ascending order
    cocaData.sort_values('Daily Returns', inplace=True,ascending=True)
    VaR_95 = cocaData['Daily Returns'].quantile(0.05)
    print("b). Value at Risk (VaR) is a statistic that is used in risk management to predict the greatest possible losses over \n    some sort of time interval. There are many methods to calculate VaR and I used the Historical Simulation Approach. \n    VaR is commonly used in investment and commercial banks to deterime the extent and probability of potential losses in portfolios. \n    The VaR for Coca-Cola is: " + str(VaR_95) + "\n")
    
    #Find Sharpe Ratio by taking the average value of all the log returns from coca cola 
    sharpe_ratio = (cocaData['Log returns'].mean()/cocaData['Log returns'].std()) * np.sqrt(255)
    print("c). Sharpe Ratio compares the return of an investment with its risk (Volatility). \n    The ratio divides a portfolio's excess returns by a measure of its volatility to assess \n    risk-adjusted performance. The Sharpe Ratio for Coca-Cola calulated is: " + str(sharpe_ratio) + "\n")

    #Calculate Downside deviation
    
    #For downside deviation, I set an arbitrary MAR (minimal acceptable return) of 20%, this is high but it is arbitrary to yeild a substantial and understandable result as the risk free rate for 2021 averaged 0.0138 (0.008)
    MAR = (0.20 * 100) # Convert to a percentage
    
    #Grab the daily returns for 2021 and set it to its own variable
    dailyReturns = cocaData['Daily Returns']
    #Calculate the annual return for 252 trading days and convert to a percentage 
    annualReturn = (dailyReturns.mean() * 252) * 100
    #Periods being examined, since it is one year it will be one
    periods = 1
    #Calculate downside deviation using the formula: sqrt(Annual return - MAR)^2 / periods, however the periods being examined is just 2021, so periods would equal 1
    downsideDeviation = np.sqrt(((annualReturn - MAR)**2) / periods) / 100
    print("d). Downside deviation is a measure of price volatility, or how stable it is over time. It goes over the \n    the returns over time and calculates how likely they are too fall below average return. Downside \n    deviation is helpful to avoid highly volatile stocks over time. To calculate DSD, you need to set a \n    minmal accepted return value (MAR), subtract that value from the annual return of the stock, only \n    keep the negatives, sum them and then square the result, and divide by the number of periods. \n    The MAR used was 20% because it would yeild a clear and explanable result. \n    The downside deviation calculated is: " + str(downsideDeviation) + "\n")
    
    #Calculate the maximum drawdown, assuming that the prompt is asking for daily max drawdown
    rollMax = cocaData['Adj Close'].rolling(5, min_periods=1).max()
    dailyDrawdown = cocaData['Adj Close']/rollMax - 1.0
    maxDrawdown = dailyDrawdown.rolling(5, min_periods=1).min()
    print("e). The maximum daily drawdown measures the maximum fall in the value of an assest/stock/investment, \n    it is provided by the difference between the value of the lowest trough to its highest peak. \n    MDD is calculated over a long time period, in tis case the year of 2021 and cannot be greater than zero. \n    The Max Daily Drawdown is provided by the data below in the table: ")
    print(maxDrawdown)
    print("The greatest drawdown was: " + str(maxDrawdown.min()))
    
def capm():
    '''capm returns the beta and alpha values for the stock os tesla TSLA during the year of 2021, the S&P 500 index will be used which has a beta of 1.0'''
    
    #Calculate beta for tesla in which I only require Adj Close
    teslaClose = capmData['Adj Close']
    
    #Grab the log returns for tesla
    logReturns = np.log(teslaClose/teslaClose.shift())
    
    #Covarience
    cov = logReturns.cov()
    #Variance using SPY
    var = logReturns['SPY'].var()
    #Calculate the beta
    beta = cov.loc['TSLA','SPY']/var
    
    #Market and risk free return as of 2021
    riskFreeReturn = 0.0138
    marketReturn = 0.105
    
    #Calculate the expected return using the CAPM formula
    expectedReturn = riskFreeReturn + beta*(marketReturn - riskFreeReturn)
    #Due to the usage of the CAPM formula, the alpha formula is alpha = return - risk free return - beta * (the market return - risk free return) and therefore be zero
    alpha = expectedReturn - riskFreeReturn - beta*(marketReturn - riskFreeReturn)
    
    print("a). The beta of a stock is a measure of a stocks volatility in relation to the overall market. High-beta stocks are much riskier but provide \n    a higher return potential. Low beta stocks pose less risk but also lower returns. a beta above 1 is more volatile \n    than the market but expect higher return. A beta below 1 has a lower stock volatility, and expects less return. \n    The beta for Tesla is: " + str(beta) + '\n')
    print("b). The alpha measures the amount that the investment has returned in comparison to the market index or any other broad benchmark its compared \n    Alpha generally shows how well or poor a stock has performed in comparison to the benchmark. Generally high alphas \n    are always preferred. Due to the fact I am using a Capital Asset Pricing Model, the formula for alpha used is the \n    return - risk free rate - the beta * (expected market return - risk free rate), the alpha yeilded is zero, \n    therefore the alpha of Tesla is: " + str(alpha) + ". An alpha of zero means that the stock has performed in line with the market. ")

#Main method to make printing more formatted 
def main():
    #Print the answers to console
    statistics()
    print('--------------------------------------------------------------------------------------------------------------------------------')
    metrics()
    print('--------------------------------------------------------------------------------------------------------------------------------')
    capm()
    
if __name__ == "__main__":
    #Call main to print everything
    main()