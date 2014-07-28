import json
from collections import defaultdict
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

yearly_statuses = json.load(open("../data_processing/yearly_statuses.json"))

countries = ["Austria", "England", "France", "Germany", "Italy", "Russia", "Turkey"]

def game_visual_summary(gamename):
    years, evolutions = [], defaultdict(lambda: [])
    sorted_statuses = sorted(yearly_statuses[gamename].items(), key=lambda x: int(x[0][1:5]))
    for year, status in sorted_statuses:
        years.append(year)
        for country in countries:
            supplies, armies = status.get(country, [0, 0])
            evolutions[country].append(supplies - armies)
            # evolutions[country].append(np.sign(supplies - armies))

    for country in countries:
        plt.plot(evolutions[country], label=country)
    plt.xticks(range(len(years)), years, rotation=90)
    plt.legend()
    plt.ylabel("supplies")
    plt.title(gamename)


plt.figure(figsize=(20, 20))
sz = np.ceil(np.sqrt(len(yearly_statuses)))
for k, game in enumerate(yearly_statuses.keys()):
    plt.subplot(8, 4, 1 + k)
    game_visual_summary(game)
plt.tight_layout()
plt.savefig("player_evolutions.png")
