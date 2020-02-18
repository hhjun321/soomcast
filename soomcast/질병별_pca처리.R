library(zoo)
library(dplyr)
library(data.table)
library(plyr)
library(reshape2)
library(psych)
library(TSclust)
library(seewave)
library(caret) 

file = "D:\\국민대학원\\프로젝트\\한국질병\\파일다운_datasetting_지역별(월별_일별로)\\J40.csv"
df  = read.csv(file, header=TRUE, sep=',', stringsAsFactors = FALSE)

#그래프로 pca와 각 변수의 값 확인
par(mfrow=c(5,2))
for(city in unique(df$지역)[1:10]){
  print(city)
  df_city = df[df$지역 == city,]
  rownames(df_city) = df_city$날짜
  #pairs.panels(df_city)
  
  pca = prcomp(df_city[,c(3,4,5,6,7)], scale=TRUE, center = T)
  #summary(pca)
  #screeplot(pca, npcs = 4)
  
  t = data.frame('pca1' = pca$x[,1] )
  t$pca2 = pca$x[,2]
  pca_ = prcomp(t, scale=FALSE)
  
  plot(scale(df_city[,c(3,4,5,6,7)])%*%pca$rotation[,1], pca$x[,1], main=city)
  
  plot(pca$x[,1],type='l', main=city)
  lines(scale(df_city$환자수), col="red")
  lines(scale(df_city$내원일수), col="blue")
  lines(scale(df_city$보험자부담금), col="green")
  lines(scale(df_city$청구건수), col="yellow")
  lines(scale(df_city$요양급여비용총액), col="gray")
}


# pca값은 sax로 변환 0,1로 치환하여 target df 생성 (2010~2014) test
city_list = lapply(unique(df$지역), function(city){
  print(city)
  #df_city = df[df$지역 == city & as.yearmon(df$날짜) < as.yearmon("2015-01"),]
  df_city = df[df$지역 == city,]
  rownames(df_city) = df_city$날짜
  
  
  #pca 생성
  pca = prcomp(df_city[,c(3,4,5,6,7)], scale=TRUE, center = T)
  
  #pca1을 sax를 위한 timeseries로 치환
  ts_pca = ts(pca$x[,1], start = c(2010,1,1), frequency = 365)
  
  # 1년치로 축소
  #paa_1 = PAA(ts_pca, 365)
  
  # 3개구간으로 sax 생성
  sax = convert.to.SAX.symbol(ts_pca, alpha=3)
  
  # sax 그래프확인 
  #ts.plot(sax)
  
  # 그래프확인
  #diss.MINDIST.SAX(ts_pca, ts_pca,length(ts_pca), alpha = 3, plot=TRUE)
  
  # target 생성 
  # sax > 2 면 1, 아니면 0 
  target = ifelse(sax > 2, 1, 0)
  
  # 최종 target df 생성
  target_df = df_city[,c("날짜","지역")]
  target_df$target = target
  target_df
})

final_df = do.call(rbind, city_list)
final_df$지역 = gsub("계","전체",final_df$지역)
saved = paste0("D:\\국민대학원\\프로젝트\\한국질병\\파일다운_datasetting_지역별(월별_일별로)\\target\\J40.csv")
write.csv(final_df, saved, row.names=FALSE)

# target으로 저장된 df 조회
final_df = fread(paste0("D:\\국민대학원\\프로젝트\\한국질병\\파일다운_datasetting_그룹별\\급성 상기도 감염\\성인(pca).csv"))
final_df = final_df[,c("날짜","target")]

# 대기자료 조회
file = "D:\\국민대학원\\프로젝트\\한국대기환경2\\x변수확장(1~4일).csv"
degi = fread(file)
degi = degi[degi$지역 =="서울",]

# 기상자료 조회
file = "D:\\국민대학원\\프로젝트\\한국대기환경2\\한국기상관측(일별).csv"
gisang = fread(file)
gisang = gisang[gisang$지역 =="서울",]

# 2016년 이전만 자름 (2016년도 대기자료 부족)
final_df_ = final_df[as.yearmon(final_df$날짜) < as.yearmon('2016-01'),]  
gisang_ = gisang[as.yearmon(gisang$날짜) < as.yearmon('2016-01'),]
degi_ = degi[as.yearmon(degi$날짜) < as.yearmon('2016-01'),]

#merge
df_ = cbind(degi_, final_df_, gisang_)
df_ = unique(df_)

#일단 풍향은 제외
df_$최대풍속풍향 = NULL
df_$최대순간풍속풍향 = NULL


df_ = data.frame(df_)
#2010년 ~ 2014년 train set 생성
df_2014 = df_[as.yearmon(df_$날짜) < as.yearmon('2015-01'),]

df_2014 = do.call(data.frame,lapply(df_2014, function(x) replace(x, is.infinite(x),NA)))
df_2014 = df_2014[complete.cases(df_2014),]

#날짜, 지역컬럼 삭제 후 trainset 생성
df_2014_ = df_2014[,c(3:length(colnames(df_2014)))]
write.csv(df_2014_, "C:\\Users\\han\\Desktop\\trainset.csv", row.names=FALSE)

#2015년 test set 생성 
df_2015 = df_[as.yearmon(df_$날짜) >= as.yearmon('2015-01') & as.yearmon(df_$날짜) < as.yearmon("2016-01"),]  

#날짜, 지역컬럼 삭제 후 testset 생성
df_2015 = df_2015[,c(3:length(colnames(df_2015)))]
write.csv(df_2015, "C:\\Users\\han\\Desktop\\testset.csv", row.names=FALSE)


# 모델생성 및 성능 평가
df_2014_$target = as.factor(df_2014_$target)

# train, test set 나누기
intrain = createDataPartition(y=df_2014_$target, p=0.7, list=FALSE)
train = df_2014_[intrain,]
test = df_2014_[-intrain,]

# randomForest
library(party)
library(randomForest)

randomF <- randomForest(target ~ ., data = train)

pred = predict(randomF, newdata = test, type = "class")
real = test$target
xtab = table(pred,real)
confusionMatrix(xtab)

#naiveBayes
#install.packages("e1071")
library(e1071)

nb_model = naiveBayes(target~., data = train)
pred = predict(nb_model, newdata = test)
real = test$target
xtab = table(pred,real)
confusionMatrix(xtab)


#tree
library(tree)

tree_model = tree(target~., data = train)
pred = predict(tree_model, newdata = test, type = "class")
real = test$target
xtab = table(pred,real)
confusionMatrix(xtab)

cv.trees<-cv.tree(tree_model, FUN=prune.misclass ) 
plot(cv.trees)
