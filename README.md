# README

## How to Run the Tool
1. Download the `data.zip` and unzip it to `./data`
2. Create `./server/.env.local` for the OPENAI API
- `export OPENAI_API_KEY=DONTSHAREWITHOTHERS`
3. Run frontend at port `5001`:
- `cd frontend`
- `npm install`
- `npm run start`
4. Run server at port `3000`:
- `cd server`
- `python install -r requirements.txt`
- `python app.py`