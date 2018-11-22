traffic_dataframe_main_road <- read.csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/Raw_count_data_major_roads.csv")
traffic_dataframe_minor_road <- read.csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/Raw_count_data_minor_roads.csv")
weather_data <- read.csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/met_data_complete.csv", header = FALSE, stringsAsFactors = FALSE)

weather_data <- weather_data[-3,]
weather_data[,1] <- paste((weather_data[,1]) , (weather_data[,2]), sep = " : ")
row.names(weather_data) <- weather_data[,1]
weather_data[,1] <- NULL
weather_data[,1] <- NULL



Column_names <- paste(substr(weather_data[1,],0,3), substr(weather_data[2,],0,3), sep = ", ")
names(weather_data) <- Column_names
weather_data <- weather_data[3:nrow(weather_data),]
traffic_dataframe_main_road$min_temp <- NA
traffic_dataframe_main_road$max_temp <- NA
traffic_dataframe_main_road$mean_temp <- NA
traffic_dataframe_main_road$rainfall <- NA


#traffic_dataframe_main_road_trial <- sample_n(traffic_dataframe_main_road,100000)

for (i in 1:nrow(traffic_dataframe_main_road)){
  print(i)
  date <- traffic_dataframe_main_road[i,"dCount"]
  easting <- substr(traffic_dataframe_main_road[i,"S.Ref.E"],0,3)
  northing <- substr(traffic_dataframe_main_road[i,"S.Ref.N"],0,3)
  column_finder <- paste(easting, northing, sep = ", ")
  column_finder <- grep(column_finder, names(weather_data))
  weather_date <- grep(date, row.names(weather_data))
  reduced_date_weather_data <- weather_data[weather_date, column_finder]
  if (is.double(reduced_date_weather_data)){
    print("FOUND")
    traffic_dataframe_main_road[i,"min_temp"] <- reduced_date_weather_data[1]
    traffic_dataframe_main_road[i,"mean_temp"] <- reduced_date_weather_data[2]
    traffic_dataframe_main_road[i,"max_temp"] <- reduced_date_weather_data[3]
    traffic_dataframe_main_road[i,"rainfall"] <- reduced_date_weather_data[4]
    }
  }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
View(traffic_dataframe_main_road)

