# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 15:45:37 2018

@author: user
"""

import pandas as pd
from scipy.spatial import *
import random
import numpy as np

weather_data = pd.read_csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/met_data_complete.csv", header = [0,1], index_col = [0,1])
traffic_data_main_roads = pd.read_csv("C:/Users/user/Documents/University/Foundations_Of_Data_Science/Group_Project/Raw_count_data_major_roads.csv")


weather_data.head()

weather_locations = weather_data.columns
for thing in weather_locations[0:10]:
    print(thing)

the_tree = cKDTree([thing for thing in weather_locations])
to_query = []

#for pos in range(100):
#    to_query.append((traffic_data_main_roads.iloc[random.randint(0,len(traffic_data_main_roads)),4],traffic_data_main_roads.iloc[random.randint(0,len(traffic_data_main_roads)),5]))
#
#print(to_query[0:5])
#
#results = the_tree.query_ball_point(to_query,r=50000) # find all weather points within 50km of the traffic point
#counts = []
#for result in results:
#    counts.append(len(result))
#print(len([thing for thing in counts if thing < 120]))

traffic_data_main_roads["max_temp"] = ""
traffic_data_main_roads["mean_temp"] = ""
traffic_data_main_roads["min_temp"] = ""
traffic_data_main_roads["rainfall"] = ""

#for i in range(len(traffic_data_main_roads)):
#    print(i)
#    loc = (traffic_data_main_roads.loc[i, "S Ref E"], traffic_data_main_roads.loc[i, "S Ref N"])
#    nearest_points = the_tree.query_ball_point(loc, r = 10000)
#    trial_rows = weather_data.loc[traffic_data_main_roads.loc[i, "dCount"]]
#    trial_cols = trial_rows[trial_rows.columns[nearest_points]]
#    trial_cols['mean'] = trial_cols.mean(axis=1)
#    traffic_data_main_roads.loc[i, "max_temp"] = trial_cols.iloc[0,len(trial_cols.columns) - 1]
#    traffic_data_main_roads.loc[i, "mean_temp"] = trial_cols.iloc[1,len(trial_cols.columns) - 1]
#    traffic_data_main_roads.loc[i, "min_temp"] = trial_cols.iloc[2,len(trial_cols.columns) - 1]
#    traffic_data_main_roads.loc[i, "rainfall"] = trial_cols.iloc[3,len(trial_cols.columns) - 1] 


def merging(row):
    loc = (row["S Ref E"], row["S Ref N"])
    print(loc)
    nearest_points = the_tree.query_ball_point(loc, r = 10000)
    trial_rows = weather_data.loc[row["dCount"]]
    trial_cols = trial_rows[trial_rows.columns[nearest_points]]
    trial_cols['mean'] = trial_cols.mean(axis=1)
    row["max_temp"] = trial_cols.iloc[0,len(trial_cols.columns) - 1]
    row["mean_temp"] = trial_cols.iloc[1,len(trial_cols.columns) - 1]
    row["min_temp"] = trial_cols.iloc[2,len(trial_cols.columns) - 1]
    row["rainfall"] = trial_cols.iloc[3,len(trial_cols.columns) - 1] 
    

traffic_data_main_roads.apply(merging, axis = 1)
traffic_data_main_roads.to_csv("Main_Road_Combined", encoding='utf-8', index=False)