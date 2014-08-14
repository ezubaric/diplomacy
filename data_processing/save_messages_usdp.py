from __future__ import print_function
import sys
from os.path import basename
import unicodecsv
import re


PATH = "../data_standardized"


def _country_code(country):
    if country == '(ANON)':
        return '?'
    elif country == 'All':
        return 'all'
    else:
        return country[0]


def _process_sig(signature):
    sender, recipients = signature.split(None, 1)
    recipients = recipients.split()
    sender = _country_code(sender)
    recipients = "".join([_country_code(r) for r in recipients])
    return sender, recipients

phase_re = r'[SFWA]\d{4}[MRBA]X?'  # move, retreat, build, adjust;
                                   # spring, fall, winter(?), anno(?)

if __name__ == "__main__":
    for fname in sys.argv[1:]:
        game_name = basename(fname)
        if game_name.endswith(".press"):
            game_name = game_name[:-len(".press")]
        with open(fname, "rU") as f:
            contents = f.read()
        presses = re.split(":: ({}|\?\?\?\?\?)".format(phase_re), contents)[1:]
        last_phase = "S1901M"
        processed_presses = []
        for ii in range(0, len(presses), 2):
            phase = presses[ii]
            press = presses[ii + 1]
            tagline, subject, press = press.split("\n", 2)
            #phase, signature = tagline.split(None, 1)
            signature = tagline.split(" | ")
            if len(signature) == 2:
                actual_sig, apparent_sig = signature
                actual_sender, actual_recipients = _process_sig(actual_sig)
                apparent_sender, apparent_recipients = _process_sig(apparent_sig)
            elif len(signature) == 1:
                actual_sender, actual_recipients = _process_sig(signature[0])
                apparent_sender = actual_sender
                apparent_recipients = actual_recipients
            else:
                raise ValueError("Too many sections in signature line!")

            # little hack to avoid undefined phases.
            if phase.startswith("?"):
                phase = last_phase
            else:
                last_phase = phase
            processed_presses.append((actual_sender,
                                      actual_recipients,
                                      apparent_sender,
                                      apparent_recipients,
                                      phase,
                                      None,  # no timestamp available
                                      press
                                     ))
        fname = PATH + "/usdp-{}.press".format(game_name)
        with open(fname, "wb") as f:
            writer = unicodecsv.writer(f, encoding="utf8", lineterminator="\n")
            writer.writerow(("actual_sender",
                             "actual_receivers",
                             "apparent_sender",
                             "apparent_receivers",
                             "phase",
                             "timestamp",
                             "message"))
            writer.writerows(processed_presses)
