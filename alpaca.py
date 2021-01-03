import alpaca_trade_api as alpaca
import pandas
import os
import json

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'


class AlpacaTrader:
    def __init__(self, paper=True):
        api_key = open('keys/alpaca_public').read().strip()
        api_secret = open('keys/alpaca_private').read().strip()
        base_url = 'https://paper-api.alpaca.markets'
        if paper:
            base_url = 'https://api.alpaca.markets'
        # or use ENV Vars shown below
        self.api = alpaca.REST(api_key, api_secret,
                               base_url=base_url, api_version='v2')
        # obtain account information

    def cleanup(self, filename, how_far_back):
        '''
        Cleans up the file so it doesn't overflow memory.
        '''

        whole_file = pandas.read_csv(filename)
        whole_file = whole_file.drop_duplicates()
        whole_file.to_csv(filename, index=False)
        num_lines = sum(1 for line in open(filename))
        if num_lines > how_far_back:
            end = num_lines-how_far_back

            parsed = whole_file.drop(list(range(0, end)))
            parsed.to_csv(filename, index=False)
            # drop early rows and then rewrite NOT APPEND

    def saveTickerPair(self, ticker):
        '''
        Saves latest price to file.
        '''

        quote = self.api.get_last_quote(ticker.upper()).__dict__['_raw']
        print(quote)
        filename = 'data/'+ticker+'_alpaca.csv'
        if not os.path.isfile(filename):
            header = list()
            for i in quote.items():
                header.append(i[0])
            print(header)
            pandas.DataFrame([header]).to_csv(
                filename, mode='a', header=False, index=False)

        dropped = list()
        for i in quote.values():
            dropped.append(i)

        pandas.DataFrame([dropped]).to_csv(
            filename, mode='a', header=False, index=False)
        self.cleanup(filename, 4096)
        return pandas.DataFrame([dropped])

    def test(self):
        tsla = self.api.get_last_quote('TSLA')
        print(self.saveTickerPair('TSLA'))


if __name__ == '__main__':
    tester = AlpacaTrader()
    tester.test()
