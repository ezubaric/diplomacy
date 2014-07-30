from __future__ import print_function
from collections import Counter
import numpy as np

from sklearn.utils import shuffle

def player_status_train_test(player_statuses):
    """Make a train-test split"""

    # test games chosen by calling:
    # np.random.RandomState(0).choice(good_games, 20)
    # and taking the first 6 games that are not incomplete (see wiki)

    test_games = ['ns000078', 'ns000081', 'cavalry', 'showcase01', 'malafide',
                  'nexxice']

    # filter out short instances
    print("Before filtering: n_instances=", len(player_statuses))
    THRESHOLD = 10  # at least 10 sent and 10 received messages
    player_statuses = [p for p in player_statuses
                    if sum(msg['direction'] == 'from'
                           for msg in p['talk']) >= THRESHOLD
                    and sum(msg['direction'] == 'to'
                            for msg in p['talk']) >= THRESHOLD]
    print("After filtering: n_instances=", len(player_statuses))
    train_statuses = [p for p in player_statuses if p['game'] not in test_games]
    test_statuses = [p for p in player_statuses if p['game'] in test_games]
    print("Train: {}, test: {}".format(len(train_statuses), len(test_statuses)))
    print("Test label distribution: ",
          Counter(row['status'] for row in test_statuses))

    train_statuses = np.array(train_statuses)
    test_statuses = np.array(test_statuses)

    train_statuses = shuffle(train_statuses, random_state=0)
    test_statuses = shuffle(test_statuses, random_state=0)

    y_train = np.array([p['status'] for p in train_statuses])
    y_test = np.array([p['status'] for p in test_statuses])

    return train_statuses, y_train, test_statuses, y_test
