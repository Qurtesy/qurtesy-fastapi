import requests
import spacy
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

def train():
    # Load SpaCy model with vectors (use en_core_web_md or en_core_web_lg, not sm)
    nlp = spacy.load("en_core_web_md")

    training_data_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdDuM9UfluHPKV_ja9cAH6--7wFnMeSwKi7W32n_MQ63KD1abuymGs6FUM5EnTo-X7WyXlnTIMbEFS/pub?output=csv"
    df = pd.read_csv(training_data_csv)

    # Convert texts into vectors
    X = np.array([nlp(text).vector for text in df.iloc[:, 1].astype(str)]) # texts
    y = df.iloc[:, 0].values # labels

    # Split & train SVM for Category Identification
    X_train, X_test, y_train, labels_y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = svm.SVC(kernel="linear", probability=True)
    clf.fit(X_train, y_train)

    # Evaluate
    labels_y_pred = clf.predict(X_test)

    # Save the trained model
    joblib.dump(clf, "category_svm.pkl")

    y = df.iloc[:, 2].values # types
    # Split & train SVM for Category Identification
    X_train, X_test, y_train, types_y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = svm.SVC(kernel="linear", probability=True)
    clf.fit(X_train, y_train)

    # Evaluate
    types_y_pred = clf.predict(X_test)

    # Save the trained model
    joblib.dump(clf, "txn_type_svm.pkl")

    return f"{classification_report(labels_y_test, labels_y_pred)}\n{classification_report(types_y_test, types_y_pred)}"
