#create master CSV

import pandas as pd

# Use relative paths - go up one folder (..) then into unfiltered_data
proj_pts_table = pd.read_csv('../unfiltered_data/ESPN_proj_pts.csv')

final_pts_table = pd.read_csv('../unfiltered_data/end_of_season_points.csv')
final_pts_table['name'] = final_pts_table['name'].str.strip()

master_df = pd.merge(proj_pts_table, final_pts_table, on='name', how='outer')
#master_df.sort_values(by='rank_pre', inplace=True)
master_df = master_df.dropna(subset=['rank_pre', 'rank_post'])

master_df.to_csv('master_df.csv', index=False)
print(master_df.head())
