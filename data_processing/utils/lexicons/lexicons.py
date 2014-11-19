from io import open
import re


def lexicon_re(lexicon, ignore_case=True):
    args = [re.IGNORECASE] if ignore_case else []
    return re.compile(ur"\b({})\b".format(u"|".join(map(re.escape, lexicon))),
                      *args)


def load_lexicon(fname, comment="#", **kwargs):
    with open(fname, "r", **kwargs) as f:
        lex = [x.strip() for x in f if x.strip() and not x.startswith(comment)]
    return lex


claim = load_lexicon("data/claim_markers.txt")
premise = load_lexicon("data/premise_markers.txt")
positive = load_lexicon("data/positive-words.txt",
                        comment=";", encoding="latin1")
negative = load_lexicon("data/negative-words.txt",
                        comment=";", encoding="latin1")
assertives = load_lexicon("data/bias_related_lexicons/"
                          "assertives_hooper1975.txt")
factives = load_lexicon("data/bias_related_lexicons/factives_hooper1975.txt")
hedges = load_lexicon("data/bias_related_lexicons/hedges_hyland2005.txt")
implicatives = load_lexicon("data/bias_related_lexicons/"
                            "implicatives_karttunen1971.txt")
reportvb = load_lexicon("data/bias_related_lexicons/report_verbs.txt")

with open("data/subjectivity_clues_hltemnlp05/"
          "subjclueslen1-HLTEMNLP05.tff") as f:
    raw_subjectivity = [dict([field.split("=")
                              for field in line.split()
                              if "=" in field])
                        for line in f]

strongsubj = [entry['word1'] for entry in raw_subjectivity
              if entry['type'] == 'strongsubj']
allsubj = [entry['word1'] for entry in raw_subjectivity]

lexicons = dict(claim=claim,
                premise=premise,
                positive=positive,
                negative=negative,
                assertive=assertives,
                factive=factives,
                hedge=hedges,
                implicative=implicatives,
                reportvb=reportvb,
                strongsubj=strongsubj,
                allsubj=allsubj)

lexicons_re = {key: lexicon_re(val) for key, val in lexicons.items()}
