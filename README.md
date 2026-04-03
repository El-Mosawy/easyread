## EasyRead
EasyRead turns difficult English into a clearer, easier-to-read version. Built for people who find official or complex English hard to follow.

### Current features
- Paste text or upload a `.txt` file
- Choose a reading level (simple / very simple)
- Generate an “easy version” and download it as a text file

### Run locally
**Backend (FastAPI)**
```bash
source easy/bin/activate
uvicorn backend.main:app --reload --port 8000