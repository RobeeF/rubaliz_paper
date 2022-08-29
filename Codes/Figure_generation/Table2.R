#==================================================
# Make a fancy version to put in the main text
#==================================================
library(stringr)

# Change the path with yours
setwd('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

# Import the limits of the mesopelagic sublayers
zones = read.csv('Results/ruptures/zones.csv')
zones['mesopelagic boundaries'] = str_c('(',str_c(round(zones$Upper.boundary, 0), ' ; ', round(zones$Lower.boundary, 0)), ')')
zones = zones[,c('cruise', 'station',  'mesopelagic boundaries')]

# Import the integrated PHP values
all.res = read.csv('Results/integration/RUBALIZ.csv')

colnames(all.res) = c("cruise",    "station", 
                      "PHP estimated (mg C m-2 d-1)", "low", "high",    
                      "R2", 'points number', 'xs')

# Create a CI rather than 2 values
all.res['PHP Confidence Interval (mg C m-2 d-1)'] = str_c('(',str_c(all.res$low, ' ; ', all.res$high), ')')

# Add the limits of the upper / lower mesopelagic zones
all.res = merge(all.res, zones , by=c('cruise', 'station'))

all.res = all.res[,c("cruise", "station", 'mesopelagic boundaries',
                     "PHP estimated (mg C m-2 d-1)", 'PHP Confidence Interval (mg C m-2 d-1)', 
                     "R2", 'points number' )]

write.csv(all.res, 'Results/integration/Table2.csv', row.names=FALSE)
