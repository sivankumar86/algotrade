from broker.samco import login, getindexHistory
import sys

import pandas as pd
from datetime import datetime,timedelta

from algo.CandleCalculation import roc, hammer, shootingStar
from broker.samco import login, getindexHistory, getindexIntraDay, getOptionChain
from utils import email
from utils.Logger import getLogger
from utils.utils import converTopandas, signal, getMonthExpiryDay, get_opSymbol, addDays

holidays=['2021-09-10','2021-10-15','2021-11-05','2021-11-19']
from dateutil.tz import gettz
lastBusDay = datetime.now(tz=gettz('Asia/Kolkata'))
#lastBusDay = datetime.today()
current_date=lastBusDay.strftime('%Y-%m-%d')

table_expire_datetime = lastBusDay + timedelta(days=-1 )

date1 = addDays(days=-2)



start_date=date1.strftime("%Y-%m-%d")
if(start_date in holidays):
    start_date = addDays(days=-3)
    start_day = date1.strftime("%Y-%m-%d")

intra_today='{} 10:00:00'.format(start_day.strftime("%Y-%m-%d"))

credential =login(requestBody=info)
nifty_bank = 'NIFTY BANK'
intra_bank_nifty = getindexIntraDay(nifty_bank, intra_today, credential['sessionToken'])
intra_df = converTopandas(intra_bank_nifty['indexIntraDayCandleData'])

import pandas as pd

def ADX(df):
    def getCDM(df):
        dmpos = df["high"][-1] - df["high"][-2]
        dmneg = df["low"][-2] - df["low"][-1]
        if dmpos > dmneg:
            return dmpos
        else:
            return dmneg

    def getDMnTR(df):
        DMpos = []
        DMneg = []
        TRarr = []
        n = round(len(df) / 10)
        idx = n
        while n <= (len(df)):
            dmpos = df["high"][n - 1] - df["high"][n - 2]
            dmneg = df["low"][n - 2] - df["low"][n - 1]

            DMpos.append(dmpos)
            DMneg.append(dmneg)

            a1 = df["high"][n - 1] - df["high"][n - 2]
            a2 = df["high"][n - 1] - df["close"][n - 2]
            a3 = df["low"][n - 1] - df["close"][n - 2]
            TRarr.append(max(a1, a2, a3))

            n = idx + n

        return DMpos, DMneg, TRarr

    def getDI(df):
        DMpos, DMneg, TR = getDMnTR(df)
        CDM = getCDM(df)
        POSsmooth = (sum(DMpos) - sum(DMpos) / len(DMpos) + CDM)
        NEGsmooth = (sum(DMneg) - sum(DMneg) / len(DMneg) + CDM)

        DIpos = (POSsmooth / (sum(TR) / len(TR))) * 100
        DIneg = (NEGsmooth / (sum(TR) / len(TR))) * 100

        return DIpos, DIneg

    def getADX(df):
        DIpos, DIneg = getDI(df)

        dx = (abs(DIpos - DIneg) / abs(DIpos + DIneg)) * 100

        ADX = dx / 10
        return ADX

    return (getADX(df))


def pandas_rsi(df: pd.DataFrame, window_length: int = 14, output: str = None, price: str = 'close'):
    """
    An implementation of Wells Wilder's RSI calculation as outlined in
    his 1978 book "New Concepts in Technical Trading Systems" which makes
    use of the α-1 Wilder Smoothing Method of calculating the average
    gains and losses across trading periods and the Pandas library.

    @author: https://github.com/alphazwest
    Args:
        df: pandas.DataFrame - a Pandas Dataframe object
        window_length: int - the period over which the RSI is calculated. Default is 14
        output: str or None - optional output path to save data as CSV
        price: str - the column name from which the RSI values are calcuated. Default is 'Close'

    Returns:
        DataFrame object with columns as such, where xxx denotes an inconsequential
        name of the provided first column:
            ['xxx', 'diff', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs', 'rsi']
    """
    # Calculate Price Differences using the column specified as price.
    df['diff'] = df[price].diff(1)

    # Calculate Avg. Gains/Losses
    df['gain'] = df['diff'].clip(lower=0).round(2)
    df['loss'] = df['diff'].clip(upper=0).abs().round(2)

    # Get initial Averages
    df['avg_gain'] = df['gain'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
    df['avg_loss'] = df['loss'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]

    # Calculate Average Gains
    for i, row in enumerate(df['avg_gain'].iloc[window_length+1:]):
        df['avg_gain'].iloc[i + window_length + 1] =\
            (df['avg_gain'].iloc[i + window_length] *
             (window_length - 1) +
             df['gain'].iloc[i + window_length + 1])\
            / window_length

    # Calculate Average Losses
    for i, row in enumerate(df['avg_loss'].iloc[window_length+1:]):
        df['avg_loss'].iloc[i + window_length + 1] =\
            (df['avg_loss'].iloc[i + window_length] *
             (window_length - 1) +
             df['loss'].iloc[i + window_length + 1])\
            / window_length

    # Calculate RS Values
    df['rs'] = df['avg_gain'] / df['avg_loss']

    # Calculate RSI
    df['rsi'] = 100 - (100 / (1.0 + df['rs']))

    # Save if specified
    if output is not None:
        df.to_csv(output)

    return df


df=pandas_rsi(intra_df)
df=ADX(df)

