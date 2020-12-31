from datetime import datetime, timezone
import CryptoPredict
import time
import csv
import kraken
import threading
import psutil
import os
import sklearn
import sys
import json
from guppy import hpy


class ThreadedTrader:
    def __init__(self, pair, headers, retrain_every, initial_investment):
        self.headers = headers
        self.fiat = initial_investment
        self.initial_investment = initial_investment
        self.crypto = 0
        self.pair = pair
        self.filename = self.getFilename(pair)
        self.retrain_every = retrain_every*60
        self.k_trader = kraken.KrakenTrader()
        self.predictor = CryptoPredict.CryptoPredictor(lookback=1,
                                                       epochs=13,
                                                       units=256,
                                                       batch_size=1,
                                                       pair=pair,
                                                       cutpoint=2400,
                                                       important_headers=headers,
                                                       verbose=1)
        self.current_df = self.predictor.createFrame()
        self.smallest_size = 1800
        self.total_net = 0
        self.start_time = datetime.now()
        self.log_path = 'logs/' + \
            self.start_time.strftime("%m-%d-%Y_%H-%M-%S")+'.csv'

        # reset file
        headers = ['unix', 'action', 'price ({})'.format(self.pair[0]), 'balance ({})'.format(
            self.pair[1]), 'balance ({})'.format(self.pair[0]), 'valuation ({})'.format(self.pair[1]), 'total net (%)', 'uptime', 'dataset size']

        with open('logs/current_log.csv', 'w+') as filename:
            writer = csv.writer(filename)
            writer.writerow(headers)

        with open(self.log_path, 'w+') as filename:
            writer = csv.writer(filename)
            writer.writerow(headers)

    def logToCSV(self, row):
        '''
        Logs diagnostics to file.
        '''
        with open('logs/current_log.csv', 'a') as filename:
            writer = csv.writer(filename)
            writer.writerow(row)

        with open(self.log_path, 'a') as filename:
            writer = csv.writer(filename)
            writer.writerow(row)

    def getFilename(self, pair):
        '''
        Gets the appropiate filename given a pair.
        '''
        return 'data/'+'-'.join(pair)+'_kraken.csv'

    def getFees(self):
        '''
        Gets the fees for each exchange (no longer needed).
        '''
        # open file with json of fees and return dict of fees for the prices keys
        with open('data/fees.json', 'r') as jfees:
            self.fees = json.loads(jfees.read())
        return self.fees

    def checkMemory(self, heapy=False):
        '''
        Checks size of memory and prints it in MB.
        '''
        process = psutil.Process(os.getpid())
        # in bytes
        print(
            '* Using {:.2f} MB of memory\n'.format(process.memory_info().rss/(1024*1024)))
        if heapy:
            h = hpy()
            print(h.heap())

    # write threading here using threads and futures
    def checkRetrainLoop(self):
        '''
        Checks to see whether or not the model needs to be retrained.
        '''
        # RETRAIN
        last_time_trained = 0
        while True:
            if ((time.time() - last_time_trained) > self.retrain_every or last_time_trained == 0) and len(self.current_df) >= self.smallest_size:
                last_time_trained = time.time()
                print('* Retraining model ...\n')
                self.predictor.retrainModel(self.current_df)

            if last_time_trained != 0:
                print('Last model trained at', self.k_trader.utc_to_local(
                    datetime.utcfromtimestamp(last_time_trained)))
            else:
                print('Model not trained yet ...')
            print('')
            time.sleep(10)

    def saveLoop(self):
        '''
        Saves the latest price for the currency to the csv file, applies the model, and makes a decision.
        Will later be modified to trade as well.
        '''
        while True:
            try:
                self.k_trader.saveTickerPair(self.pair)
            except:
                print('api call failed...trying again in 5')
                time.sleep(5)
                self.k_trader.saveTickerPair(self.pair)

            self.current_df = self.predictor.createFrame()  # re update frame

            try:
                if len(self.current_df) >= self.smallest_size:
                    current_model = self.predictor.loadModel()
                    # only do this once it can verify last 2400 CONTINUOUS DATA
                    decision = self.predictor.decideAction(
                        self.current_df, current_model)

                    # buy or sell here
                    current_price = self.current_df.iloc[-1][self.headers['price']]
                    crypto_value = self.fiat/current_price  # in crypto
                    dollar_value = self.crypto*current_price  # in usd

                    if decision == 'buy' and self.fiat >= dollar_value:
                        self.crypto = self.crypto + crypto_value
                        self.fiat = self.fiat - self.crypto*current_price
                        print(
                            '+ Balance:\n  + {:.2f} {}\n  + {:.8f} {}\n   (bought)'.format(
                                self.fiat, self.pair[1].upper(), self.crypto, self.pair[0].upper()))
                    elif decision == 'sell' and self.crypto >= crypto_value:
                        self.fiat = self.fiat + dollar_value
                        self.crypto = self.crypto - self.fiat/current_price
                        print(
                            '+ Balance:\n  + {:.2f} {}\n  + {:.8f} {}\n   (sold)'.format(
                                self.fiat, self.pair[1].upper(), self.crypto, self.pair[0].upper()))
                    else:
                        print(
                            '+ Balance:\n  + {:.2f} {}\n  + {:.8f} {} (valued at {:.2f} USD)\n   (holding)'.format(
                                self.fiat, self.pair[1].upper(), self.crypto, self.pair[0].upper(), dollar_value))

                    self.total_net = (((self.fiat/self.initial_investment) +
                                       ((self.crypto*current_price)/self.initial_investment))*100)-100

                    print(
                        '+ Total net: {:.3f}%\n   (since {})\n'.format(self.total_net, self.start_time.replace(microsecond=0)))
                    # end transaction

                    #  save to log
                    row = [datetime.now().replace(microsecond=0), decision, current_price, round(self.fiat, 2),
                           round(self.crypto, 8), (self.crypto*current_price+self.fiat), round(self.total_net, 3), str(datetime.now()-self.start_time)[:-7], len(self.current_df)]
                    self.logToCSV(row)
                    #  end
                else:
                    print(
                        '* Not predicting, dataset not big enough ({} < {})'.format(len(self.current_df), self.smallest_size))
            except sklearn.exceptions.NotFittedError:
                print('* Model not fit yet - waiting til next cycle')

            except UnboundLocalError:
                print('* Model not fit yet - waiting til next cycle')
            except FileNotFoundError as e:
                print(
                    '* Model not found - {} ...'.format(e))

            self.checkMemory()
            time.sleep(8)

    def run(self):
        '''
        Main function.
        '''
        try:
            print('* Initial training ...')
            # self.predictor.retrainModel(self.current_df) ## initialize with retrained model

            print('* Creating savingThread ...')
            savingThread = threading.Thread(target=self.saveLoop)
            print('* Starting savingThread ...')
            savingThread.start()
            print('* Creating retrainingThread ...')
            retrainingThread = threading.Thread(target=self.checkRetrainLoop)
            print('* Waiting 10 seconds ...\n')
            time.sleep(10)
            print('* Starting retrainingThread ...\n')
            retrainingThread.start()
            print('\nGood to go!\n')

        except (KeyboardInterrupt, SystemExit):
            print('* Cancelled')
