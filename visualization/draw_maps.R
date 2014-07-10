library(png)
library(grid)
library(ggplot2)

# img <- readPNG("images/map.png")
# g <- rasterGrob(img, interpolate=TRUE)
# movements <- read.csv("move_sum.move.csv")
#movements <- movements[1:10,]

# dim_x <- dim(img)[1]
# dim_y <- dim(img)[2]

# movements$start_y <- dim_y - movements$start_y
# movements$end_y <- dim_y - movements$end_y

# basic layer and options
# plot1 <- ggplot(movements, aes(x = start_x, y = start_y, colour = country)) + xlim(0, dim_x) + ylim(0, dim_y) + geom_jitter(aes(size=all_freq)) + facet_grid(country ~ .) # +annotation_custom(g, xmin=0, ymin=0) + geom_text(aes(x=start_x, y=start_y + 25, label=start_name)) 

# load in the map layer
map <- read.csv("images/map_countries.csv")

country_names <- aggregate(map, by=list(map$territory), FUN=mean)
country_names$territory <- country_names$Group.1

countries <- ggplot() + geom_polygon(data=map, mapping=aes(x=x, y=y, group=territory, color=owner, fill=geography)) + scale_fill_manual(values=c("#AAFFAA", "#AADDDD", "#AAAAFF")) + geom_text(data=country_names, aes(x,y,label=territory))