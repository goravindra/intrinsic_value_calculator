import urllib, sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date

def main():
    #Get stock ticker and discount rate
    ticker, discount = get_user_input()

    #Get Key Ratios from Morningstar
    kr_df = ratios_download(ticker)

    #get book values
    book_values, dividend = get_book_div(ticker, kr_df)

    average_book_change, years = calculate_average_book_change(book_values)

    intrinsic_value = calculate_intrinsic_value(book_values,average_book_change, years, ticker, dividend, discount)

def get_user_input():
    ticker = input('\nEnter stock ticker to research: ')
    discount = float(input('\nEnter discount rate (10y TNote): '))
    return ticker, discount

def ratios_download(ticker):
    #Get key ratios from Morningstar
    try:
        url = 'http://financials.morningstar.com/ajax/exportKR2CSV.html?&callback=?&t='+ticker+'&region=usa&culture=en-US&cur=USD&order=asc'
        kr_df = pd.read_csv(url, skiprows=2, index_col=0)
        #df.to_csv('test.csv')
        return kr_df
    except Exception as e:
        print("------------------------")
        print('Could not find ticker on Morningstar: %s \n' % ticker)
        print('Check ticker spelling and that data exists:\n')
        print(url)
        print('\nError: %s' % e)
        print()
        main()

def get_book_div(ticker, kr_df):
    #Get book value history
    book_values = kr_df.loc['Book Value Per Share * USD']
    print('\nBook Value History')
    print(book_values)

    #Get Dividend History
    dividend_history = kr_df.loc['Dividends USD']

    print('\nDividend History:')
    print(dividend_history)

    #Get user input for expected dividend
    dividend = float(input('\nChoose expected dividend: $'))

    return book_values, dividend

def calculate_average_book_change(book_values):
    #get years over which to calculate average change.
    #remove TTM and initial year
    years = book_values.size-2
    print('\nNumber of years: %i' % years)

    #calculate average book value change
    base = float(book_values[-2]) / float(book_values[0])
    upper = 1 / years
    a = base**upper
    average_book_change = 100 * (a-1)

    print('\nAverage change in book value: %6.2f%% ' % average_book_change)

    #warn if growth company
    if average_book_change >= 15:
        print('Warning - average book value change is high.  Stock may be growth company.  Consider a DCF value calculation')

    return average_book_change, years

def calculate_intrinsic_value(book_values, average_book_change, years, ticker, dividend, discount):

    bv_multiplier = average_book_change/100 + 1

    current_book_value = float(book_values[-1])
    print('\nCurrent Book Value: $%6.2f' % current_book_value)

    base_bv = bv_multiplier ** 10

    parr = base_bv*current_book_value

    discount = discount / 100

    extra = (1+discount)**10

    intrinsic_value = dividend*(1-(1/extra))/discount + parr/extra

    print('\nIntrinsic Value (10-year): $%6.2f \n' % intrinsic_value)


if __name__ == "__main__":

    main()
