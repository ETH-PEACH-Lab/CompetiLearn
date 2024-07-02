# README

## How to Run the Tool
1. Download the `data.zip` and unzip it to `./data`

2. Create `./.env` for the OPENAI API

```
# .env
OPENAI_API_KEY=YOUR_API_KEY

```

5. Run frontend at port `3000`:
```
cd frontend
npm install
npm run start
```

4. Run server at port `5001`:

```
cd server
pip install -r requirements.txt
python app.py
```
