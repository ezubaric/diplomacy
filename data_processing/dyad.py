from __future__ import print_function
import sys

from collections import defaultdict

from extract_results import movement_tuples
from iter_game import iter_game

COUNTRIES = "EAGFRIT"

INIT_SUPPLY = {
    'Austria': "Budapest,Trieste,Vienna".split(","),
    "England": "Edinburgh,London,Liverpool".split(","),
    "France": "Brest,Marseilles,Paris".split(","),
    "Germany": "Berlin,Kiel,Munich".split(","),
    "Italy": "Naples,Rome,Venice".split(","),
    "Russia": "Moscow,Sevastopol,St Petersburg,Warsaw".split(","),
    "Turkey": "Ankara,Constantinople,Smyrna".split(",")}


def standardize_location(loc):
    """Standardize location names"""
    if "(" in loc:
        loc = loc[:loc.find("(") - 1]
    return loc.strip()


def important_orders(res):
    """Preprocesses results for easier extraction of attacks/helps"""
    moves, supps, holds = [], [], []
    for move in movement_tuples(res, {}, False):
        if move['order_type'] == 'move':
            moves.append((move['country'][0],
                          standardize_location(move['start_location']),
                          standardize_location(move['end_location'])))
        elif move['order_type'] == 'hold':
            holds.append((move['country'][0],
                          standardize_location(move['end_location'])))
        elif move['order_type'] == 'support':
            supps.append((move['country'][0],
                          standardize_location(move['end_location']),
                          move['help_country'][0],
                          standardize_location(move['support_start']),
                          standardize_location(move['support_end'])))

    # link each order to all units that support it
    # makes a dict of signature (move_type, move_idx):
    #                                (helper_country, helper_unit)

    linked_supps = defaultdict(list)
    for country, loc, supp_country, supp_start, supp_end in supps:
        idx = None
        if supp_start != supp_end:
            try:
                move_idx = moves.index((supp_country, supp_start, supp_end))
                idx = ('move', move_idx)
            except ValueError:
                pass
        else:
            stay = (supp_country, supp_start)
            if stay in holds:
                hold_idx = holds.index(stay)
                idx = ('hold', hold_idx)
            elif stay in [tuple(sup[:2]) for sup in supps]:
                supp_idx = [tuple(sup[:2]) for sup in supps].index(stay)
                idx = ('support', supp_idx)

        if idx is not None:
            linked_supps[idx].append((country, loc))

    return dict(moves=moves,
                holds=holds,
                supports=supps,
                linked_supports=linked_supps)


def supports(imp_orders):
    return [(fro, to)
            for fro, _, to, _, _ in imp_orders['supports'] if fro != to]


def attacks_on_home(imp_orders, return_supports=False):
    terr_owned = {terr: country[0]
                  for country, terrs in INIT_SUPPLY.items()
                  for terr in terrs}

    attacks = []
    supp_atk = []

    for k, (mover, _, dest) in enumerate(imp_orders['moves']):
        if dest in terr_owned and mover != terr_owned[dest]:
            attacks.append((mover, terr_owned[dest]))
            supp_atk.extend([(supporter, terr_owned[dest])
                              for supporter, _
                              in imp_orders['linked_supports']['move', k]])


    if return_supports:
        return attacks, supp_atk
    else:
        return attacks


def attacks_with_hold(imp_orders, return_supports=False):
    attacks = []
    supp_atk = []

    for holder, loc in imp_orders['holds']:
        for k, (mover, _, dest) in enumerate(imp_orders['moves']):
            if loc == dest and mover != holder:
                attacks.append((mover, holder))
                supp_atk.extend([(supporter, holder)
                                 for supporter, _
                                 in imp_orders['linked_supports']['move', k]])

    if return_supports:
        return attacks, supp_atk
    else:
        return attacks


def attacks_with_cut(imp_orders, return_supports=False, transitive=False):
    """Trying to cut a support is an attack."""
    attacks = []
    supp_atk = []
    for supporter, loc, supported, _, _ in imp_orders['supports']:
        for k, (mover, _, dest) in enumerate(imp_orders['moves']):
            if loc == dest and mover != supporter:
                # cutting support is aggressive
                attacks.append((mover, supporter))
                # and this propagates from who supports the attack
                supp_atk.extend([(other_supporter, supporter)
                                 for other_supporter, _
                                 in imp_orders['linked_supports']['move', k]])
                # but maybe also towards the supported country
                if transitive and supported not in (mover, supporter):
                    attacks.append((mover, supported))
                    supp_atk.extend([(other_supporter, supported)
                                     for other_supporter, _
                                     in imp_orders['linked_supports']['move', k]
                                     ])

    if return_supports:
        return attacks, supp_atk
    else:
        return attacks


