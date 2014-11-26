import numpy as np
from sklearn.cross_validation import KFold

class GameKFold(KFold):
    def __init__(self, labels, n_folds=5):
        self.labels = labels
        self.n_folds = n_folds

    def __iter__(self):
        unique_labels = np.unique(self.labels)
        fold_sizes = (len(unique_labels) // self.n_folds) * np.ones(self.n_folds, dtype=np.int)
        fold_sizes[:len(unique_labels) % self.n_folds] += 1
        current = 0
        for fold_size in fold_sizes:
            start, stop = current, current + fold_size
            test_labels = unique_labels[start:stop]
            train_idx = np.where(reduce(np.logical_and, [self.labels != label for label in test_labels]))[0]
            test_idx = np.where(reduce(np.logical_or, [self.labels == label for label in test_labels]))[0]
            yield train_idx, test_idx
            current = stop

    def __repr__(self):
        return '%s(labels=%r, n_folds=%i)' % (
            #self.__class__.__module__,
            self.__class__.__name__,
            self.labels,
            self.n_folds,
        )
