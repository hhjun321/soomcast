from urllib.request import urlopen
import json
import pandas as pd

def get_degi_data(itemCd, period):
    #result values id
    keys = ['dataTime','seoul','busan','daegu','incheon','gwangju','daejeon'
            ,'ulsan','gyeonggi','gangwon','chungbuk','chungnam','jeonbuk','jeonnam','gyeongbuk','gyeongnam','jeju','sejong']
    
    #airkorea api
    mainurl = 'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/'
    
    #set api request url
    urllist = [
                mainurl + 'getCtprvnMesureLIst?', 'itemCode=',itemCd, "&searchCondition=",period, "&numOfRows=",'30',
                "&dataGubun=", "DAILY", '&ServiceKey=', '9KoytWfk%2B9Gyf9buuTarVdO6z2tD03e8v5JWtlS0Ot6UBfECalPP89BZrBWlcx%2B3Cyx68hKkdrpWk0ogdeFlnQ%3D%3D', '&_returnType=json'
            ]


    url = ''.join(urllist)
    
    #response
    response = urlopen(url).read().decode("utf-8")
    jsondata = json.loads(response)

    
    returndata = dict()
    totalCount = jsondata['totalCount']
    print(totalCount)
    
    #json to dataframe
    for i in range(0, totalCount):
        returndata[str(i)] = dict()
        
        for j in keys:
            returndata[str(i)][j] = jsondata['list'][i-1][j]


    df = pd.DataFrame(returndata)
    
    df.columns = df.loc['dataTime']
    df = df.drop('dataTime')
    
    #set values using cities name
    col_list = df.columns
    lst = []
    for col in col_list:
        city = df[col].index
        value = df[col].values
        n_df = pd.DataFrame()
        n_df['city'] = city
        n_df[itemCd] = value
        n_df['date'] = col
        lst.append(n_df)
        
    final_df = pd.concat(lst, axis=0)
    
    return(final_df)


def start(engine, today):
        
    today = today.strftime("%Y-%m-%d")
    
    #WEEK,MONTHLY
    period = "WEEK"
    
    #make dataframe
    final_df = get_degi_data('SO2',period)
    item_list = ['CO', 'O3', 'NO2', 'PM10', 'PM25']
    for itemCd in item_list:
        df = get_degi_data(itemCd,period)
        print(df.columns)
        final_df = pd.merge(final_df, df, how="inner")
    
    #dataset rebuild
    final_df= final_df[['date','city','SO2','CO','O3','NO2','PM10','PM25']]
    final_df.sort(['date','city'], inplace=True)
    
    final_df = final_df[final_df['date'] == today]
    #del final_df['PM25']
    
    print('degi save..')
    final_df.to_sql(name='degi', con=engine, if_exists = 'append', index=False, chunksize=1000000)
