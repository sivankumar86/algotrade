



def roc(dfp):
    dfp['roc'] = round(((dfp['close'] - dfp['close'].shift(5)) / dfp['close'].shift(5)) * 100)
    dfp['roctradel'] = dfp.apply(lambda row:  row['roc'] < -2, axis=1)
    dfp['roctrades'] = dfp.apply(lambda row:  row['roc'] > 2, axis=1)
    return dfp


def hammer(dfp):
    dfp['hammer'] = dfp.apply(
        lambda row: row['roc'] < 0 and row['close'] - row['low'] > (2 * (row['open'] - row['close'])) and row['high'] - row['open'] < (
                    0.5 * (row['open'] - row['close'])) if row['open'] > row['close'] else row['open'] - row['low'] > (
                    1.5 * (row['close'] - row['open'])) and row['high'] - row['close'] < (0.5 * (row['close'] - row['open'])),
        axis=1)
    return dfp

def shootingStar(dfp):
    dfp['shooting'] = dfp.apply(
        lambda row: row['roc'] > 0 and row['high'] - row['open'] > (2 * (row['open'] - row['close'])) and row['close'] - row['low'] < (
                    0.5 * (row['open'] - row['close'])) if row['open'] > row['close'] else row['high'] - row['open'] > (
                    1.5 * (row['close'] - row['open'])) and row['close'] - row['low'] < (0.5 * (row['close'] - row['open'])),
        axis=1)
    return dfp
