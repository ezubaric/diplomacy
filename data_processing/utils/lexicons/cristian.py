import re
import cPickle

def lexicon_re(lexicon):
    return re.compile(r"\b({})\b".format("|".join(map(re.escape, lexicon))))

def extended_lexicons(filename):
    lexicons = cPickle.load(open(filename, 'rb'))
    return {key: lexicon_re(val) for key, val in lexicons.items()}

lexicons = extended_lexicons("lexicons/data/extended-lexicons.pkl")
