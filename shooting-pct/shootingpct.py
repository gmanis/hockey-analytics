import json
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

with open("hockeyshootingpct.json", "r") as file:
    data = json.load(file)
teams = []
years = []
game17 = []
game41 = []
game82 = []
last65 = []
goals17 = []
goals41 = []
goals82 = []
shots17 = []
shots41 = []
shots82 = []
for season in data:
    team, year = season.split(' ')
    if ('82' in data[season]):
        teams.append(team)
        years.append(year)
        game17.append(float(data[season]['17']['sh%']))
        game41.append(float(data[season]['41']['sh%']))
        game82.append(float(data[season]['82']['sh%']))
        last65.append((float(data[season]['82']['goals']) - float(data[season]['17']['goals'])) / (float(data[season]['82']['shots']) - float(data[season]['17']['shots'])))
        goals17.append(float(data[season]['17']['goals']))
        goals41.append(float(data[season]['41']['goals']))
        goals82.append(float(data[season]['82']['goals']))
        shots17.append(float(data[season]['17']['shots']))
        shots41.append(float(data[season]['41']['shots']))
        shots82.append(float(data[season]['82']['shots']))

df = pd.DataFrame({'team': teams, 'year': years, 'game17': game17, 'game41': game41, 'game82': game82, 'last65': last65, 'goals17': goals17, 'goals41': goals41, 'goals82': goals82, 'shots17': shots17, 'shots41': shots41, 'shots82': shots82})

print df.describe()

hot_start = df[df['game17'] > .1]

print hot_start.describe()

lm = smf.ols(formula='endonly ~ start', data=df).fit()

print lm.summary()
