#encoding: utf8
from __future__ import print_function
from os.path import basename
from os import listdir
import sys
import re

import unicodecsv

phase_re = re.compile(ur'[SFWAPOÞB]\d{1,4}[MRBA]X?')
# move, retreat, build, adjust
# spring, fall, winter(?), anno(?), strange variations?

PATH = "./data_standardized/"

datafolders = ["./data/usdp_private_press/", "./data/usdp_public_press/"]

if __name__ == '__main__':
    for datafolder in datafolders:
        for fname in listdir(datafolder):
            if not fname.endswith(".results"):
                continue
            game_name = basename(fname)
            if game_name.endswith(".results"):
                game_name = game_name[:-len(".results")]
            with open(datafolder + fname) as f:
                contents = f.read()
            msgs = contents.split("From dpjudge@")[1:]  # can come from various
            last_phase = None
            rows = []
            for m in msgs:
                timestamp, subject, content = m.split("\n", 2)
                judge_email_domain, timestamp = timestamp.split(None, 1)
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
                rows.append((phase, subject,
                            "{}\n{}".format(timestamp.strip(), content)))

        # get first non-null phase name
            for first_phase, _, _ in rows:
                if first_phase:
                    break
        #replace first undefined phases by first_phase
            rows = [(first_phase if not phase else phase,
                 subject,
                 content) for (phase, subject, content) in rows]
        # write the output file
            with open(PATH + "usdp-{}.results".format(game_name), "wb") as f:
                writer = unicodecsv.writer(f, encoding="utf8", lineterminator="\n")
                writer.writerow(("phase", "subject", "content"))
                writer.writerows(rows)
