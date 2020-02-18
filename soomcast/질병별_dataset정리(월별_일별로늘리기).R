library(zoo)
library(dplyr)
library(data.table)
library(plyr)

# function: dataframe 만들기 
make_dataframe = function(df){
  print("start")
  
  colnames(df) = gsub("X","",colnames(df))
  df$날짜 = zoo(as.character(df$날짜))
  
  #numeric으로 변환
  cols = c(4:length(df));    
  df[,cols] = apply(df[,cols], 2, function(x) as.numeric(x));
  
  gender = unique(df$성별구분)
  
  # 남, 여, 계 별로 dataframe을 자른다.
  df_gender_list = lapply(gender, function(key) {
    # 남, 여, 계에 해당하는 dataframe 조회
    df_key = df[df$성별구분 == key,]
    
    # 5세미만..... 80세이상 컬럼들 조회
    cols = colnames(df_key)
    cols = cols[4:length(cols)]
    
    # 5세미만..... 80세이상 컬럼별로 dataframe을 자른다
    df_col_list = lapply(cols, function(col) {
      print(paste0(key,"::",col))
      # 5세미만..... 80세이상 에 해당하는 dataframe 조회
      df_by_col = df_key[c("날짜",col)]
      
      # 월별을 일별로 데이터 늘리기
      df_col_day = month_to_day(df_by_col, col)
      
      # zoo to dataframe
      colnames(df_col_day) = c("날짜",col)
      df_col_day$성별구분 = key
      # 총 2344일이 맞다.
      df_col_day[order(df_col_day$날짜,  decreasing = FALSE),]
      
    })
    
    # 5세미만..... 80세이상 컬럼별 dataframe List를 하나의 dataframe으로 merge
    df_col = do.call(cbind,df_col_list)
    df_col = df_col[unique(colnames(df_col))]
    #df_col = Reduce(function(x, y) merge(x, y, by="날짜"), df_col_list)
    #df_col$성별구분 = key
    #sum(df_col[as.yearmon(df_col$날짜) == as.yearmon("2010-01-01") & df_col$성별구분 == "계",]$소계) 577.4483
    #sum(df[df$날짜 == "2010-01" & df$성별구분 == "계",]$소계)
    
  })
  
  # 남, 여, 계 별 dataframe List를 하나의 dataframe으로 merge
  final_df <- ldply(df_gender_list, data.table)
  print("done")
  return(final_df)
}



# function: 월별을 일별로 데이터 늘리기
month_to_day = function(df, col){
  
  # 값 추출
  #mBev = df_by_col[col]
  mBev = df[col]
  
  # 껍데기 만들기
  mMonth <- c(seq(as.Date('2010-1-1'),by='month',length=79))
  
  # 껍데기 order by 
  cpi <- zoo(mBev,order.by=mMonth)
  
  # 껍데기 일별로 나누고 값은 등록, 나머진 NA로 채우기
  mNA = merge(cpi, foo=zoo(NA, seq(start(cpi), end(cpi),"day")))[, 1]
  mNA = mNA[1:length(mNA)-1]
  # 스플라인(곡선형태값으로 NA값 채우기)
  mNA_spln = na.spline(mNA)
  
  # 껍데기 NA값 0으로 채우기
  mNA[is.na(mNA)] = 0
  
  # 실제값과 스플라인값 차이 제거 (실제값으로 맞추기)
  #mNA2 = mNA+(mean(mBev)-mean(mNA))
  
  #mNA_final = mNA_spln + (mean(as.numeric(mBev[[col]])) - mean(mNA_spln))
  #mNA_final = mNA_spln + (150 - mNA_spln)
  
  # zoo로만든 time series -> dataframe으로 변환 
  df_mNA = fortify.zoo(mNA)
  df_mNA_spln = fortify.zoo(mNA_spln)
  
  #년도-월 list 생성 (년월별 기준으로 일데이터로 변환위함)
  year_mon_list = substring(mMonth,1,7)
  year_mon_list = year_mon_list[1:length(year_mon_list)-1]
  
  # lapply(list, function(list_val){})
  # year_mon_list 안에 하나하나 돌려가면서 function 실행 후 list로 append
  df_mNA_spln_list = lapply(year_mon_list, function(year_mon) {
    # 월 sum
    mNA_ym= df_mNA[as.yearmon(df_mNA$Index) == as.yearmon(year_mon),]
    
    # 일별 값들 
    mNA_spln_ym = df_mNA_spln[as.yearmon(df_mNA_spln$Index) == as.yearmon(year_mon),]
    
    # 임의생성값 * ( sum(월) / sum(일별값) ) 
    # 생성한 값들의 합이 sum(월) 과 같아야 하므로 값을 조정한다. 
    # 예) 2010년 1월값이 150일때 
    # 임의값 150 + 155 + 160 의 합이 150이 되어야 한다. sum(125+155+170) = 150
    # 450x = 150
    # x = 150/450 -> x = sum(150) / sum(125+155+170)
    # 150 = 125*x + 155*x + 170*x 
    new = mNA_spln_ym$mNA_spln * ( sum(mNA_ym$mNA) / sum(mNA_spln_ym$mNA_spln))  
    
    # 현재 년월 데이터를 수정한 값으로 변경한다.
    df_mNA_spln[as.yearmon(df_mNA_spln$Index) == as.yearmon(year_mon),]$mNA_spln = new
    
    test = df_mNA_spln[as.yearmon(df_mNA_spln$Index) == as.yearmon(year_mon),]
  })
  
  #list -> dataframe 
  return_df <- ldply(df_mNA_spln_list, data.table)
  
  return(return_df)
}

# 실행 
file = "D:\\국민대학원\\프로젝트\\한국질병\\J질병_월별(청구건수).csv"
data = read.csv(file, header=TRUE, sep = ",", stringsAsFactors = FALSE)
month_df = data[data$코드 == "J00",]

day_df = make_dataframe(month_df)

# na 값 0으로 
day_df[is.na(day_df)] = 0
write.csv(day_df, "J00(일별).csv", row.names=FALSE)