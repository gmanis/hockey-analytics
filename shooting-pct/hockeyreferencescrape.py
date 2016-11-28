from bs4 import BeautifulSoup
import csv
import urllib2
import numpy
import json

#teams = ['NYR']
#years = ['2016']
teams = ['ANA','BOS','BUF','CGY','CAR','CHI','COL','CBJ','DAL','DET','EDM','FLA','LAK','MIN','MTL','NSH','NJD','NYI','NYR','OTT','PHI','PIT','SJS','STL','TBL','TOR','VAN','WSH']
years = [2011,2012,2014,2015,2016]
goals_column = {2011: 3, 2012: 3, 2014: 4, 2015: 4, 2016: 4}
shots_column = {2011: 12, 2012: 12, 2014: 13, 2015: 13, 2016: 13}
special_cases = [('PHX',2011),('PHX',2012),('PHX',2014),('ARI',2015),('ARI',2016),('ATL',2011),('WPG',2012),('WPG',2014),('WPG',2015),('WPG',2016)]

output = {}
diffFrom17 = []

for team, year in [(team,year) for team in teams for year in years] + special_cases:
    print team + " " + str(year)
    r  = urllib2.urlopen("http://www.hockey-reference.com/teams/" + team + "/" + str(year) + "_games.html")
    data = r.read()
    r.close()

    soup = BeautifulSoup(data, "html.parser")

    table = soup.find('table')
    season = {}
    game = 0
    goals = 0.0
    shots = 0.0
    for row in table.find_all('tr'):
        values = [val.text.encode('utf8') for val in row.find_all('td')]
        if values != []:
            if values[goals_column[year]] == '':
                break
            game += 1
            goals += float(values[goals_column[year]])
            if (values[goals_column[year]+3] == "SO" and values[goals_column[year]+2] == "W"):
                goals -= 1
            shots += float(values[shots_column[year]])
            season[game] = {'goals': goals, 'shots': shots, 'sh%': goals/shots}
    if (82 in season):
        diffFrom17.append(abs(season[17]['sh%'] - season[82]['sh%']))
    else:
        print team + " " + str(year)
    output[team + " " + str(year)] = season

with open("hockeyshootingpct.json", "a") as file:
    file.write(json.dumps(output))

diff = numpy.array(diffFrom17)
print "Mean " + str(numpy.mean(diff))
print "Median " + str(numpy.median(diff))
print "Deviation " + str(numpy.std(diff))
print "Max " + str(numpy.amax(diff))
print "Min " + str(numpy.amin(diff))
