from __future__ import print_function
import sys
import re
from os import stat

from unicodecsv import DictReader
from collections import defaultdict

from common import kADJECTIVES as ADJS

from extract_results import movement_tuples

COUNTRIES = "EAGFRIT"

def supports(orders):
    support_orders = []
    for line in orders.split("\n"):
        m = re.search("SUPPORT ({})".format("|".join(ADJS)), line)
        if m:
            support_orders.append((line[0], m.group(1)[0]))  # just first letter?

    return support_orders


def attacks_on_home(orders):
    INIT_SUPPLY = {
        'Austria': "Budapest,Trieste,Vienna".split(","),
        "England": "Edinburgh,London,Liverpool".split(","),
        "France": "Brest,Marseilles,Paris".split(","),
        "Germany": "Berlin,Kiel,Munich".split(","),
        "Italy": "Naples,Rome,Venice".split(","),
        "Russia": "Moscow,Sevastopol,St Petersburg,Warsaw".split(","),
        "Turkey": "Ankara,Constantinople,Smyrna".split(",")}
    terr_owned = {terr: country[0]
                  for country, terrs in INIT_SUPPLY.items()
                  for terr in terrs}

    attacks = []
    for move in movement_tuples(orders, {}, escaped=False):
        dest = move['end_location']
        country = move['country'][0]
        if "(" in dest:  # is a fleet on a coast
            dest = dest[:dest.find("(") - 1]
        if (move['order_type'] == 'move' and dest in terr_owned
                and move['result'] == ''):
            victim = terr_owned[dest]
            if victim != country:
                attacks.append((country, victim))
    return attacks


def attacks_with_hold(orders):
    """Identify obvious attacks of the type: A moves to B; B holds."""
    territories_held = {}
    territories_moved_to = defaultdict(list)
    for move in movement_tuples(orders, {}, escaped=False):
        dest = move['end_location']
        country = move['country'][0]
        if "(" in dest:  # is a fleet on a coast
            dest = dest[:dest.find("(") - 1]
        if move['order_type'] == 'hold':
            territories_held[dest] = country
        elif move['order_type'] == 'move':
            territories_moved_to[dest].append(country)

    attacks = []
    for terr in territories_held:
        if terr in territories_moved_to:
            attacks.extend(((attacking_country, territories_held[terr])
                            for attacking_country in territories_moved_to[terr]))
    return attacks


def attacks_with_support(orders):
    territories_held = {}
    territories_supported_into = defaultdict(list)
    for move in movement_tuples(orders, {}, escaped=False):
        dest = move['end_location']
        country = move['country'][0]
        if "(" in dest:  # is a fleet on a coast
            dest = dest[:dest.find("(") - 1]
        if " " in dest:  # not sure about this
            dest, _ = dest.split(" ", 1)
        if move['order_type'] == 'hold':
            territories_held[dest] = country
        elif move['order_type'] == 'support':
            supp_start = move['support_start']
            supp_end = move['support_end']
            supp_country = move['help_country'][0]
            if supp_start != supp_end and supp_country != country:
                territories_supported_into[supp_end].append(country)

    attacks = []
    for terr in territories_held:
        if terr in territories_supported_into:
            attacks.extend(((attacking_country, territories_held[terr])
                            for attacking_country in territories_supported_into[terr]))

    return attacks

def friend(orders):
    return supports(orders)


def enemy(orders):
    return attacks_with_hold(orders) + attacks_on_home(orders)


def nested_by_phase(rows, return_keys=True):
    if return_keys:
        ordered_years = []
        ordered_seasons = []
        ordered_types = []

    # ugh! default dict 3 levels deep
    nested = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        phase = row['phase']
        if phase == 'Beginning':
            continue  # skip these intro messages for now
        else:
            parsed_phase = re.search("([A-Z]+)(\d+)([A-Z]+)", phase)
            if not parsed_phase:  # unknown phase
                continue
            season, year, phase_type = parsed_phase.groups()
            year = int(year)

        nested[year][season][phase_type].append(row)

        if return_keys:
            if year not in ordered_years:
                ordered_years.append(year)
            if season not in ordered_seasons:
                ordered_seasons.append(season)
            if phase_type not in ordered_types:
                ordered_types.append(phase_type)

    if return_keys:
        return nested, ordered_years, ordered_seasons, ordered_types
    else:
        return nested


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


def iter_game(game):
    # raise appropriate exception if gamestate is empty
    if stat(game + ".gamestate").st_size == 0:
        raise ValueError("Game {} has empty gamestate, probably doesn't start "
                         "at the beginning.".format(game))

    with open(game + ".gamestate", "rb") as f:
        game_state = list(DictReader(f))

    with open(game + ".press", "rb") as f:
        press = list(DictReader(f, encoding="latin1"))

    with open(game + ".results", "rb") as f:
        order_results = list(DictReader(f))

    nested_state = nested_by_phase(game_state, return_keys=False)
    nested_press = nested_by_phase(press, return_keys=False)
    nested_results, years, seasons, types = nested_by_phase(order_results)

    for year in years:
        for season in seasons:
            for phase_type in types:
                state = nested_state[year][season][phase_type]
                press = nested_press[year][season][phase_type]
                results = nested_results[year][season][phase_type]
                if any(len(k) for k in (state, press, results)):
                    state = nested_state[year][season][phase_type]
                    press = nested_press[year][season][phase_type]
                    results = nested_results[year][season][phase_type]
                    yield (year, season, phase_type, state, press, results)


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
            friends = friend(result)
            enemies = enemy(result)
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


def status_flips(game, len_before=3, len_after=3, val_before=1, val_after=-1):
    total_len = len_before + len_after
    res = {key: [run  # all runs of appropriate length
                 for run in zip(*[seq[k:] for k in range(total_len)])
                 if all(x == val_before for _, _, x in run[:len_before])
                 and all(x == val_after for _, _, x in run[-len_after:])]
           for key, seq in dyad_seqs(game).items()}
    return {key: val for key, val in res.items() if val}


def status_flip_dataset(game, **flips_kwargs):
    dataset = []
    flips = status_flips(game, **flips_kwargs)
    press = [pr for _, _, _, _, pr, _ in iter_game(game)]
    for (country_a, country_b), runs in flips.items():
        for run in runs:
            idx_start, idx_end = run[0][0], run[-1][0]
            run_press = [[msg
                        for msg in phase_press
                        if (msg['apparent_sender'],
                            msg['apparent_receivers']) in (
                            (country_a, country_b), (country_b, country_a))]
                        for phase_press in press[idx_start:idx_end + 1]]
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
