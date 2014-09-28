from __future__ import print_function
import sys
import re
from os import stat

from unicodecsv import DictReader
from collections import defaultdict

from common import kADJECTIVES as ADJS

from extract_results import movement_tuples

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


def analyze_game(game):
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

    player_sup_rel = []
    player_atk_rel = []
    player_atkhome_rel = []
    for year in years:
        #print(year)
        for season in seasons:
            #print(" ", season)
            for phase_type in types:
                this_state = nested_state[year][season][phase_type]
                this_press = nested_press[year][season][phase_type]
                this_results = nested_results[year][season][phase_type]
                result = standard_result(this_results)
                if any(len(k) for k in (this_state, this_press, this_results)):
                    #print("  ", phase_type,
                    #      len(this_state), len(this_press), len(this_results))
                    if phase_type == "M" and result:
                        player_sup_rel.append(supports(result))
                        player_atk_rel.append(attacks_with_hold(result))
                        player_atkhome_rel.append(attacks_on_home(result))
    return player_sup_rel, player_atk_rel, player_atkhome_rel


if __name__ == '__main__':
    game = sys.argv[1]
    player_sup_rel, player_atk_rel, player_atkhome_rel = analyze_game(game)
