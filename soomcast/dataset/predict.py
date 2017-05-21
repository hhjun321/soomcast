import numpy as np
import pandas as pd
import os
import pickle
 
def start(engine, today, model_path):
    
    #set model path
    os.chdir(model_path)
    
    # current day set
    today = today.strftime("%Y-%m-%d")
    
    #select dataset_x
    dataset_x  = pd.read_sql("SELECT * FROM dataset_x where date = '"+today+"' and city='seoul';", engine)
    
    del dataset_x['date']
    del dataset_x['city']
    
    #select models
    models  = pd.read_sql("SELECT * FROM model;", engine)
    
    model_names = models['model_name']
    
    #model_name
    col_list=[]
    
    #pred values
    pred_list=[]
    
    #append predict value
    for model_name in model_names:
        #open model
        with open(model_name+".pkl", 'rb') as f:
            model = pickle.load(f)
            
            #predict...
            pred = model.predict_proba(dataset_x)
            pred_a = np.argmax(pred, axis=1)
            pred_a = str(pred_a[0]).replace('0','N').replace('1','Y')
    
            col_list.append(model_name)
            pred_list.append(pred_a)
    
    #make pred dataframe        
    final_df  = pd.DataFrame(list(zip (col_list,pred_list)))
    
    #pred values
    final_df = final_df.T[1:]
    
    #pred columns name setting 
    final_df.columns = col_list
     
    final_df['date'] = today
    print('predict save..')
    final_df.to_sql(name='pred', con=engine, if_exists = 'append', index=False, chunksize=1000000)
