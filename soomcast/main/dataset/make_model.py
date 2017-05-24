import pandas as pd
import numpy as np
import h2o

import glob
import os
from sqlalchemy import create_engine


# days 일전 x값들로 y값 예측하는 dataframe 생성
# 예) days=5 
# 5일후 y값 예측
def make_pred_df(data, days):
    
    #dataset_x
    data_ = data.drop(['target'], axis=1)
    data_b = data_[0:len(data_)-days]
    
    #target_y
    target_ = data.target
    target_b = target_[days:len(target_)]    
    target_b = target_b.reset_index(drop=True)
    
    #rebuild dataframe
    final_df = pd.concat([data_b,target_b], axis=1)    
    final_df = h2o.H2OFrame(final_df)
    
    final_df["target"]=final_df["target"].asfactor()    
    
    return final_df

# 몇일전 데이터로 예측하는지 세팅

def make_model(days_a, data, file_nm):

    for days in range(2,days_a):
        model_name = "M"+file_nm+str(days-1)      
        print(model_name)

        #==============================================================================
        # dataset
        #==============================================================================

        train = make_pred_df(data, days)
        #test  = make_pred_df(test_2015, days)

        x=train.drop(['target'],axis=1).columns
        y="target"    
        
        #train set
        '''data_  = data_d.drop(['target'], axis=1)
        X_train = data_.ix[:,0:len(data_.columns)].as_matrix()
        y_train = data_d.target
        
        #import xgboost as xgb
        clf1 = RandomForestClassifier()
        clf1.fit(X_train,y_train)
        
        #now you can save it to a file        
        with open(model_name, 'wb') as f:
            pickle.dump(clf1, f)
    
        '''
        # Random Forest
        model = H2ORandomForestEstimator(ntrees=100,max_depth=10)
        model.train(x=x,y=y,training_frame=train)
        
        model_nm = h2o.save_model(model, path = save_path, force=True)
        os.rename(model_nm, model_name)
        


jil_grp_dict ={"급성.상기도.감염":"0101"
                ,"인플루엔자.및.폐렴":"0102"
                ,"기타.급성.하기도.감염":"0103"
                ,"상기도의.기타.질환":"0104"
                ,"만성.하기도.질환":"0105"
                ,"외부요인에.의한.폐질환":"0106"
                ,"주로.간질에.영향을.주는.기타.호흡기.질환":"0107"
                ,"하기도의.화농성.및.괴사성.병태":"0108"
                ,"흉막의.기타.질환":"0109"
                ,"호흡기계의.기타.질환":"0110"
                ,"영유아":"01"
                ,"어린이":"02"
                ,"청소년":"03"
                ,"성인":"04"
                ,"장년층":"05"
                ,"_":""
                ,"JGINDEX":""}

def make_rename(file):
    print("old::"+file)
    for dic in jil_grp_dict:
        #print(dic)
        file = file.replace(dic,jil_grp_dict[dic])
    print("new::"+file)
    return file



file = "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\분석자료_소스코드 및 캡처본\\분석_호준\\dataset_x\\dataset_x(all).csv"
dataset_x = pd.read_csv(file, header=0, encoding='cp949')

files = glob.glob("C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\분석자료_소스코드 및 캡처본\\분석_호준\\target_y"+ "\\*.csv")


save_path = 'D:\\국민대학원\\프로젝트\\모델만들기\\model2'
os.chdir(save_path)


# turn on H2O
t= h2o.init()
h2o.ls()



#1일~7일 예측모델생성
days_a = 9
for file in files:
    
    #target_y load
    target = pd.read_csv(file, header=0, encoding='cp949')
    target.columns = ["date","target"]

    #dataset_x merge
    df = pd.merge(dataset_x, target, how='inner')

    del df['date']
    del df['city']
    
    #old_name
    file_nm = os.path.basename(file)
    
    #new_name
    name = make_rename(file_nm)

    file_nm = name.replace(".csv","")
    
    #모델생성
    make_model(days_a, df, file_nm)
    
    