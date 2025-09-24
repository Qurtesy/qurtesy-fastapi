import requests
import spacy
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load SpaCy model with vectors (use en_core_web_md or en_core_web_lg, not sm)
nlp = spacy.load("en_core_web_md")

training_data_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdDuM9UfluHPKV_ja9cAH6--7wFnMeSwKi7W32n_MQ63KD1abuymGs6FUM5EnTo-X7WyXlnTIMbEFS/pub?output=csv"
df = pd.read_csv(training_data_csv)

# Convert texts into vectors
X = np.array([nlp(text).vector for text in df.iloc[:, 1].astype(str)])
y = df.iloc[:, 0].values

# Split & train SVM
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = svm.SVC(kernel="linear", probability=True)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred))

# Save the trained model
joblib.dump(clf, "category_svm.pkl")
