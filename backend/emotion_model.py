import joblib

emotion_pipeline = joblib.load("models/emotion_pipeline.joblib")
emotion_label_encoder = joblib.load("models/emotion_label_encoder.joblib")

def predict_emotion(text):
    try:
        pred = emotion_pipeline.predict([text])[0]
        emotion = emotion_label_encoder.inverse_transform([pred])[0]
        return emotion
    except Exception as e:
        print("Emotion prediction error:", e)
        return "neutral"
