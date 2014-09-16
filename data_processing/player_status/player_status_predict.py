from __future__ import print_function
from collections import Counter
import numpy as np

from sklearn.utils import shuffle

def _clean_message(msg):
    """Clean up a message"""
    return "\n".join(line for line in msg.split("\n")
                     if not line.startswith(">"))


def _clean(player_status):
    """Clean up all messages in a player status instance"""
    cleaned_talk = []
    for msg in player_status['talk']:
        msg['message'] = _clean_message(msg['message'])
        cleaned_talk.append(msg)
    player_status['talk'] = cleaned_talk
    return player_status


def player_status_train_test(player_statuses):
    """Make a train-test split"""

    # usak test games chosen by calling:
    # np.random.RandomState(0).choice(good_games, 20)
    # and taking the first 6 games that are not incomplete (see wiki)

    test_games = ['ns000078', 'ns000081', 'cavalry', 'showcase01', 'malafide',
                  'nexxice']
    test_games = ['usak-{}'.format(k) for k in test_games]


    # add more test games 
    # 50 test games from usdp such that they have at least 500 talk entries

    test_games += [u'usdp-anzac2011_potts', u'usdp-aloha2', u'usdp-service13',
u'usdp-vole_003', u'usdp-service14', u'usdp-owlsopen2011_1a',
u'usdp-owlsopen10_3f', u'usdp-echo7', u'usdp-owls_256', u'usdp-owls_246',
u'usdp-timgroup1', u'usdp-owlsopen2011_2f', u'usdp-agitar10', u'usdp-owls_242',
u'usdp-vole_001', u'usdp-tango', u'usdp-leoxiii', u'usdp-owlsopen2011_2g',
u'usdp-vole_025', u'usdp-vole_006', u'usdp-310', u'usdp-owlsopen2011_1c',
u'usdp-skullhouse11', u'usdp-vole_004', u'usdp-chess_match',
u'usdp-anzac2011_claw', u'usdp-service16', u'usdp-wetterling',
u'usdp-owlsopen2011_3c', u'usdp-inthedark1', u'usdp-owls_261',
u'usdp-owlsopen2011_3g', u'usdp-ltb2', u'usdp-owlsopen10_3h', u'usdp-vanilla1',
u'usdp-owlsopen2011_1g', u'usdp-vole_002', u'usdp-warzones1', u'usdp-vole_012',
u'usdp-benjgame', u'usdp-owlsopen2011_3e', u'usdp-power_struggle7',
u'usdp-owlsopen2011_3h', u'usdp-owlsopen2011_1d', u'usdp-vole_008',
u'usdp-owlsopen2011_2h', u'usdp-spartan01', u'usdp-rainier', u'usdp-owls_252',
u'usdp-owls_245'] 

    # filter out short instances
    print("Before filtering: n_instances=", len(player_statuses))
    THRESHOLD = 5  # at least 5 sent and 5 received messages
    player_statuses = [p for p in player_statuses
                    if sum(msg['direction'] == 'from'
                           for msg in p['talk']) >= THRESHOLD
                    and sum(msg['direction'] == 'to'
                            for msg in p['talk']) >= THRESHOLD]
    print("After filtering: n_instances=", len(player_statuses))
    train_statuses = [_clean(p) for p in player_statuses
                      if p['game'] not in test_games]
    test_statuses = [_clean(p) for p in player_statuses
                     if p['game'] in test_games]
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
