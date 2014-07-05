library(png)
library(grid)
library(ggplot2)

img <- readPNG("images/map.png")
g <- rasterGrob(img, interpolate=TRUE)
movements <- read.csv("movements.csv")

# basic layer and options
plot1 <- ggplot(mdat, aes(x = Count, y = Country, colour = Place))
+ geom_point()
+ facet_grid(.~Place) + theme_bw()
+ annotation_custom(g, xmin=-Inf, xmax=Inf, ymin=-Inf, ymax=Inf)
+ scale_colour_manual(values=c("#CC6600", "#999999", "#FFCC33", "#000000"))
