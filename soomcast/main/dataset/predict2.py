import pandas as pd
import os
import h2o

def turn_on():
    # turn on H2O
    h2o.init()
    h2o.ls()

def start(engine, today, model_path):
    
    #turn on h2o machine
    turn_on()
    
    
    #set model path
    os.chdir(model_path)
    
    # current day set
    today = today.strftime("%Y-%m-%d")
    
    #select dataset_x
    dataset_x  = pd.read_sql("SELECT * FROM dataset_x where date = '"+today+"' and city='seoul';", engine)
    
    del dataset_x['date']
    del dataset_x['city']
    
    #make dataframe to h2oframe 
    df = h2o.H2OFrame(dataset_x)
    
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
        model = h2o.load_model(model_path+model_name)
        
        h2o_pred = model.predict(df)
        h2o_pred = h2o.as_list(h2o_pred)
        h2o_pred = h2o_pred.predict
        pred_a = str(h2o_pred[0]).replace('0','N').replace('1','Y')

  
        col_list.append(model_name)
        pred_list.append(pred_a)
    
    #shutdown h2o
    h2o.cluster().shutdown()
    #make pred dataframe        
    final_df  = pd.DataFrame(list(zip (col_list,pred_list)))
    
    #pred values
    final_df = final_df.T[1:]
    
    #pred columns name setting 
    final_df.columns = col_list
     
    final_df['date'] = today
    print('predict save..')
    print(final_df)
    #final_df.to_sql(name='pred', con=engine, if_exists = 'append', index=False, chunksize=1000000)
