import os, time, json
from typing import List, Tuple
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

MODEL_DIR = os.environ.get("CYBERSATHI_MODEL_DIR", "./models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "emotion_pipeline.joblib")
ENC_PATH   = os.path.join(MODEL_DIR, "emotion_label_encoder.joblib")
META_PATH  = os.path.join(MODEL_DIR, "emotion_meta.json")

DEFAULT_CLASSES = ["distress","anger","fear","sadness","neutral"]

def _seed_data():
    data = [
        ("please help my money is gone and i am scared", "distress"),
        ("i am very angry at this fraud", "anger"),
        ("i am afraid someone hacked my account", "fear"),
        ("feeling sad because i lost funds", "sadness"),
        ("hello i want to know status", "neutral"),
        ("urgent help my account is blocked i am panicking", "distress"),
        ("this is frustrating and makes me angry", "anger"),
        ("i fear that otp was leaked", "fear"),
        ("i am upset and sad about scam", "sadness"),
        ("hi just checking", "neutral")
    ]
    X, y = zip(*data)
    return list(X), list(y)

def _new_pipeline():
    clf = SGDClassifier(loss="log_loss", max_iter=1000, tol=1e-3)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ("clf", clf)
    ])
    return pipe

def _save_meta(meta: dict):
    with open(META_PATH, "w") as f:
        json.dump(meta, f)

def _load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            return json.load(f)
    return {"last_trained": None}

def load_or_init():
    if os.path.exists(MODEL_PATH) and os.path.exists(ENC_PATH):
        pipe = joblib.load(MODEL_PATH)
        enc  = joblib.load(ENC_PATH)
        meta = _load_meta()
        return pipe, enc, meta
    classes = DEFAULT_CLASSES
    enc = LabelEncoder().fit(classes)
    pipe = _new_pipeline()
    X_seed, y_seed = _seed_data()
    y_enc = enc.transform(y_seed)
    pipe.fit(X_seed, y_enc)
    joblib.dump(pipe, MODEL_PATH)
    joblib.dump(enc, ENC_PATH)
    _save_meta({"last_trained": time.time(), "classes": classes})
    return pipe, enc, {"last_trained": time.time(), "classes": classes}

def predict(text: str):
    pipe, enc, _ = load_or_init()
    try:
        proba = pipe.predict_proba([text])[0]
        idx = proba.argmax()
        conf = float(proba[idx])
        label = enc.inverse_transform([idx])[0]
        return label, conf
    except Exception:
        pred_idx = pipe.predict([text])[0]
        label = enc.inverse_transform([pred_idx])[0]
        return label, 0.5

def train_on(samples: List[Tuple[str, str]]):
    if not samples:
        return {"trained": 0}
    pipe, enc, meta = load_or_init()
    texts = [s for s, _ in samples]
    labels = [l for _, l in samples]
    y = enc.transform(labels)
    vec = pipe.named_steps["tfidf"]
    clf = pipe.named_steps["clf"]
    Xv = vec.transform(texts)
    clf.partial_fit(Xv, y, classes=list(range(len(enc.classes_))))
    joblib.dump(pipe, MODEL_PATH)
    joblib.dump(enc, ENC_PATH)
    _save_meta({"last_trained": time.time(), "classes": enc.classes_.tolist()})
    return {"trained": len(samples)}

def info():
    _, enc, meta = load_or_init()
    meta["classes"] = enc.classes_.tolist()
    return meta
