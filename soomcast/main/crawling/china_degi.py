from selenium import webdriver
from urllib.request import urlopen
import time
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup as bs

def sleep_short():
    time.sleep(2)
    
def sleep_medium():
    time.sleep(8)

def start(engine, today):
    print('china_degi start')
    
    today = today.strftime("%Y-%m-%d")
    month_t = today.replace('-','')[0:6]
    
    #driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])        
    driver = webdriver.Firefox()
    
    url = "https://www.aqistudy.cn/historydata/daydata.php?city=%E5%8C%97%E4%BA%AC&month=201312"
    driver.get(url)
    
    city_list = [
                '北京',
                '上海',
                '天津',
                '重庆',
                '杭州',
                '哈尔滨',
                '长春',
                '沈阳',
                '石家庄',
                '太原',
                '西安',
                '济南',
                '乌鲁木齐',
                '拉萨',
                '西宁',
                '兰州',
                '银川',
                '郑州',
                '南京',
                '武汉',
                '合肥',
                '福州',
                '南昌',
                '长沙',
                '贵阳',
                '成都',
                '广州',
                '昆明',
                '南宁',
                '深圳']


    base = "https://www.aqistudy.cn/historydata/daydata.php?month="+month_t+"&city="

    for city in city_list:
        print(city)
        driver.get(base+urllib.parse.quote_plus(city))
        sleep_medium()
            
        soup = bs(driver.page_source, 'lxml')
        values = [tr.findAll('td') for tr in soup.find('tbody').findAll('tr')]
        val_list=[]
        for n in range(1,len(values)):
            t = [t.get_text() for t in values[n]]
            val_list.append(t)
        df = pd.DataFrame(val_list)
        df['city'] = city
    
        header = ['date','aqi','status','PM2.5','PM10','SO2','CO','NO2','O3','rank','city']
        df.columns = header
        df = df[['date','aqi','PM2.5','PM10','SO2','CO','NO2','O3','rank','city']]
        df = df[df['date'] == today]
        print('save')
    
        #gs = goslate.Goslate()
        #df.replace(city, gs.translate(city,"en"), inplace=True)
        df.to_sql(name='china_degi', con=engine, if_exists = 'append', index=False, chunksize=1000000)
    
    driver.close()
 
