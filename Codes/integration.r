#***********************************
# Mesopelagic PHP integration
#**********************************
# Code: D. Nerini 03/2022, R. Fuchs 03/2022

rm(list=ls())
cat("\014")

library(mvtnorm)
library(tidyr)

#working directory. Change it your path
setwd("C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/")
res.dir <- file.path('Results', 'integration/')

#*********************************
# Fetch the bounds of all methods
#*********************************
# Import rupture file
rubaliz = read.csv('Results/ruptures/zones.csv')
benchmarks = read.csv('Results/ruptures/benchmark.csv', check.names = F)
benchmarks[,'200-1000m'] = 200
benchmarks[,'50-1000m'] = 50

methods = c('RUBALIZ', colnames(benchmarks)[3:length(benchmarks)])

cruises <- list.dirs('Data/integration', full.names = F, recursive = FALSE)
nb.cruises = length(cruises)

for (method in methods){

  #*********************************
  # List the cruises and stations
  #*********************************

  # Declare the storage
  paramsave=list(cruise=NULL, station= NULL, a1=NULL,b1=NULL,a2=NULL,b2=NULL,xs=NULL)
  SSEsave=NULL
  intbootot=NULL
  saveint=NULL
  nomcamp = c()
  nb.points = c()
  xs.s = c()
  R2.list = c()
  int.values = c()

  nboot=10000
  n.xs = 100
  pred.resolution1 = 500
  pred.resolution2 = 250
  pred.resolution3 = 10000

  for (cruise in cruises){
    
    # Keep only the stations that present a rupture
    if (method == 'RUBALIZ'){
      stations <- rubaliz[rubaliz$cruise == cruise,]$station
      rupt.cruise <- rubaliz[rubaliz$cruise == cruise,]
    } else {
      stations <- benchmarks[benchmarks$cruise == cruise,]$station
      rupt.cruise <- benchmarks[benchmarks$cruise == cruise,
                                c('cruise', 'station', method)]
      rupt.cruise[, method] = round(rupt.cruise[, method], 0)

      rupt.cruise[,'Lower.boundary'] = 1000 # No lower boundaries for benchmark methods
      colnames(rupt.cruise) = c('cruise', 'station', 'Upper.boundary', 'Lower.boundary')
    }

    for (station in stations){
      data.dir <- file.path('Data', 'integration', cruise, station)

      #Load data
      df <- read.table(file.path(data.dir, 'prodFLP.csv'),
                       sep = ',', header = T,check.names=FALSE)
      data = df[,c('Depth (m)', 'PHP (mg C m-3 d-1)')]

      # Set the limit of the mesopelagic zone
      rupt.station = rupt.cruise[rupt.cruise$station == station,]

      xmin = rupt.station$Upper.boundary
      xmax = rupt.station$Lower.boundary

      # If the boundary is missing do not output this station for the given method
      if (is.na(xmin)){
        next
      } else {
        nomcamp = c(nomcamp, paste0(cruise, '_', station))
      }

      #==========================================
      # REGRESSION DOUBLE EN FIXANT LE SEUIL
      #==========================================

      x=log(data[,'Depth (m)'])
      y=log(data[,'PHP (mg C m-3 d-1)'])
      n=length(y)
      nb.points = c(nb.points, n)

      y=y[order(x)]
      x=sort(x)

      #**********************
      # CHOIX AUTOMATIUE DU SEUIL
      #**********************

      born=quantile(x, c(0.2,0.8))
      xstest=seq(born[1],born[2],length=n.xs)

      SSE=NULL
      for(xs in xstest){
        x1=x[x<=xs]
        x2=x[x>xs]
        y1=y[x<=xs]
        y2=y[x>xs]

        n1=length(x1)
        n2=length(x2)
        Xdes=cbind(rep(1,n),c(x1,rep(xs,n2)),c(rep(0,n1),x2-xs))
        achap=solve(t(Xdes)%*%Xdes)%*%t(Xdes)%*%y
        b1=achap[1]
        a1=achap[2]
        a2=achap[3]
        b2=(a1-a2)*xs+b1

        xpred=seq(min(x),max(x),length=pred.resolution1)
        ypred=c(a1*xpred[xpred<=xs]+b1,a2*xpred[xpred>xs]+b2)

        ychap=c(a1*x1+b1,a2*x2+b2)
        sig2chap=1/n*sum((y-ychap)^2)
        SSE=c(SSE,sig2chap)
      }

      #**********************
      # FIT AVEC xs OPTIMAL
      #**********************

      SSEsave=cbind(SSEsave,SSE)
      elu=which.min(SSE)
      xs=xstest[elu]
      xs.s = c(xs.s, exp(xs))

      x1=x[x<=xs]
      x2=x[x>xs]
      y1=y[x<=xs]
      y2=y[x>xs]

      n1=length(x1)
      n2=length(x2)
      Xdes=cbind(rep(1,n),c(x1,rep(xs,n2)),c(rep(0,n1),x2-xs))
      achap=solve(t(Xdes)%*%Xdes)%*%t(Xdes)%*%y
      b1=achap[1]
      a1=achap[2]
      a2=achap[3]
      b2=(a1-a2)*xs+b1

      xpred=seq(min(x),max(x),length=pred.resolution2)
      ypred=c(a1*xpred[xpred<=xs]+b1,a2*xpred[xpred>xs]+b2)

      ychap=c(a1*x1+b1,a2*x2+b2)
      sig2chap=1/n*sum((y-ychap)^2)
      Vchap=sig2chap*solve(t(Xdes)%*%Xdes)

      #**********************
      # R2 computation
      #**********************

      num = sum((exp(y) - exp(ychap))^2)
      den = sum((exp(y) - mean(exp(y)))^2)
      R2 = 1 - num / den
      R2.list = c(R2.list, R2)

      #***********************
      # SAUVEGARDE DATA
      #***********************

      paramsave$cruise=c(paramsave$cruise,cruise)
      paramsave$station=c(paramsave$station,station)
      paramsave$a1=c(paramsave$a1,a1)
      paramsave$b1=c(paramsave$b1,exp(b1))
      paramsave$a2=c(paramsave$a2,a2)
      paramsave$b2=c(paramsave$b2,exp(b2))
      paramsave$xs=c(paramsave$xs,exp(xs))

      if(xmin>=exp(xs)) tmpint=exp(b2)/(a2+1)*(xmax^(a2+1)-(exp(xs))^(a2+1))
      if(xmin<exp(xs)) tmpint=exp(b1)/(a1+1)*((exp(xs))^(a1+1)-xmin^(a1+1))+exp(b2)/(a2+1)*(xmax^(a2+1)-(exp(xs))^(a2+1))
      paramsave$int=c(paramsave$int,tmpint)

      int.values = c(int.values, tmpint)

      #***********************
      # BOOTSTRAP IC + INT
      #***********************

      yboot=NULL
      intboot=NULL

      tir=rmvnorm(nboot,achap,Vchap)
      b1boot=tir[,1]
      a1boot=tir[,2]
      a2boot=tir[,3]
      b2boot=(a1boot-a2boot)*xs+b1boot

      if(xmin<exp(xs)) intboot=exp(b1boot)/(a1boot+1)*((exp(xs))^(a1boot+1)-xmin^(a1boot+1))+exp(b2boot)/(a2boot+1)*(xmax^(a2boot+1)-(exp(xs))^(a2boot+1))
      if(xmin>=exp(xs)) intboot=exp(b2boot)/(a2boot+1)*(xmax^(a2boot+1)-(exp(xs))^(a2boot+1))

      intbootot=cbind(intbootot,intboot)
      cat("intboot_mean=",mean(intboot),", int=",tmpint,", pmin=", xmin,", pseuil=",exp(xs),", pmax=",xmax,fill=TRUE)
      for(i in 1:pred.resolution2){
        if(xpred[i]<=xs) tmp=a1boot*xpred[i]+b1boot
        if(xpred[i]>xs)  tmp=a2boot*xpred[i]+b2boot
        yboot=cbind(yboot,tmp)
      }
      yquant=apply(yboot,2,quantile,c(0.025,0.5,0.975))
      yquant=t(yquant)

      #***************************
      # Calcul des IC
      #***************************

      # ! Take x, y in level and not in log
      x=data[,'Depth (m)']
      y=data[,'PHP (mg C m-3 d-1)']

      y=y[order(x)]
      x=sort(x)

      if(xmin<xs) int=b1/(a1+1)*(xs^(a1+1)-xmin^(a1+1))+b2/(a2+1)*(xmax^(a2+1)-xs^(a2+1))
      if(xmin>=xs)int=b2/(a2+1)*(xmax^(a2+1)-xs^(a2+1))

      saveint=c(saveint,int)

    }
  }

  #=========================
  # Wrapping all together
  #=========================

  names(saveint)=nomcamp
  colnames(intbootot)=nomcamp
  quant=apply(intbootot,2,quantile,c(0.025,0.25,0.5,0.75,0.975))
  int.bxp=boxplot(intbootot,plot=FALSE)
  int.bxp$stats=quant

  # Mettre param.savint comme tot
  final.out = round(t(quant[c(1,3, 5),]),2)
  colnames(final.out) = c('low', 'tot', 'high')
  final.out = final.out[,c('tot', 'low','high')]

  # Format the data
  names = data.frame(x =rownames(final.out)) %>% separate(x, c("cruise", "station"), sep = '_')
  final.out = cbind(names, final.out)
  final.out$R2 = round(R2.list, 2) # Will ask David
  final.out[,'points number'] = nb.points
  final.out[,'xs'] = round(xs.s, 0)
  final.out[, 'tot'] = round(int.values, 2)
  write.csv(final.out, file = file.path(res.dir, paste0(method, '.csv')), row.names = F)
}
