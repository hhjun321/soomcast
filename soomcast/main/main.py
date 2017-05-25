from sqlalchemy import create_engine
from datetime import timedelta, date

from crawling import degi_api, gisang_api
from dataset import dataset_x
#from dataset import predict
#from dataset import predict2

#today = date(2017, 5, 19)+timedelta(days=-1)
today = date.today()+timedelta(days=-1)

# before 4days 
before_4day = today+timedelta(days=-4)


db_config = 'mysql+pymysql://root:soomcastmysql@soomcast.vitamiin.co.kr:3306/soomcast'
engine = create_engine(db_config, echo=False)

model_path = '../model'
#model_path = '../model2/'

degi_api.start(engine, today)
gisang_api.start(engine, today)
dataset_x.start(engine, today, before_4day)
#predict.start(engine, today, model_path)
#predict2.start(engine, today, model_path)