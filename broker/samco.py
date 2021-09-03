import requests
import json

def login(requestBody):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    r = requests.post('https://api.stocknote.com/login'
                      , data=json.dumps(requestBody)
                      , headers=headers)

    return r.json()

def getindexHistory(indexName,startdate,enddate,sessionid):
    import requests
    headers = {
        'Accept': 'application/json',
        'x-session-token': '{}'.format(sessionid)
    }

    r = requests.get('https://api.stocknote.com/history/indexCandleData', params={
        'indexName': indexName, 'fromDate': '{}'.format(startdate),'toDate':f'{enddate}'
    }, headers=headers)

    return r.json()


def getindexIntraDay(indexName,startdate,sessionid,minutes=30):
    headers = {
        'Accept': 'application/json',
        'x-session-token': f'{sessionid}'
    }
    r = requests.get('https://api.stocknote.com/intraday/indexCandleData', params={
        'indexName': f'{indexName}', 'fromDate': f'{startdate}','interval':f'{minutes}'
    }, headers=headers)

    return r.json()


def getOptionChain(symbolName,sessionid,expirydate=None):
    headers = {
        'Accept': 'application/json',
        'x-session-token': f'{sessionid}'
    }
    if(expirydate):
        r = requests.get('https://api.stocknote.com/option/optionChain', params={
            'searchSymbolName':  f'{symbolName}', 'exchange': 'NFO','expiryDate': '{}'.format(expirydate)
        }, headers=headers)
    else:
        r = requests.get('https://api.stocknote.com/option/optionChain', params={
            'searchSymbolName': f'{symbolName}', 'exchange': 'NFO'
        }, headers=headers)
    return r.json()

