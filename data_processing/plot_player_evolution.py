import json
from collections import defaultdict
from matplotlib import pyplot as plt
import seaborn as sns

yearly_statuses = json.load(open("../data_processing/yearly_statuses.json"))

countries = ["Austria", "England", "France", "Germany", "Italy", "Russia", "Turkey"]

def game_visual_summary(gamename):
    years, evolutions = [], defaultdict(lambda: [])
    sorted_statuses = sorted(yearly_statuses[gamename].items(), key=lambda x: int(x[0][1:5]))
    for year, status in sorted_statuses:
        years.append(year)
        for country in countries:
            evolutions[country].append(status.get(country, [0, 0])[0])

    for country in countries:
        plt.plot(evolutions[country], label=country)
    plt.xticks(range(len(years)), years)
    plt.legend()
    plt.ylabel("Supply center owned")
    plt.title(gamename)
    plt.show()


game_visual_summary('phan03')
