from sqlalchemy import create_engine
from datetime import timedelta, date

from crawling import degi_api, gisang_api
from dataset import dataset_x, predict

#today = date(2017, 5, 17)+timedelta(days=-1)
today = date.today()+timedelta(days=-1)

# before 4days 
before_4day = today+timedelta(days=-4)


db_config = 'mysql+mysqlconnector://root:93115@127.0.0.1:3307/sum'
engine = create_engine(db_config, echo=False)

model_path = 'D:\\국민대학원\\프로젝트\\모델만들기\\model'

degi_api.start(engine, today)
gisang_api.start(engine, today)
dataset_x.start(engine, today, before_4day)
predict.start(engine, today, model_path)