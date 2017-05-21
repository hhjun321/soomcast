from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup as bs
 
def sleep_short():
    time.sleep(2)
    
def sleep_medium():
    time.sleep(5)

def rebuild_frame(df):
    
    df['temp_range'] = df['temp_max'] - df['temp_min']
    
    cols = ['date'
            ,'city'
            ,'temp'
            ,'temp_range'            
            ,'rain'
            ,'ws_mont_max'
            ,'ws_max'
            ,'ws_mean'
            ,'dew_point_temp'
            ,'humidity'
            ,'air_press'
            ,'sunshn_time'
            ,'snow'
            ,'cloud_amt'
            ,'surface_temp']
    
    df = df[cols]    
    return df

def start(engine, today):
    today = today.strftime("%Y%m%d")
    
    driver = webdriver.Firefox()
    url = "https://data.kma.go.kr/data/grnd/selectAsosRltmList.do?pgmNo=36"
    driver.get(url)
    
    sleep_short()
    
    driver.execute_script('$("#loginBtn").click();')
    driver.execute_script('$("#loginId").val("hhjun321@naver.com");')
    driver.execute_script('$("#passwordNo").val("han93115301!");')
    
    driver.execute_script('fnLogin(); return false;')
    
    sleep_short()
    
    #select days data
    driver.execute_script('$("#dataFormCd option:eq(1)").attr("selected", "selected");')
    
    #start date
    driver.execute_script('$("#startDt").val("'+today+'");')
    
    #end date
    driver.execute_script('$("#endDt").val("'+today+'");')
    
    #select element
    driver.execute_script('$("#elementCds").val("SFC01013004,SFC01013002,SFC01013001,SFC01014006,SFC01015007,SFC01015004,SFC01015001,SFC01016004,SFC01016001,SFC01017001,SFC01018002,,SFC01019003,SFC01020001,SFC01021001");')
    
    #select element grp
    driver.execute_script('$("#elementGroupSns").val("102,103,104,105,106,107,,108,109,110");')
    
    #select location code
    driver.execute_script('$("#stnIds").val("154_116,154_108,155_159,156_143,156_176,157_201,157_102,157_112,158_156,159_133,160_152,161_98,161_119,161_202,161_203,161_99,162_105,162_100,162_106,162_104,162_93,162_214,162_90,162_121,162_114,162_211,162_217,162_95,162_101,162_216,162_212,163_226,163_221,163_131,163_135,163_127,164_238,164_235,164_236,164_129,164_232,165_172,165_251,165_140,165_247,165_243,165_254,165_244,165_248,165_146,165_245,166_259,166_262,166_266,166_165,166_164,166_258,166_174,166_168,166_252,166_170,166_260,166_256,166_175,166_268,166_261,166_169,167_283,167_279,167_273,167_271,167_137,167_136,167_277,167_272,167_281,167_115,167_130,167_278,167_276,167_138,168_294,168_284,168_253,168_295,168_288,168_255,168_289,168_257,168_263,168_192,168_155,168_162,168_264,168_285,169_185,169_189,169_188,169_187,169_265,169_184");')
    
    #100rows in 1page
    driver.execute_script('$("#schListCnt").val("100");')
    
    #start search
    driver.execute_script('goSearch(); return false;')
    
    #loading....
    sleep_medium()
    
    #table values
    #extract td values append list
    values = driver.find_element_by_id('contentsList').get_attribute('innerHTML')
    soup = bs(values,"lxml")
    values = [tr.findAll('td') for tr in soup.findAll('tr')]
    
    val_list=[]
    for n in range(0,len(values)):
        t = [t.get_text() for t in values[n]]
        val_list.append(t)
        
    #make table values to dataframe
    df = pd.DataFrame(val_list)
    
    #select city_code
    df_code  = pd.read_sql("SELECT * FROM GISANG_CITY;", engine)
    
    #change columns name
    cols = [ 'no','date'
              ,'temp'
              ,'temp_min'
              ,'temp_max'
              ,'rain'
              ,'ws_mont_max'
              ,'ws_max'
              ,'ws_mean'
              ,'dew_point_temp'
              ,'humidity'
              ,'air_press'
              ,'sunshn_time'
              ,'snow'
              ,'cloud_amt'
              ,'surface_temp']
    df.columns = cols   
    
    #convert city_code -> city_name
    df['city'] = 'test'
    
    for n in df_code.cityCd:
        df.loc[df['no'] == n, 'city'] = df_code[df_code.cityCd ==n].city.values[0]    
        
    #replace none and nan to zero
    df.fillna(0, inplace=True)
    df.replace('',0, inplace=True)
    df[cols[2:]]=df[cols[2:]].astype(float)
    
    #groupby using city and date
    df = df.groupby([df.city, df.date])[df.columns].median()
    df.reset_index(inplace=True)
    
    #dataframe rebuild
    df = rebuild_frame(df)
    print('gisang save')
    df.to_sql(name='gisang', con=engine, if_exists = 'append', index=False, chunksize=1000000)
    driver.close()
 
