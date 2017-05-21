import numpy as np
import pandas as pd
 
 
def start(engine, today, before_4day):
    
    # current day set
    today = today.strftime("%Y-%m-%d")
    
    # before 4days 
    start = before_4day.strftime("%Y-%m-%d")
    
    # select degi data (city=seoul)
    degi  = pd.read_sql("SELECT * FROM degi where date >= '"+start+"' and date <= '"+today+"' and city='seoul' ;", engine)
    
    # select gisang data (city=seoul)
    gisang  = pd.read_sql("SELECT * FROM gisang where date='"+today+"' and city='seoul' ;", engine)
    
    # to factor
    degi['date'] = pd.to_datetime(degi['date'])
    gisang['date'] = pd.to_datetime(gisang['date'])
    
    # delete pm25 (not model)
    del degi['PM25']
    
    
    city_list = []
    for city in degi['city'].unique():
        
        degi_city = degi[degi['city'] == city]
        total = len(degi_city)
        
        diff_df = pd.DataFrame([today], columns=['date'])
        for col in ['SO2','CO','NO2','O3','PM10']:
            
            col_df = np.array(degi_city[col])
    
            for no in range(1,5):            
                # before no day value
                col_df_1 = col_df[:(-no)][-1]
                # diff curent and before value
                diff = col_df[-1] - col_df_1
                
                # before value 
                diff_rate = diff/col_df_1
                
                #diff_df[col+"_d"+str(no)] =  col_df_1
                diff_df[col+"_d"+str(no)+"_rate"] =  diff_rate
    
        diff_df['city'] = city
        city_list.append(diff_df)
      
    final_df = pd.concat(city_list)
    
    final_df['date'] = pd.to_datetime(final_df['date'])
    
    df = pd.merge(final_df, gisang, on=['date'])
    df = pd.merge(df, degi, on=['date'])
    
    df['city'] = df['city_x']
    
    del df['city_x']
    del df['city_y']
    
    print('dataset_x save..')
    df.to_sql(name='dataset_x', con=engine, if_exists = 'append', index=False, chunksize=1000000)
 
