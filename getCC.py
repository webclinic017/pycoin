import requests, json, datetime
#using crypto compare

#load api_key
def loadKey(filename):
    global cc_key
    with open(filename, 'r') as key:
        cc_key = key.read()

def getExchanges(filename, key):
    try:
        exc = requests.get('https://min-api.cryptocompare.com/data/exchanges/general?'+
                            key).json()['Data']
        with open(filename, 'w') as outfile:
            json.dump(exc, outfile)
        return exc
    except:
        return -1    

def getPrices(currency, exchanges, key): #returns dictionary
    summation = {}
    for exc in exchanges:
        call = 'https://min-api.cryptocompare.com/data/price?fsym='+currency+'&tsyms=USD&e='+exc+'&api_key='+cc_key
        print('Asking for',currency,'on '+exc+'...')
        try:
            recieved = requests.get(call).json()['USD']
        except:
            recieved = 'NA'
        summation[exc] = recieved
    return summation

def printj(js):
    print(json.dumps(js, indent=2))

# use cryptocompare to GET the data
# use individual apis for each exchange ugh

if __name__ == '__main__':
    loadKey('keys/cryptocompare')
    exchanges = ['binanceusa','bittrex', 'kraken', 'bitfinex', 'bitstamp', 'gemini']
    prices = getPrices('BTC',exchanges, cc_key)
    print('At',datetime.datetime.now())
    printj(prices)
    # code fees for each exchange in a json file