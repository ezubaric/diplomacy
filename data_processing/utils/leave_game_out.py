from __future__ import print_function
import warnings

import numpy as np

from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef
from sklearn.base import clone
from sklearn.cross_validation import LeaveOneLabelOut
from sklearn.grid_search import ParameterGrid
from sklearn.externals.joblib import Parallel, delayed

from scikits.bootstrap import ci

def _fit_predict(clf, X, y_true, labels, params):
    y_pred = np.empty_like(y_true)
    clf = clone(clf).set_params(**params)
    for train, test in LeaveOneLabelOut(labels):
        clf.fit(X[train], y_true[train])
        y_pred[test] = clf.predict(X[test])
    return y_pred


def leaveout_fit_predict(clf, param_dict, X, y, labels, n_jobs=None,
                         verbose=None):
    param_grid = ParameterGrid(param_dict)
    predictions = Parallel(n_jobs=n_jobs, verbose=verbose)(
        delayed(_fit_predict)(clf, X, y, labels=labels, params=params)
        for params in param_grid)

    return zip(list(param_grid), predictions)


def best_setting(predictions, y_true, score=accuracy_score):
    scores = [score(y_true, y_pred) for _, y_pred in predictions]
    best_idx = np.argmax(scores)
    if best_idx in (0, len(scores) - 1):
        _which = "lowest" if best_idx == 0 else "highest"
        warnings.warn("Optimal score found using the {} parameter setting "
                      "provided. Please extend the search space in the "
                      "appropriate direction.".format(_which))
    return best_idx


def scores_table(row_preds, row_names, y_true, score_func=matthews_corrcoef,
                 alpha=0.05):
    for preds, name in zip(row_preds, row_names):
        best_idx = best_setting(preds, y_true, score_func)
        settings, y_pred = preds[best_idx]
        print_row = "|| {} ||".format(name)
        for report_score_func in accuracy_score, f1_score, matthews_corrcoef:
            score = report_score_func(y_true, y_pred)
            if score == 0:
                score_low, score_hi = 0, 0
            else:
                score_low, score_hi = ci((y_true, y_pred), report_score_func,
                                          alpha=alpha, n_samples=5000,
                                          method='bca')
            print_row += "{:.2f} ({:.2f}-{:.2f}) ||".format(score,
                                                            score_low,
                                                            score_hi)
        print(print_row)
