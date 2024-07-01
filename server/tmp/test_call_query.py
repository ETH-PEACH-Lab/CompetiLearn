# from flask import Flask, request, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# @app.route('/search', methods=['POST'])
# def search():
#     data = request.json
#     query = data.get('query', '')
#     print(f'Received search query: {query}')
#     return jsonify({'status': 'success', 'query': query})

# if __name__ == '__main__':
#     app.run(debug=True)

# app.py

from query_module import get_query_result  # Import the function from the module

query = 'how to load the data?'
print(f'Received search query: {query}')
    
result = get_query_result(query)
print(result)