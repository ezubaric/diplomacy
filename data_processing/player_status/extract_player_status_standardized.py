import unicodecsv
import re
import json
import fileinput
import warnings


def get_statuses(results_fname):
    statuses = {}
    years = set()
    years_with_status = set()
    with open(results_fname, "rb") as results_file:
        for row in unicodecsv.DictReader(results_file, encoding="latin1"):
            phase = row['phase']
            subject = row['subject']
            content = row['content']
            years.add(int(re.findall(r"\d+", phase)[0]))
            if "Ownership of supply centers" in content:
                if (subject.startswith("Re:") or subject.startswith("Rcpt:")
                        or 'Press ' in subject):
                    continue
                # phase = re.search(phase_re, subject).group(0)
                status = re.search(r'Ownership of supply centers:'
                                   r'\n\n.*?\n\n(.*?)\n\n',
                                   content, re.MULTILINE + re.DOTALL)
                if not status:
                    warnings.warn('Extraction regex failed in {}/{}'
                                  ''.format(game, phase),
                                  stacklevel=2)
                    continue
                status = status.group(1).strip().split("\n")
                if len(status) <= 1:
                    continue
                ownership = {}
                for line in status:
                    country = line.split()[0]
                    country = country[:-1]  # strip colon
                    supplies, units, _ = re.findall(r"\d+", line)
                    supplies, units = int(supplies), int(units)
                    ownership[country] = [supplies, units]
                statuses[phase] = ownership
                years_with_status.add(int(re.findall(r"\d+", phase)[0]))
    if years != years_with_status:
        warnings.warn("Years disagreement in {}: missed {}, added {}"
                      "".format(results_fname,
                                years - years_with_status,
                                years_with_status - years),
                      stacklevel=2)
    return statuses


if __name__ == '__main__':
    PATH = "/local/diplomacy/code/diplomacy/data_standardized/"
    # PATH = "/Users/mbk-59-41/diplomacy/code/diplomacy/data_standardized/"
    game_statuses = {}
    # old_statuses = json.load(open("player_status/yearly_statuses.json", "rb"))
    for game in fileinput.input():
        game = game.strip()
        statuses = get_statuses(PATH + game + ".results")
        # temporary check for consistency with old method
        # raw_name = game.split("-", 1)[1]
        # for key in statuses:
        #     for country in statuses[key]:
        #         a = statuses[key][country]
        #         b = old_statuses[raw_name][key][country]
        #         if a != b:
        #             raise ValueError("Disagreement in game {} "
        #                              "for phase {} and country {}: "
        #                              "{} != {}".format(game, key, country, a, b))
        game_statuses[game] = statuses
    with open("game_statuses.json", "wb") as f:
        json.dump(game_statuses, f)

