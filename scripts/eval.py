"""
# Usage: 
1. Your PYTHONPATH has to be set to PYTHONPATH:pathtodreemdirectory
2. Go from the terminal in the directory of this file
3. Execute python eval.py `modelname` `datatype`

# Example:
`python eval.py logreg epochs`
"""

import sys
import importlib
import numpy as np

from sklearn.metrics import f1_score
from sklearn.model_selection import KFold

from load_features import *

modelname = 'svm'

# Read args
if len(sys.argv) > 1:
    modelname = sys.argv[1]

model_module = importlib.import_module("src.models." + modelname)

X = read('train')
X = scale(X)
y=readlabel()

kf = KFold(n_splits=4)
kf.get_n_splits(X)

scores = []
for train, test in kf.split(X):
    model = model_module.gen_model()
    model.fit(X[train], y[train])

    pred = model.predict(X[test])
    score = f1_score(y[test], pred, average='weighted')

    print(f"Score: {round(np.mean(score), 4)}")
    scores.append(score)

print(f"Mean score: {round(np.mean(scores), 4)}")
# SVM = .644
# RF = .66
