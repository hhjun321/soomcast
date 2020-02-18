# load the library
library(caret)
library(zoo)
library(dplyr)
library(data.table)
library(plyr)
library(reshape2)
library(psych)
library(TSclust)
library(seewave)

# target으로 저장된 df 조회
#file = "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\분석자료_소스코드 및 캡처본\\분석_호준\\J40.csv"
file = "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\분석자료_소스코드 및 캡처본\\분석_호준\\성인(pca).csv"
#file ="D:\\국민대학원\\프로젝트\\한국질병\\파일다운_datasetting_그룹별\\급성 상기도 감염\\성인.csv"
final_df = fread(file)
#final_df = final_df[,c("날짜","target")]
final_df = final_df[,c(1,2)]
colnames(final_df) = c("날짜","target")
# 대기자료 조회
file = "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\DATA_분야별 수집 데이터\\2ND_step_대기관련\\x변수확장(1~4일).csv"
degi = fread(file)
degi = degi[degi$지역 =="서울",]

# 기상자료 조회
file = "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\DATA_분야별 수집 데이터\\2ND_step_대기관련\\한국기상관측(일별).csv"
gisang = fread(file)
gisang = gisang[gisang$지역 =="서울",]

# 풍향 목적->수치
# library(reshape2)
# file = "D:\\국민대학원\\프로젝트\\한국대기환경2\\wind direction.csv"
# direct = fread(file)
# 
# wind_dir1= gisang[,c("날짜","지역","최대풍속","최대풍속풍향")]
# wind_dir1_ = dcast(wind_dir1, 날짜 + 지역 ~ direct$Direction, value.var = c("최대풍속"))
# wind_dir1_[is.na(wind_dir1_)] = 0
# wind_dir1_
# 
# gisang = merge(gisang,wind_dir1_)


# 2016년 이전만 자름 (2016년도 대기자료 부족)
final_df_ = final_df[as.yearmon(final_df$날짜) < as.yearmon('2016-01'),]  
gisang_ = gisang[as.yearmon(gisang$날짜) < as.yearmon('2016-01'),]
degi_ = degi[as.yearmon(degi$날짜) < as.yearmon('2016-01'),]

#merge
df_ = merge(degi_, gisang_, by=c("지역","날짜"))
df_ = merge(df_, final_df_, by="날짜")

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
write.csv(df_2014_, "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\분석자료_소스코드 및 캡처본\\분석_호준\\trainset.csv", row.names=FALSE)

#2015년 test set 생성 
df_2015 = df_[as.yearmon(df_$날짜) >= as.yearmon('2015-01') & as.yearmon(df_$날짜) < as.yearmon("2016-01"),]  

#날짜, 지역컬럼 삭제 후 testset 생성
df_2015 = df_2015[,c(3:length(colnames(df_2015)))]
write.csv(df_2015, "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\분석자료_소스코드 및 캡처본\\분석_호준\\testset.csv", row.names=FALSE)




# 
# # 모델생성 및 성능 평가
# df_2014_$target = as.factor(df_2014_$target)
# 
# # train, test set 나누기
# intrain = createDataPartition(y=df_2014_$target, p=0.7, list=FALSE)
# train = df_2014_[intrain,]
# test = df_2014_[-intrain,]
# 
# # randomForest
# library(party)
# library(randomForest)
# 
# randomF <- randomForest(target ~ ., data = train)
# 
# pred = predict(randomF, newdata = test, type = "class")
# real = test$target
# xtab = table(pred,real)
# confusionMatrix(xtab)
# 
# #naiveBayes
# #install.packages("e1071")
# library(e1071)
# lm_model = lm(target~., data = df_2014_)
# nb_model = lm_model
# nb_model = naiveBayes(target~., data = train)
# pred = predict(nb_model, newdata = test)
# real = test$target
# xtab = table(pred,real)
# confusionMatrix(xtab)
# 
# test = df_2015[,c(1:40)]
# pred = predict(nb_model, newdata = test)
# real = df_2015$target
# 
# plot(real, type='l')
# lines(pred, col=2)
# #tree
# library(tree)
# 
# tree_model = tree(target~., data = train)
# pred = predict(tree_model, newdata = test, type = "class")
# real = test$target
# xtab = table(pred,real)
# confusionMatrix(xtab)
# 
# cv.trees<-cv.tree(tree_model, FUN=prune.misclass ) 
# plot(cv.trees)
