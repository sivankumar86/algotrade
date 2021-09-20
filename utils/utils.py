import pandas as pd
from datetime import datetime,timedelta
from dateutil.relativedelta import TH, relativedelta
from dateutil.tz import gettz
from pandas.tseries.offsets import BDay


def converTopandas(tradeDetails):
    '''
    :param tradeDetails:
    :return:
    '''
    dfp = pd.json_normalize(tradeDetails)
    if 'ltp' in dfp:
        dfp['ltp'] = dfp['ltp'].astype(float)
    dfp['low'] = dfp['low'].astype(float)
    dfp['high'] = dfp['high'].astype(float)
    dfp['close'] = dfp['close'].astype(float)
    dfp['open'] = dfp['open'].astype(float)
    dfp['volume'] = dfp['volume'].astype(int)
    return dfp

def signal(dfp):
    dfp['long'] = dfp.apply(lambda row: row['hammer'] , axis=1)
    dfp['short'] = dfp.apply(lambda row: row['shooting'], axis=1)
    return dfp

def getMonthExpiryDay():
    expire_day = datetime.now() + relativedelta(day=31, weekday=TH(-1))
    expiry=expire_day.strftime('%Y-%m-%d')
    return expiry

def addDays(date=datetime.now(tz=gettz('Asia/Kolkata')),days=0):
    return date + BDay(days)


def get_opSymbol(symbol,  expiry):
        month = {
            "01": 'JAN',
            "02": 'FEB',
            "03": 'MAR',
            "04": 'APR',
            "05": 'MAY',
            "06": 'JUN',
            "07": 'JUL',
            "08": 'AUG',
            "09": 'SEP',
            "10": 'OCT',
            "11": 'NOV',
            "12": 'DEC'
        }
        mon = month[expiry[5:7]]
        year = expiry[2:4]
        symbol = symbol.upper()
        return f'{symbol}{year}{mon}'


