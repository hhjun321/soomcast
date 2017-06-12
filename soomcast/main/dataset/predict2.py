import pandas as pd
import os
import glob
import h2o
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
from h2o.estimators.gbm import H2OGradientBoostingEstimator
from h2o.estimators.deeplearning import H2ODeepLearningEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator

def turn_on():
    # turn on H2O
    h2o.init()
    h2o.ls()

def start(engine, today, model_path):
    print('predict start')
    
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
    model_names = glob.glob(model_path+"\\*")
    
    #model_name
    col_list=[]
    
    #pred values
    pred_list=[]
    
    #append predict value
    for model_p in model_names:
        #open model
        model = h2o.load_model(model_p)
        
        h2o_pred = model.predict(df)
        h2o_pred = h2o.as_list(h2o_pred)
        h2o_pred = h2o_pred.predict
        pred_a = str(h2o_pred[0]).replace('0','N').replace('1','Y')

        model_name = os.path.basename(model_p)
        col_list.append(model_name)
        pred_list.append(pred_a)
    
    #shutdown h2o
    h2o.cluster().shutdown()
    #make pred dataframe        
    pred_df  = pd.DataFrame(columns=(['model_code','pred']),data=list(zip (col_list,pred_list)))
    
    models  = pd.read_sql("SELECT * FROM model;", engine)
    model_codes = models['model_name']
    
    for model_code in model_codes:
        
        #subset model using model_code
        df = pred_df[pred_df['model_code'].str.contains(model_code) ]
        
        #pred values
        final_df = df.T[1:]
        
        #pred columns name setting 
        final_df.columns = [col.replace(model_code,"D") for col in df['model_code']]
        final_df['model_name'] = model_code
        final_df['date'] = today
        
        print('predict save..'+model_code)
        final_df.to_sql(name='pred', con=engine, if_exists = 'append', index=False, chunksize=1000000)
