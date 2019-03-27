library(tools)

if(!dir.exists("pdf")) dir.create("pdf")
args <- commandArgs(trailingOnly = TRUE)
plot_title=args[1]
fname_data <- args[2]
max_y <- as.integer(args[3])
scaling <- as.integer(args[4])
y_label <- args[5]
unit <- args[6]

fname=gsub(' ','_',plot_title,fixed=TRUE)
fname_pdf=paste("pdf/bar_plot-",fname,".pdf",sep="")
pdf(fname_pdf,width=9)

colors=c("red2","deepskyblue4","orange","chartreuse3")

par(cex=1.5)
data=read.csv(fname_data,sep=",",head=F,comment.char="#")
len=length(data[,1])
xcol=vector(length=len)
for(i in 1:len)
{
  xcol[i] <- colors[len+1-i]
}

if (max_y == 0)
{
  max_y = max(data[,2])
}

bp <- barplot(data[,2],
              col = xcol,
              ylab=y_label,
              legend=colnames(data[0,2:2]),
              las=1,
              xaxt="n",
              yaxt="n",
              ylim=c(0,max_y),
             )
text(x=bp, y=data[,2], label=data[,2], pos=3, cex=0.8, col="black")
axis(side=1, at=bp, labels=data[,1])
ticks=sapply(axTicks(2), function(i) as.integer(i))
labels=sprintf("%.0f%s",ticks/scaling, unit)
axis(2, at=ticks, labels=labels)
title(plot_title,outer=TRUE,line=-1,font.main=2)
