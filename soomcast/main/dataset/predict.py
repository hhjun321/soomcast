import numpy as np
import pandas as pd
import os
import glob
import pickle
 
def start(engine, today, model_path):
    print('predict start')
    
    #set model path
    os.chdir(model_path)
    
    # current day set
    today = today.strftime("%Y-%m-%d")
    
    #select dataset_x
    dataset_x  = pd.read_sql("SELECT * FROM dataset_x where date = '"+today+"' and city='seoul';", engine)
    
    del dataset_x['date']
    del dataset_x['city']
    
    #select models
    model_names = glob.glob(model_path+"\\*")
    
    #model_name
    col_list=[]
    
    #pred values
    pred_list=[]
    
    #append predict value
    for model_p in model_names:
        #open model
        with open(model_p, 'rb') as f:
            model = pickle.load(f)
            
            #predict...
            pred = model.predict_proba(dataset_x)
            pred_a = np.argmax(pred, axis=1)
            pred_a = str(pred_a[0]).replace('0','N').replace('1','Y')
    
            #extract model_name
            model_name = os.path.basename(model_p).replace('.pkl','')
            
            col_list.append(model_name)
            pred_list.append(pred_a)
    
    #make pred dataframe        
    pred_df  = pd.DataFrame(columns=(['model_code','pred']),data=list(zip (col_list,pred_list)))
    
    #select model_code    
    models  = pd.read_sql("SELECT * FROM model;", engine)    
    model_codes = models['model_name']
    
    # insert data from each model_names
    for model_code in model_codes:
        #select model_code values
        df = pred_df[pred_df['model_code'].str.contains(model_code) ]
        
        #pred values
        final_df = df.T[1:]
        
        #pred columns name setting 
        final_df.columns = [col.replace(model_code,"D") for col in df['model_code']]
        final_df['model_name'] = model_code
        final_df['date'] = today
    
        print('predict save..'+model_code)
        final_df.to_sql(name='pred', con=engine, if_exists = 'append', index=False, chunksize=1000000)
    
