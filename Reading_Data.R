traffic_dataframe_main_road <- read.csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/Raw_count_data_major_roads.csv")
traffic_dataframe_minor_road <- read.csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/Raw_count_data_minor_roads.csv")
weather_data <- read.csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/test.csv", header = FALSE)

weather_data_required_time <- weather_data[c(1,2,14613:20000),]
dates <- format(strptime(as.character(weather_data_required_time[3:nrow(weather_data_required_time),1]), "%d/%m/%Y"), "%Y-%m-%d")
row.names(weather_data_required_time) <- c("easting","northing",dates)
weather_data_required_time[,1] <- NULL



Column_names <- paste(substr(weather_data_required_time[1,],0,3), substr(weather_data_required_time[2,],0,3), sep = ", ")
names(weather_data_required_time) <- Column_names
weather_data_required_time <- weather_data_required_time[3:nrow(weather_data_required_time),]
traffic_dataframe_main_road$Min.Rain <- NA


traffic_dataframe_main_road_trial <- sample_n(traffic_dataframe_main_road,100000)

for (i in 1:nrow(traffic_dataframe_main_road)){
  date <- traffic_dataframe_main_road[i,"dCount"]
  easting <- substr(traffic_dataframe_main_road[i,"S.Ref.E"],0,3)
  northing <- substr(traffic_dataframe_main_road[i,"S.Ref.N"],0,3)
  column_finder <- paste(easting, northing, sep = ", ")
  column_finder <- grep(column_finder, names(weather_data_required_time))
  if (length(weather_data_required_time[date,column_finder]) > 0){
    print("FOUND")
    traffic_dataframe_main_road[i,"Min.Rain"] <- weather_data_required_time[as.character(traffic_dataframe_main_road[i,"dCount"]),paste(easting, northing, sep = ", ")]
    }
  }
View(traffic_dataframe_main_road)

