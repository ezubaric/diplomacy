import json
import numpy as np

instances = json.load(open("player_status_dataset.json", "r"))

from matplotlib import pyplot as plt
import seaborn as sns

lens_from = [len([msg for msg in instance['talk'] if msg['direction'] == 'from'])
             for instance in instances]

lens_to = [len([msg for msg in instance['talk'] if msg['direction'] == 'to'])
           for instance in instances]

lens = [len_from + len_to for len_from, len_to in zip(lens_from, lens_to)]
bins = range(0, 100, 10) + range(100, 1000, 100) + [1500]
print(bins)
plt.hist(lens_from, normed=False, alpha=0.5, bins=bins, label="from")
plt.hist(lens_to, normed=False, alpha=0.5, bins=bins, label="to")
plt.ylabel("Number of training instances")
plt.xlabel("Number of messages")
plt.legend()
plt.savefig("player_status_dataset_hist.png")
