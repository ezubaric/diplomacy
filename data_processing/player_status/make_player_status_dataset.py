""" usage: python $0 game_statuses.json path_to_presses/ [--tagged] """
from __future__ import print_function
import sys

import json
import unicodecsv
import re
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


extension = "press.tagged" if "--tagged" in sys.argv else "press"

with open(sys.argv[1], "rb") as f:
    yearly_statuses = json.load(f)

def talk_of_country_in_year(talk, country, year):
    result = []
    for msg in talk:
        if not msg['phase']:
            continue
        msg_year = int(re.findall(r"\d+", msg['phase'])[0])
        if msg_year != year:
            continue
        if msg['apparent_sender'] == country:
            msg['direction'] = 'from'
            result.append(msg)
        elif (country in msg['apparent_receivers'] or
              msg['apparent_receivers'] == 'all'):
            msg['direction'] = 'to'
            result.append(msg)
    return result

paths = {game_name: sys.argv[2] + "/{}.{}".format(game_name, extension)
         for game_name in yearly_statuses.keys()}

instances = []
for game_name, statuses in yearly_statuses.items():
    with open(paths[game_name], "rb") as f:
        talk = list(unicodecsv.DictReader(f))


    statuses = [(int(re.findall(r"\d+", phase)[0]), country_statuses)
                for phase, country_statuses in statuses.items()
                if phase]

    statuses = sorted(statuses)
    for year, country_statuses in statuses:
        for country, (supplies, armies) in country_statuses.items():
            segment = talk_of_country_in_year(
                talk,
                country[0],  # initial of country name
                year=year)
            instances.append(dict(game=game_name,
                                  year=year,
                                  country=country,
                                  status=np.sign(supplies - armies),
                                  talk=segment))

json.dump(instances, open("player_status_dataset.json", "w"))

# dataset statistics
print("Number of instances: ", len(instances))
lens_from = [len([msg for msg in instance['talk'] if msg['direction'] == 'from'])
             for instance in instances]

lens_to = [len([msg for msg in instance['talk'] if msg['direction'] == 'to'])
           for instance in instances]

lens = [len_from + len_to for len_from, len_to in zip(lens_from, lens_to)]

print("Avg. messages: {:.2f} ({:.2f} from, {:.2f} to)".format(
    np.mean(lens), np.mean(lens_from), np.mean(lens_to)))

print("Min messages: {:.2f} ({:.2f} from, {:.2f} to)".format(
    np.min(lens), np.min(lens_from), np.min(lens_to)))

bins = np.arange(0, 250, 10)
plt.figure(figsize=(8, 3))
pal = sns.color_palette()
plt.hist(lens_from, normed=False, alpha=0.33, bins=bins, label="from")
plt.hist(lens_to, normed=False, alpha=0.33, bins=bins, label="to")
plt.ylabel("Number of player-player-year instances")
plt.xlabel("Number of messages")
plt.legend()
plt.title("Message count distribution in yearly player evolution dataset")
plt.savefig("player_status_dataset_hist.png")
