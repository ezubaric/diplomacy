from __future__ import print_function
import json
import unicodecsv
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


yearly_statuses = json.load(open("../data_processing/yearly_statuses.json"))

def talk_of_country_in_year(talk, country, year):
    result = []
    for msg in talk:
        if msg['sender'] == country:
            msg['direction'] = 'from'
            result.append(msg)
        elif country in msg['receivers'] or msg['receivers'] == 'all':
            msg['direction'] = 'to'
            result.append(msg)
    return result


instances = []
for game_name, statuses in yearly_statuses.items():
    with open("../press_data/{}".format(game_name), "rb") as f:
        talk = list(unicodecsv.DictReader(f))


    statuses = [(int(phase[1:5]), country_statuses)
                for phase, country_statuses in statuses.items()]

    statuses = sorted(statuses)
    for phase, country_statuses in statuses:
        for country, (supplies, armies) in country_statuses.items():
            segment = talk_of_country_in_year(
                talk,
                country[0],  # initial of country name
                year=phase)
            instances.append(dict(game=game_name,
                                  year=phase,
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

bins = range(0, 100, 10) + range(100, 1000, 100) + [1500]
plt.hist(lens_from, normed=False, alpha=0.5, bins=bins, label="from")
plt.hist(lens_to, normed=False, alpha=0.5, bins=bins, label="to")
plt.ylabel("Number of training instances")
plt.xlabel("Number of messages")
plt.legend()
plt.title("Message count distribution in yearly player evolution dataset")
plt.savefig("player_status_dataset_hist.png")
