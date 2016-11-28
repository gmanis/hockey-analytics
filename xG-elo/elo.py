from collections import defaultdict
import pandas as pd
import math

teams = {'ANA': 'Anaheim Ducks', 'ARI': 'Arizona Coyotes', 'BOS': 'Boston Bruins', 'BUF': 'Buffalo Sabres', 'CGY': 'Calgary Flames', 'CAR': 'Carolina Hurricanes', 'CHI': 'Chicago Blackhawks', 'COL': 'Colorado Avalanche', 'CBJ': 'Columbus Blue Jackets', 'DAL': 'Dallas Stars', 'DET': 'Detroit Red Wings', 'EDM': 'Edmonton Oilers', 'FLA': 'Florida Panthers', 'L.A': 'Los Angeles Kings', 'MIN': 'Minnesota Wild', 'MTL': 'Montreal Canadiens', 'NSH': 'Nashville Predators', 'N.J': 'New Jersey Devils', 'NYI': 'New York Islanders', 'NYR': 'New York Rangers', 'OTT': 'Ottawa Senators', 'PHI': 'Philadelphia Flyers', 'PIT': 'Pittsburgh Penguins', 'S.J': 'San Jose Sharks', 'STL': 'St. Louis Blues', 'T.B': 'Tampa Bay Lightning', 'TOR': 'Toronto Maple Leafs', 'VAN': 'Vancouver Canucks', 'WSH': 'Washington Capitals', 'WPG': 'Winnipeg Jets'}

home_factor = 35.0
velocity_of_change = 8.0
regular_importance = 1.0
playoff_importance = 1.5

elo = defaultdict(lambda: 1500.0)
elo_xG = defaultdict(lambda: 1500.0)

def expectation(home, away, elos):
    return (1.0 + math.pow(10, (elos[away] - elos[home] - home_factor)/400)) ** -1

def delta_elo(home, away, elos, margin, outcome, expectation, playoff=False):
    delta = playoff_importance if playoff else regular_importance
    delta = delta * velocity_of_change
    delta = delta * max(1, math.log(abs(margin - .85 * (elos[home] - elos[away] + home_factor) / 100) + math.e - 1))
    delta = delta * (outcome - expectation)
    return delta

stats = pd.read_csv("Corsica_Team.Stats_2015-2017.csv", parse_dates=['Date'], infer_datetime_format=True)
stats = stats.replace({"Team": teams})
stats = stats.rename(columns = {'Team': 'Home'})

schedule2015rs = pd.read_csv("2015rs.csv", parse_dates=['Date'], infer_datetime_format=True)
schedule2015rs["Playoff"] = False
schedule2015po = pd.read_csv("2015po.csv", parse_dates=['Date'], infer_datetime_format=True)
schedule2015po["Playoff"] = True
schedule2016rs = pd.read_csv("2016rs.csv", parse_dates=['Date'], infer_datetime_format=True)
schedule2016rs["Playoff"] = False
schedule2016po = pd.read_csv("2016po.csv", parse_dates=['Date'], infer_datetime_format=True)
schedule2016po["Playoff"] = True
schedule2017rs = pd.read_csv("2017rs.csv", parse_dates=['Date'], infer_datetime_format=True)
schedule2017rs["Playoff"] = False

schedule = pd.concat([schedule2015rs, schedule2015po, schedule2016rs, schedule2016po, schedule2017rs])

games = pd.merge(stats, schedule, how='left', on=['Date', 'Home'])
games = games.rename(columns = {'Visitor': 'Away'})
games = games.sort_values(by=["Date", "Home"])

results_df = pd.DataFrame(columns=['Date', 'Home', 'Home_ELO', 'Home_ELO_xG', 'Away', 'Away_ELO', 'Away_ELO_xG', 'Expectation', 'Expectation_xG', 'G+/-', 'xG+/-', 'Points', 'Points_xG', 'Home_ELO_new', 'Home_ELO_xG_new', 'Away_ELO_new', 'Away_ELO_xG_new'])
results = []
game = {}

for index, row in games.iterrows():
    game['Date'] = row['Date']
    game['Home'] = row['Home']
    game['Home_ELO'] = elo[row['Home']]
    game['Home_ELO_xG'] = elo_xG[row['Home']]
    game['Away'] = row['Away']
    game['Away_ELO'] = elo[row['Away']]
    game['Away_ELO_xG'] = elo_xG[row['Away']]
    game['Expectation'] = expectation(row['Home'], row['Away'], elo) * 100.0
    game['Expectation_xG'] = expectation(row['Home'], row['Away'], elo_xG) * 100.0
    game['G+/-'] = row['G+/-']
    game['xG+/-'] = row['xG+/-']
    if (row['G+/-'] == 0.0):
        game['Points'] = 100.0 - (abs(50.0 - game['Expectation']) * 2.0)
        game['Points_xG'] = 100.0 - (abs(50.0 - game['Expectation_xG']) * 2.0)
        outcome = 0.5
    elif (row['G+/-'] > 0.0):
        game['Points'] = game['Expectation']
        game['Points_xG'] = game['Expectation_xG']
        outcome = 1.0
    else:
        game['Points'] = 100.0 - game['Expectation']
        game['Points_xG'] = 100.0 - game['Expectation_xG']
        outcome = 0.0
    if (row['xG+/-'] == 0.0):
        outcome_xG = 0.5
    elif (row['xG+/-'] > 0.0):
        outcome_xG = 1.0
    else:
        outcome_xG = 0.0
    delta = delta_elo(row['Home'], row['Away'], elo, row['G+/-'], outcome, game['Expectation']/100, row['Playoff'])
    delta_xG = delta_elo(row['Home'], row['Away'], elo_xG, row['xG+/-'], outcome_xG, game['Expectation_xG']/100, row['Playoff'])
    elo[row['Home']] = elo[row['Home']] + delta
    elo[row['Away']] = elo[row['Away']] - delta    
    elo_xG[row['Home']] = elo_xG[row['Home']] + delta_xG
    elo_xG[row['Away']] = elo_xG[row['Away']] - delta_xG
    game['Home_ELO_new'] = elo[row['Home']]
    game['Home_ELO_xG_new'] = elo_xG[row['Home']]
    game['Away_ELO_new'] = elo[row['Away']]
    game['Away_ELO_xG_new'] = elo_xG[row['Away']]
    results.append(game)
    game = {}

results_df = results_df.append(results)

results_df.to_csv("elos.csv")
