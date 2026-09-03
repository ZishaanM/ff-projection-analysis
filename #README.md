#README

This is a README file for the project.

Plan:
- Grab ESPN projections for the 2025 season.
- Then, compare those point projections to the 2025 end of season points.
- (Use SQL? to) create two linked tables (or one combined table?)
- I'll use RMSD to measure the difference between the projections and the actual points, deriving a stdev for each position (RB_std, WR_std, etc.)
- Then, I'll need to start drafting leagues which will give me team stats.
    - Not sure how to do this yet. Maybe I'll have to code up a bunch of algorithms for each factor.

- The final output will be a streamlit UI with a page for each statistical factor being tested

Nature of the league:
- PPR
- 10-man
- NO TRADING OR SUBBING (bye-weeks, injuries will hopefully average out)

Data Cleaning Steps:
- Name matching: Handle variations ("De'Von Achane" vs "DeVon Achane")
- Position standardization: Ensure consistent RB/WR/QB/TE labels
- Missing player strategy: Decide how to handle players in only one dataset

Factors to test:
- are rookies typically overvalued?
- effectiveness of autodraft
- How successful is drafting each type of position first?
- Is it best to diversify teams?
- Better to get 3 wr/rb in the first 3 rounds? Or different positions
- Complete Random vs. Random within 50 spots on the list vs random within 40 spots...etc.
    - Basically, how much lower should you be able to reach without worrying about a dropoff in effectiveness. (May be tied to stdev)
- Team of rookies?
- Team of "injury prone" players?
- Same real-life team team
- Optimal draft position (first vs last)
- How optimal is taking the best players from last year

Things to consider:
- injuries and rookie-ness (they won't have a previous years ranking)
- If only 90 players start (9 people per team, 10 teams per league), then it may only make sense to look at the top 150 players in each dataset where hopefully the overlap is captured. The risk is that we may be leaving out important outliers.
- I don't believe I have 10 defenses, kickers. This may mean I have to take an average and use that in place of a defense to have that as a "constant". May need to graph to determine average or median.




