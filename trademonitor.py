import sys

import pandas as pd
from business_calendar import Calendar, MO, TU, WE, TH, FR
from time import time
from datetime import datetime

from algo.CandleCalculation import roc, hammer, shootingStar
from broker.samco import login, getindexHistory, getindexIntraDay, getOptionChain
from utils import email
from utils.Logger import getLogger
from utils.utils import converTopandas, signal, getMonthExpiryDay, get_opSymbol

holidays=['2021-09-10','2021-10-15','2021-11-05','2021-11-19']
cal = Calendar(holidays=holidays)
lastBusDay = datetime.today()
current_date=lastBusDay.strftime('%Y-%m-%d')

date1 = cal.addbusdays(lastBusDay, -1)
date2 = cal.addbusdays(lastBusDay, -20)
date3 = cal.addbusdays(lastBusDay, -300)


today=date1.strftime("%Y-%m-%d")
intra_today='{} 10:00:00'.format(today)

fromdate=date2.strftime("%Y-%m-%d")

tendaybk=date3.strftime("%Y-%m-%d")

logger=getLogger(__name__)



def technicalAnalysis(df):
    df=roc(df)
    df=hammer(df)
    df=shootingStar(df)
    df=signal(df)
    return df


def optionAnalyze(option_chain):
    option_df = pd.json_normalize(option_chain['optionChainDetails'])
    option_df['strikePrice'] = option_df['strikePrice'].astype(float)
    option_df['openInterest'] = option_df['openInterest'].astype(int)
    filter_strike = option_df[(option_df.strikePrice < (intra_close + (intra_close / 10))) & (
                option_df.strikePrice > (intra_close - (intra_close / 10)))]
    filter_strike_CE = filter_strike[filter_strike.optionType == 'CE']
    filter_strike_PE = filter_strike[filter_strike.optionType == 'PE']
    ce_oi = filter_strike_CE['openInterest'].sum()
    pe_oi = filter_strike_PE['openInterest'].sum()
    ce_oi_m = filter_strike_CE['openInterest'].max()
    pe_oi_m = filter_strike_PE['openInterest'].max()
    ce_oi_m_s = filter_strike_CE[filter_strike_CE.openInterest == ce_oi_m]
    pe_oi_m_s = filter_strike_PE[filter_strike_PE.openInterest == pe_oi_m]
    return round(pe_oi / ce_oi, 2),pe_oi_m_s,ce_oi_m_s


def oisignal(opt_symbol,sessionToken,expiry_day=None):
    option_chain = getOptionChain(opt_symbol,sessionToken ,expiry_day);
    oi, pe_m, ce_m = optionAnalyze(option_chain)
    ce_mx=ce_m.strikePrice.item()
    pe_max=pe_m.strikePrice.item()
    status = pd.DataFrame([{"oi": oi, "day": today, "close": intra_close}])
    if (oi < 0.8):
        logger.info("Buy CE and sell PE")
        email.send_email(status.to_html(), "Indian Stock Short PE and Long CE - {}".format(today))
    elif (oi > 1.5):
        email.send_email(status.to_html(), "Indian Stock Short CE and Buy PE- {}".format(today))
        logger.info("Buy PE and sell CE")
    elif (intra_close > (ce_mx-100)):
        email.send_email(status.to_html(), "Indian Stock Short CE Weekly- {}".format(today))
        logger.info(f"Indian Stock Short CE Weekly {oi}")
    elif (intra_close < (pe_max+100)):
        email.send_email(status.to_html(), "Indian Stock Short PE Weekly - {}".format(today))
        logger.info(f"Indian Stock Short PE Weekly {oi}")
    else:
        logger.info(f"no signal from OI {oi}")


if __name__ =='__main__':
    # config.read('conf/app.conf')
    # TODO move hardcoded config
    logger.info("Analyzer Started")
    if(current_date in holidays):
        logger.info("Holiday Today")
        sys.exit(0)
    else:
        nifty_bank = 'NIFTY BANK'
        banknifty = getindexHistory(nifty_bank, fromdate, today, credential['sessionToken'])
        df = converTopandas(banknifty['indexCandleData'])
        df=technicalAnalysis(df)
        today_df=df[df['date']==today]
        intra_bank_nifty = getindexIntraDay(nifty_bank, intra_today, credential['sessionToken'])
        intra_df = converTopandas(intra_bank_nifty['indexIntraDayCandleData'])
        df2 = intra_df.iloc[[-1]]
        intra_close = int(df2['close'].item())
        if(today_df['long'].bool() or today_df['short'].bool()):
            close=round(today_df['ltp'].item())
            details=[]
            if(today_df['long'].bool()):
                if(intra_close > close  and intra_close -close <150):
                    logger.info("short PE")
                    logger.info(f'long : {close}')
                    details.append({"day": today, "close":close})
                    details.append({"day": df2['dateTime'].item(), "close":intra_close})
                    status = pd.DataFrame(details)
                    email.send_email(status.to_html(), "Indian Stock Short PE and Long CE - {}".format(today))
                else:
                    details.append({"day": today, "close": close})
                    details.append({"day": df2['dateTime'].item(), "close": intra_close})
                    status = pd.DataFrame(details)
                    email.send_email(status.to_html(), "Indian Stock Short PE - {}".format(today))
                    logger.info("short PE")
            else:
                if (intra_close < close):
                    details.append({"day": today, "close": close})
                    details.append({"day": df2['dateTime'].item(), "close": intra_close})
                    status = pd.DataFrame(details)
                    email.send_email(status.to_html(), "Indian Stock Short CE - {}".format(today))
                    logger.info("short CE")
        expiry_day=getMonthExpiryDay()
        opt_symbol=get_opSymbol("BANKNIFTY",expiry_day)
        oisignal(opt_symbol,credential['sessionToken'],expiry_day)
        oisignal(opt_symbol,credential['sessionToken'])














