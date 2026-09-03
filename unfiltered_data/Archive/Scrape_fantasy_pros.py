import pandas as pd
#import sqlalchemy as sa

url = "https://www.fantasypros.com/nfl/adp/overall.php"
#dfs = pd.read_html(url)

#adp_df = dfs[0]

#adp_df.to_csv("fantasy_pros_data.csv", index=False)

# Read the CSV back in
df = pd.read_csv("fantasy_pros_data.csv")

def split_player_team_bye(value):
    # Example: "Christian McCaffrey SF (9)"
    if pd.isna(value):
        return pd.Series([None, None, None])
    parts = value.strip().split()
    if len(parts) < 3:
        return pd.Series([value, None, None])
    bye = parts[-1]
    team = parts[-2]
    player = " ".join(parts[:-2])
    # Remove parens from bye and convert to int
    bye = int(bye.strip("()"))
    return pd.Series([player, team, bye])

df[['Player', 'Team', 'Bye']] = df['Player Team (Bye)'].apply(split_player_team_bye)

# Optionally, save the new dataframe
df.to_csv("fantasy_pros_data3.csv", index=False)
