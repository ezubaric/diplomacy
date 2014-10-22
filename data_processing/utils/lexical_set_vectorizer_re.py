import re
from collections import OrderedDict

import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin

class LexicalSetVectorizerRe(BaseEstimator, TransformerMixin):
    def __init__(self, word_sets=None, normalize=False, lower=False,
                 token_pattern=ur'(?u)\b\w\w+\b'):
        self.word_sets = word_sets
        self.normalize = normalize
        self.lower = lower
        self.token_pattern = token_pattern

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        word_sets = {key: re.compile(val) for key, val in self.word_sets.items()}
        word_sets = OrderedDict(sorted(word_sets.items())) if word_sets else {}
        self.feature_names_ = word_sets.keys()
        token_pattern = re.compile(self.token_pattern)

        counts = np.zeros((len(X), len(word_sets)), dtype=np.float)

        for row, doc in enumerate(X):
            doc = doc.lower() if self.lower else doc
            tokenized_doc = token_pattern.findall(doc)
            for col, word_set in enumerate(word_sets.values()):
                count = len(word_set.findall(doc))
                counts[row, col] = count
            if self.normalize:
                counts[row, :] /= len(tokenized_doc)
        return counts

    def get_feature_names(self):
        if not hasattr(self, "feature_names_"):
            self.feature_names_ = sorted(self.word_sets.keys())
        return self.feature_names_


if __name__ == '__main__':
    from lexicons import liwc
    liwc_lists = liwc.load(
        "/Users/mbk-59-41/code/utils/lexicons/data/LIWC2007_English080730.dic",
        return_re=False)
    cog_funct = list(
        set(liwc_lists['liwc_cogmech']).union(set(liwc_lists['liwc_funct'])))
    ws_cog_funct = {word: liwc.liwc_lexicon_re([word]).pattern
                    for word in cog_funct}
    vect = LexicalSetVectorizerRe(
        word_sets=ws_cog_funct, lower=True, normalize=False,
        token_pattern=ur"\b\w+\b")

    feature_names = vect.get_feature_names()
    for feature_idx in np.where(
            vect.transform(["I don't know what this string should be"]) > 0)[1]:
        print(feature_names[feature_idx])
