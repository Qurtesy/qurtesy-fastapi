import re
import joblib
import spacy

nlp = spacy.load("en_core_web_md")  # use vectors
clf = joblib.load("category_svm.pkl")

def parse(text: str):
    doc = nlp(text)

    # Extract amount
    amount_match = re.search(r"\d+(?:\.\d{1,2})?", text)
    amount = float(amount_match.group()) if amount_match else None

    # Intent classification
    lower_text = text.lower()
    if "spent" in lower_text or "bought" in lower_text:
        tx_type = "Expense"
    elif "sent" in lower_text or "transfer" in lower_text:
        tx_type = "Transfer"
    elif "gave" in lower_text or "lend" in lower_text:
        tx_type = "Lend"
    else:
        tx_type = "Other"

    # Extract entities
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Predict category if Expense
    category = None
    
    vector = doc.vector.reshape(1, -1)
    category = clf.predict(vector)[0]

    return {
        "transaction_type": tx_type,
        "amount": amount,
        "entities": entities,
        "category": category
    }