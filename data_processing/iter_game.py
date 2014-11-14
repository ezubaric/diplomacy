import re
from os import stat
from os.path import exists
from unicodecsv import DictReader
from collections import defaultdict

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


def iter_game(game):
    """Iterates through all phases of a game."""


    # raise appropriate exception if gamestate is empty
    if stat(game + ".gamestate").st_size == 0:
        raise ValueError("Game {} has empty gamestate, probably doesn't start "
                         "at the beginning.".format(game))

    if exists(game + ".press.tagged"):
        press_file = game + ".press.tagged"
    else:
        press_file = game + ".press"

    with open(game + ".gamestate", "rb") as f:
        game_state = list(DictReader(f))

    with open(press_file, "rb") as f:
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

