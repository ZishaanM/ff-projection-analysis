#stdev by position

#column names: rank_pre,name,team,position,2024_pts,2025_proj_pts,rank_post,2025_pts

'''
NEXT STEPS:
Fix graphs so they appear at the same time, if possible use the same scale
SHOULD WE RANK BY POINTS OR BY ESPN?
'''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

master_df = pd.read_csv("master_df.csv")
wr_df = pd.DataFrame()
rb_df = pd.DataFrame()
qb_df = pd.DataFrame()
te_df = pd.DataFrame()
for player in master_df:
    wr_df = master_df[master_df["position"] == "WR"]
    rb_df = master_df[master_df["position"] == "RB"]
    te_df = master_df[master_df["position"] == "TE"]
    qb_df = master_df[master_df["position"] == "QB"]

master_df = pd.read_csv("master_df.csv")
positionList = master_df['position'].unique()

def getPositionalError(position_df):
    errorList = pd.DataFrame()
    for index, player in position_df.iterrows():
        errorList = pd.concat([errorList, (position_df["2025_pts"] - position_df["2025_proj_pts"])/position_df["2025_proj_pts"]])
    return errorList

wr_error_list = pd.DataFrame(getPositionalError(wr_df))
rb_error_list = pd.DataFrame(getPositionalError(rb_df))
qb_error_list = pd.DataFrame(getPositionalError(qb_df))
te_error_list = pd.DataFrame(getPositionalError(te_df))
master_error_list = [wr_error_list, rb_error_list, qb_error_list, te_error_list]

#create a histogram of the errors
fig, axs = plt.subplots(2, 2)
axs[0,0].hist(wr_error_list, bins=20)
axs[0,0].set_title("WR")
axs[0,0].axvline(0, color='black', label='Perfect Prediction')

axs[0,1].hist(rb_error_list, bins=20)
axs[0,1].set_title("RB")
axs[0,1].axvline(0, color='black', label='Perfect Prediction')

axs[1,0].hist(qb_error_list, bins=20)
axs[1,0].set_title("QB")
axs[1,0].axvline(0, color='black', label='Perfect Prediction')

axs[1,1].hist(te_error_list, bins=20)
axs[1,1].set_title("TE")
axs[1,1].axvline(0, color='black', label='Perfect Prediction')

plt.tight_layout()
plt.show()

print('''call a function to calculate stats for each position''')

def calculateErrorStats(error_list):
    RMSE = 0
    delta_y = 0
    for i in error_list:
        delta_y = position_df["2025_pts"] - position_df["2025_proj_pts"]
        RMSE = RMSE + ((delta_y)**2)
    RMSE = RMSE / error_list.length()
    RMSE = RMSE**(0.5)

#calculate error statistics (RMSE?)
'''
for i in master_error_list:
    print(i + "\nSum of errors: " + sum(i))
'''
