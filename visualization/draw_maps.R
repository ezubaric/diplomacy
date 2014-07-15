library(png)
library(grid)
library(ggplot2)
library(grid)

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

country_names <- aggregate(map, by=list(map$territory, map$display), FUN=mean)
country_names$territory <- country_names$Group.1
country_names$display <- country_names$Group.2

countries <- ggplot() + geom_polygon(data=map, mapping=aes(x=x, y=y, group=territory, color=owner, fill=geography)) + scale_fill_manual(values=c("#AAFFAA", "#AADDDD", "#AAAAFF")) + geom_text(data=country_names, aes(x,y,label=display))

# Supports 
support <- read.csv("move_sum.sup.csv")
support$start_x <- support$start_x + .25
support$start_y <- support$start_y + .25
support$end_x <- support$end_x - .25
support$end_x <- support$end_x - .25
supports <- countries + geom_segment(data=support, aes(x=start_x, y=start_y, xend=end_x, yend=end_y, size=all_freq, lineend="butt"), arrow=arrow(length=unit(.25, 'cm'))) + facet_grid(country ~ target)
ggsave("supports.pdf", supports, units='in', width=64, height=64)

# Movements
move <- read.csv("move_sum.move.csv")
move$start_x <- move$start_x + .25
move$start_y <- move$start_y + .25
move$end_x <- move$end_x - .25
move$end_x <- move$end_x - .25
movements <- countries + geom_segment(data=move, aes(x=start_x, y=start_y, xend=end_x, yend=end_y, size=all_freq), arrow=arrow(length=unit(.25, 'cm'))) + facet_grid(country ~ .)
ggsave("move.pdf", movements, units='in', width=12, height=64)