library(ggplot2)
library(scales)
library(plyr)
library(foreach)
library(stringr)
setwd("~/github/2015-IndStudy-rbryan/testing")
rm(tmp)
rm(data)
data<-foreach(file=Sys.glob("*.csv"),.combine='rbind') %do% {
	tmp<-read.csv(file,header=T,stringsAsFactors=F)
	tmp$date<- as.Date(paste0(str_sub(file,0,7),"-01"))
	tmp
}
data$time <- with(data,ifelse(Trace.Duration=="day",24,ifelse(Trace.Duration=="month",24*30,ifelse(Trace.Duration=="week",24*7,1))))
ggplot(ddply(data,.(time),summarize,acc=median(Accuracy),sd=sd(Accuracy)),aes(time,acc))+geom_point()+geom_line()+theme_gray(14)+coord_cartesian(y=c(0,1))+theme(legend.position="top")+scale_x_log10(breaks=round(5^seq(0,5,by=.5)))+scale_y_continuous(breaks=pretty_breaks(20))+geom_errorbar(aes(ymin=acc-sd,ymax=acc+sd))+labs(x="hours",y="Accuracy")
