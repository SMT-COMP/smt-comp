library(tools)

if(!dir.exists("pdf")) dir.create("pdf")
args <- commandArgs(trailingOnly = TRUE)

min_x=as.integer(args[1])
max_x=as.integer(args[2])

plot_title=args[3]
fname=gsub(' ','_',plot_title,fixed=TRUE)
fname_pdf=paste("pdf/cactus_plot-",fname,".pdf",sep="")
pdf(fname_pdf,width=9)
par(cex=1.2)

colors=c("red2","deepskyblue4","orange","chartreuse3","dodgerblue1","dodgerblue3",
         "cornflowerblue","darkgreen","yellow2","darkorchid2","gray",
         "chartreuse2", "darkorange", "darkorchid3","deeppink","blue3",
         "darkolivegreen","cyan2","darkcyan","deepskyblue4","deeppink4",
         "chartreuse4","chocolate4","darkblue","darkgoldenrod2")
ncolors=length(colors)
ltypes=c(1,5,6,4,3,1,5,6,4,3,1,5,6,4,3,1,5,6,4,3,1,5,6)
lwidth=2
nfiles=(length(args)-3)/2
xlegend=vector(length=nfiles)
xtitles=vector(length=nfiles)
xpch=vector(length=nfiles)
xcol=vector(length=nfiles)
datacol=10
fname_data <- args[4]
fname <- file_path_sans_ext(basename(fname_data))

xvalues <- list()

data=read.csv(fname_data,sep=",",head=F,comment.char="#")
x=sort(ifelse(data[,datacol] > 1200, 1200, data[,datacol]))
xvalues[[1]] <- x

if (nfiles >= 2)
{
  for (i in 2:nfiles)
  {
    fname_data <- args[i+3]
    fname <- file_path_sans_ext(basename(fname_data))
    data=read.csv(fname_data,sep=",",head=F,comment.char="#")
    x=sort(ifelse(data[,datacol] > 1200, 1200, data[,datacol]))
    xvalues[[i]] <- x
  }
}

max_y=1200
xcol[1] <- colors[1]

options("scipen"=100, "digits"=4)
par(mar=c(5,5.2,2,3))
plot(x,xlab="# Benchmarks",type="n",xaxt="n",yaxt="n",ann=FALSE,col=colors[1],xlim=c(min_x, max_x),ylim=c(0, max_y))
abline(h=1200,col="lightgray")
abline(v=max_x,col="lightgray")
lines(xvalues[[1]],col=colors[1],lwd=lwidth,lty=ltypes[1])
xlegend[1] <- as.expression(bquote(bold(.(args[nfiles+4]))))

if (nfiles >= 2)
{
  for (i in 2:nfiles)
  {
    lines(xvalues[[i]],col=colors[i],lwd=lwidth,lty=ltypes[i])
    xlegend[i] <- as.expression(bquote(bold(.(args[nfiles+i+3]))))
    xcol[i] <- colors[i]
  }
}

ticks=sapply(axTicks(1), function(i) as.integer(i))
labels=sprintf("%i",ticks)
axis(1, at=ticks, labels=labels)
ticks=sapply(axTicks(2), function(i) as.integer(i))
labels=sprintf("%i",ticks)
axis(2, at=ticks, labels=labels)

title(ylab="Time [s]",line=4)
title(xlab="# Benchmarks",line=3)
title(plot_title,outer=TRUE,line=-1,font.main=2)
legend(x="topleft",xlegend,col=xcol,bty="n",lwd=lwidth,lty=ltypes,text.font=1,inset=c(0,.02))
