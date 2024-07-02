# README

## How to Run the Tool
1. Download the `data.zip` and unzip it to `./data`

2. Create `./server/.env.local` for the OPENAI API

```
touch ./server/.env.local
export OPENAI_API_KEY=DONTSHAREWITHOTHERS
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
