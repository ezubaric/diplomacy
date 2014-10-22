import re
import numpy as np

def decode_liwc_pattern(pattern):
    """LIWC uses the asterisk to denote word prefixes.  Decode it as regex"""
    if pattern.endswith("*"):
        return re.escape(pattern[:-1])
    else:
        return re.escape(pattern) + r"\b"


def liwc_lexicon_re(lexicon):
    return re.compile(r"\b({})".format("|".join(map(decode_liwc_pattern,
                                                    lexicon))))

def load(filename, return_re=True):
    """Load LIWC regular expressions from .dic file"""

    liwc_file = open(filename).readlines()

    begin_header, end_header = np.where([line.startswith('%')
                                         for line in liwc_file])[0]

    liwc_names = dict(line.split() for line in liwc_file[1 + begin_header:end_header])

    categs = dict((fields[0], fields[1:]) for fields in
                [re.sub("\(.*\)|<.*>|/", " ", line).split() for line in liwc_file[end_header + 1:]])

    liwc_lists = {"liwc_{}".format(name): [val
                                           for val, indices in categs.items()
                                           if key in indices]
                  for key, name in liwc_names.items()}

    if return_re:
        return {key: liwc_lexicon_re(val) for key, val in liwc_lists.items()}
    else:
        return liwc_lists


