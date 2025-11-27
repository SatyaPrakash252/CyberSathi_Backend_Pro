# CyberSathi Backend (Pro) — Emotion Detection + Continuous Learning + Full Logging

This is a production-ready backend-only build that includes:
- FastAPI server
- SQLite + SQLAlchemy ORM
- Message logging for ALL queries
- Emotion detection model (scikit-learn) with on-disk persistence
- Continuous learning: Admin can label messages and the model updates via partial_fit
- Complaint workflow (register, status, admin list)
- Simple intent/fraud-type detection

## Quickstart
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/init_db.py
uvicorn backend.app:app --reload --port 8000
```

## Key Endpoints
- POST /webhook — simulate WhatsApp inbound; logs message; runs emotion + intent
- POST /submit_complaint — create complaint (validates fields)
- GET  /status_check — by ticket or phone
- GET  /admin/complaints — list complaints
- GET  /messages — list/search logged messages
- POST /log_message — log any message (manual testing)
- POST /label_messages — attach human labels: {items:[{"id":1,"label":"distress"},...]}
- POST /train_emotion — train on all labeled samples (or immediately after labeling)
- GET  /model/info — model status/classes/last_trained
- GET  /export/messages.csv — export messages

## Emotions (default set)
["distress","anger","fear","sadness","neutral"]

## Notes
- The model is a TfidfVectorizer + SGDClassifier(loss='log_loss') with partial_fit for online updates.
- On first run, it bootstraps with a small seed dataset for reasonable initial predictions.
- Data is stored in ./cybersathi_pro.db and model artifacts under ./models/.
Added backend prototype notes.
this is updated later


# CyberSathi Backend – Commit by Satya
