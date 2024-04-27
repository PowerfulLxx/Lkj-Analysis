import pandas as pd

def brakeTestAtDeparture(df):
    '''
    df: dataframe: '时间' 和 '管压'
    return: 如果进行了制动试验，则返回True，否则返回False
    '''
    df_length = len(df)
    for i in range(df_length):
        for j in range(i + 1, df_length):
            if df.loc[i, '管压'] - df.loc[j, '管压'] > 100 \
                           and (df.loc[i, '时间'] - df.loc[j, '时间']).total_seconds() <= -60:
                print('不存在始发站制动机未试验')
                return True
    return False