def attacks_mutual(imp_orders, return_supports=False):
    attacks = []
    supp_atk = []

    for k_a, (mover_a, src_a, dest_a) in enumerate(imp_orders['moves']):
        for k_b, (mover_b, src_b, dest_b) in enumerate(imp_orders['moves']):
            if src_a == dest_b and src_b == dest_a and mover_a != mover_b:
                attacks.append((mover_a, mover_b))
                supp_atk.extend([(supporter, mover_b)
                                 for supporter, _
                                 in imp_orders['linked_supports']['move', k_a]])

                attacks.append((mover_b, mover_a))
                supp_atk.extend([(supporter, mover_a)
                                 for supporter, _
                                 in imp_orders['linked_supports']['move', k_b]])
    if return_supports:
        return attacks, supp_atk
    else:
        return attacks


def interactions(results, include_supports=True):
    imp_orders = important_orders(results)
    friends = supports(imp_orders)
    enemies = []
    for func in (attacks_on_home, attacks_with_hold, attacks_with_cut,
                 attacks_mutual):
        if include_supports:
            atk, atk_sup = func(imp_orders, return_supports=True)
            enemies.extend(atk + atk_sup)
        else:
            enemies.extend(func(imp_orders))

    return friends, enemies


def standard_result(phase_results):
    """Get the last result entry with "result" in the subject, or None

    In a phase, there can be 0, 1, or 2 (more?) result entries.
    On the data I looked at, you can get 2 in the first phase, because the
    "Game is starting" message is included, and you can get 0 in the very final
    state, if the game is incomplete.

    We establish the convention to use the last valid one of these (just in case
    there is more than one).
    """
    actual_results = [r['content'] for r in phase_results
                      if 'results' in r['subject'].lower()]
    if actual_results:
        return actual_results[-1]
    else:
        return None


def dyad_seqs(game):
    pairs = defaultdict(list)
    for k, (year,
            season,
            phase_type,
            state,
            press,
            results) in enumerate(iter_game(game)):
        result = standard_result(results)
        if phase_type == "M" and result:
            friends, enemies = interactions(result)
            for country_a in COUNTRIES:
                for country_b in COUNTRIES:
                    if country_a == country_b:
                        continue
                    this_fr = (country_a, country_b) in friends
                    this_en = (country_a, country_b) in enemies
                    rel = this_fr - this_en  # XXX: 0 if neither or both !!
                    pairs[country_a, country_b].append((k, (year, season), rel))

    pairs = dict(pairs)
    nonzero_pairs = dict()

    for (country_a, country_b), series in pairs.items():
        nonzero_series = [(k, turn, rel) for k, turn, rel in series
                          if rel != 0]
        if not nonzero_series:
            continue
        nonzero_pairs[country_a, country_b] = nonzero_series

    return nonzero_pairs


def status_flips(seqs, len_before=3, len_after=3, val_before=1, val_after=-1):
    total_len = len_before + len_after
    res = {key: [run  # all runs of appropriate length
                 for run in zip(*[seq[k:] for k in range(total_len)])
                 if all(x == val_before for _, _, x in run[:len_before])
                 and all(x == val_after for _, _, x in run[-len_after:])]
           for key, seq in seqs.items()}
    return {key: val for key, val in res.items() if val}


def status_flip_dataset(game, **flips_kwargs):
    dataset = []
    seqs = dyad_seqs(game)
    flips = status_flips(seqs, **flips_kwargs)
    press = [((year, season), pr) for year, season, _, _, pr, _
             in iter_game(game)]
    for (country_a, country_b), runs in flips.items():
        for run in runs:
            idx_start, idx_end = run[0][0], run[-1][0]
            run_press = [((year, season), [msg
                        for msg in phase_press
                        if (msg['apparent_sender'],
                            msg['apparent_receivers']) in (
                            (country_a, country_b), (country_b, country_a))])
                        for (year, season), phase_press
                        in press[idx_start:idx_end + 1]]
            dataset.append((country_a, country_b, run_press, run))
    return dataset


def dyad_interaction(game):
    player_sup_rel = []
    player_atk_rel = []
    player_atkhome_rel = []

    for year, season, phase_type, state, press, results in iter_game(game):
        result = standard_result(results)
        if phase_type == "M" and result:
            player_sup_rel.append(supports(result))
            player_atk_rel.append(attacks_with_hold(result))
            player_atkhome_rel.append(attacks_on_home(result))

    return player_sup_rel, player_atk_rel, player_atkhome_rel


if __name__ == '__main__':
    game = sys.argv[1]
    player_sup_rel, player_atk_rel, player_atkhome_rel = dyad_interaction(game)
