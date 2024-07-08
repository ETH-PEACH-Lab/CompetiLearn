# README

## How to Run the Tool
1. Download the `data.zip` and unzip it to `./data`

<<<<<<< HEAD
2. Create `./.env` for the OPENAI API

```
# .env
OPENAI_API_KEY=YOUR_API_KEY

```
3. Build docker
```
docker-compose build
```
5. Run docker
```
docker-compose up
=======
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
>>>>>>> origin/styling
```
