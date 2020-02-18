path = "C:\\Users\\han\\Google 드라이브\\17년도1학기_빅데이터MBA플젝\\DATA_분야별 수집 데이터\\3RD_step_호흡기질환관련\\05. J질병_일별_중분류별_연령대별\\"
setwd(path)

file = "JGINDEX_분리.csv"
j_index = fread(file)
setkey(j_index)
j_index_ = j_index[,c("날짜","만성 하기도 질환_청소년_JGINDEX")]


file = "만성 하기도 질환//청소년.csv"
df = fread(file)
df_ = df[,c(1,2,7,12,17,22,27,32)]

test=  merge(j_index_, df_, by="날짜")
test = data.frame(test)

# J_index와 상관관계분석
cor(test[,c(2:length(colnames(test)))])
pairs.panels(test[,c(2:length(colnames(test)))])
cor.plot(test[,c(2:length(colnames(test)))])


