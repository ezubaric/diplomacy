from __future__ import print_function
from os.path import basename
import sys
import re

import unicodecsv

phase_re = re.compile(r'[SFW]\d{4}[MRBA]X?')  # move, retreat, build, adjust
PATH = "../data_standardized/"

if __name__ == '__main__':
    for fname in sys.argv[1:]:
        game_name = basename(fname)
        if game_name.endswith(".results"):
            game_name = game_name[:-len(".results")]
        with open(fname) as f:
            contents = f.read()
        msgs = contents.split("From dpjudge@diplom.org")[1:]
        with open(PATH + "usdp-{}.results".format(game_name), "wb") as f:
            writer = unicodecsv.writer(f, encoding="utf8", lineterminator="\n")
            writer.writerow(("phase", "subject", "content"))
            last_phase = 'S1901M'  # all games start here
            for m in msgs:
                timestamp, subject, content = m.split("\n", 2)
                if subject.startswith("Subject: "):
                    subject = subject[len("Subject: "):]
                phase = phase_re.search(subject)
                phase = phase.group(0) if phase else None
                if not phase:
                    if 'starting' in subject or 'complete' in subject:
                        phase = last_phase
                    else:
                        raise ValueError('phase missing from subject '
                                         '{}'.format(subject))
                last_phase = phase
                writer.writerow((phase,
                                 subject,
                                 "{}\n{}".format(timestamp.strip(), content)))
