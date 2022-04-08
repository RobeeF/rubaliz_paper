library(scales)
library(grid)
library(RColorBrewer)
library(devtools)
library(ComplexHeatmap)
library(tidyr)

# Change the path with yours
setwd('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/Results/integration')

x<-read.csv('Cbudget.csv', sep=';', header = T)
x <- x[,c('METHOD', 'Station', 'Discrepancy')]
#x<-as.data.frame(x)
mat<-x %>% pivot_wider(
  names_from = METHOD,
  values_from = Discrepancy
)
mat2=mat[,2:8]
heat <- scale(t(mat2))
colnames(heat)=mat$Station
#row.names(heat)=mat$Station
ComplexHeatmap::Heatmap(heat,cluster_columns =FALSE,
                        cluster_rows =FALSE,
                        heatmap_legend_param = list(direction = 'vertical',
                        title ='Z-scores', grid_width = unit(0.5, 'cm'), grid_height = unit(0.5, 'cm') 
                        ))#, heatmap_legend_param = list(direction = "vertical",  title ="Z-scores", grid_width = unit(1, "cm"), legend_height = unit(3, "cm")))



