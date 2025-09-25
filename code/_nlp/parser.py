import re
import joblib
import spacy

nlp = spacy.load("en_core_web_md")  # use vectors
category_clf = joblib.load("category_svm.pkl") # category classifier
txn_type_clf = joblib.load("txn_type_svm.pkl") # category classifier

def parse(text: str):
    doc = nlp(text)

    # Extract amount
    amount_match = re.search(r"\d+(?:\.\d{1,2})?", text)
    amount = float(amount_match.group()) if amount_match else None

    # Extract entities
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Predict category if Expense
    category = None
    
    vector = doc.vector.reshape(1, -1)
    category = category_clf.predict(vector)[0]
    type = txn_type_clf.predict(vector)[0]

    return {
        "amount": amount,
        "entities": entities,
        "category": category,
        "transaction_type": type
    }