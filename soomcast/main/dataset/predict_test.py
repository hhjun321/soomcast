import pandas as pd
import os
import h2o
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
from h2o.estimators.gbm import H2OGradientBoostingEstimator
from h2o.estimators.deeplearning import H2ODeepLearningEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator
from sqlalchemy import create_engine


def turn_on():
    # turn on H2O
    h2o.init()
    h2o.ls()

def start(engine, model_path):
    print('predict start')
    
    
    #turn on h2o machine
    turn_on()
    
    
    #select dataset_x
    dataset_x  = pd.read_sql("SELECT * FROM dataset_x where date = '2017-05-22' and city='seoul';", engine)
    
    del dataset_x['date']
    del dataset_x['city']
    
    #make dataframe to h2oframe 
    df = h2o.H2OFrame(dataset_x)
    
    
    #model_name
    col_list=[]
    
    #pred values
    pred_list=[]
    
    #append predict value
    #open model
    model = h2o.load_model(model_path+"M0101041")
  
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
    print(final_df)
    print('predict save..')
    #final_df.to_sql(name='pred', con=engine, if_exists = 'append', index=False, chunksize=1000000)
    
db_config = 'mysql+pymysql://root:soomcastmysql@soomcast.vitamiin.co.kr:3306/soomcast?charset=utf8'
engine = create_engine(db_config, echo=False, encoding = 'utf-8')

model_path = '/media/soomcast/soomcast/'
start(engine, model_path)
