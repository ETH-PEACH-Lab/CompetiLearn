from flask import Flask, request, jsonify, send_from_directory, stream_with_context, Response
from flask_cors import CORS
from flask_caching import Cache
from query_module import (
    get_username, get_kernel_vote, get_kernel_view,get_kernel_comment,get_kernel_title,get_kernel_date,
    get_profile_image_path, 
    get_query_result_gpt4o_stream, 
    get_query_result_rag_stream, store_clear_history_signal
)
from kaggle_post_retrieve_module import get_kernel_url
import os
import nbformat
from dotenv import load_dotenv
import time
from utils import document_to_dict
from flask import session
from flask_session import Session


current_dir = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(current_dir, '../.env')
load_dotenv(dotenv_path)

frontend_path = os.path.join(current_dir, '../frontend/build')
profile_images_folder = os.path.join(current_dir, '../data/profile_images_10737')
notebook_folder = os.path.join(current_dir, '../data/competition_10737_filter_python/')

print(f"Profile images folder: {profile_images_folder}")

app = Flask(__name__, static_folder=frontend_path, static_url_path='/')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')  # Ensure you have a secret key
app.config['SESSION_TYPE'] = 'filesystem'  # Using the filesystem to store sessions

# Initialize session management
Session(app)
# Configure CORS to allow requests from localhost:3000
CORS(app)

# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://10.6.130.123:3000"]}})

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

app.config['PROFILE_IMAGES_FOLDER'] = profile_images_folder

@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path='index.html'):
    try:
        return send_from_directory(app.static_folder, path)
    except FileNotFoundError:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/profile_images_10737/<filename>')
def serve_profile_image(filename):
    return send_from_directory(app.config['PROFILE_IMAGES_FOLDER'], filename)

@app.route('/get_username', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_username_endpoint():
    kernel_id = request.args.get('kernel_id')
    username = get_username(kernel_id)
    return jsonify(username)

@app.route('/get_kernel_vote', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_kernel_vote_endpoint():
    kernel_id = request.args.get('kernel_id')
    votes = get_kernel_vote(kernel_id)
    return jsonify(votes)

@app.route('/get_kernel_view', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_kernel_view_endpoint():
    kernel_id = request.args.get('kernel_id')
    views = get_kernel_view(kernel_id)
    return jsonify(views)

@app.route('/get_kernel_comment', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_kernel_comment_endpoint():
    kernel_id = request.args.get('kernel_id')
    comment = get_kernel_comment(kernel_id)
    return jsonify(comment)

@app.route('/get_kernel_title', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_kernel_title_endpoint():
    kernel_id = request.args.get('kernel_id')
    title = get_kernel_title(kernel_id)
    return jsonify(title)

@app.route('/get_kernel_date', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_kernel_date_endpoint():
    kernel_id = request.args.get('kernel_id')
    date = get_kernel_date(kernel_id)
    return jsonify(date)

@app.route('/get_profile_image_path', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_profile_image_path_endpoint():
    username = request.args.get('username')
    profile_image_path = get_profile_image_path(username)
    filename = os.path.basename(profile_image_path)
    return jsonify(filename)

def document_to_dict(doc):
    return {
        'page_content': doc.page_content,
        'metadata': doc.metadata
    }

# @app.route('/search', methods=['POST'])
# def search():
#     data = request.json
#     query = data.get('query', '')
#     mode = data.get('mode', 'rag_with_link')
#     temperature = data.get('temperature', 0.7)
#     search_mode = data.get('search_mode', 'relevance')
#     print(f'Received search query: {query}, mode: {mode}, search_mode: {search_mode}, temperature: {temperature}')
    
#     if mode == 'rag_with_link':
#         result = get_query_result_with_modes(query, search_mode, temperature)
#     elif mode == 'rag_without_link':
#         result = get_query_result_no_link(query, temperature)
#     elif mode == 'gpt4o':
#         result = get_query_result_gpt4o(query, temperature)
#     else:
#         return jsonify({'error': 'Invalid mode specified'}), 400
    
#     result_serializable = {
#         'query': result.get('query', ''),
#         'result': result.get('result', ''),
#         'source_documents': [document_to_dict(doc) for doc in result.get('source_documents', [])]
#     }
    
#     print(result_serializable)
    
#     return jsonify(result_serializable)

@app.route('/stream', methods=['POST'])
def stream():
    data = request.json
    query = data.get('query', '')
    mode = data.get('mode', 'rag_with_link')
    temperature = data.get('temperature', 0.7)
    search_mode = data.get('search_mode', 'relevance')
    num_source_docs = data.get('num_source_docs', 3)  # New parameter
    print(f'Received stream query: {query}, mode: {mode}, search_mode: {search_mode}, temperature: {temperature}, num_source_docs: {num_source_docs}')
    # Ensure session ID exists
    if 'session_id' not in session:
        session['session_id'] = os.urandom(24).hex()
        
    if mode == 'rag_with_link':
        result = Response(stream_with_context(get_query_result_rag_stream(query, search_mode, temperature, return_source=True,mode=mode, num_source_docs=num_source_docs)), content_type='text/event-strean')
        print('result:', result)    
    elif mode == 'rag_without_link':
        result = Response(stream_with_context(get_query_result_rag_stream(query, search_mode, temperature, return_source=False,mode=mode, num_source_docs=num_source_docs)), content_type='text/event-stream')
        print('result:', result)
    elif mode == 'gpt4o':
        result = Response(stream_with_context(get_query_result_gpt4o_stream(query, temperature,mode=mode)), content_type='text/event-stream')
        print('result:', result)
    return result

@app.route('/new_chat', methods=['POST'])
def new_chat():
    session_id = session.get('session_id')
    if session_id:
        # Add a row to record.csv to indicate clearing history
        ip_address = request.remote_addr
        store_clear_history_signal(session_id, ip_address)
    return jsonify({'status': 'success'}), 200


@app.route('/get_kernel_url', methods=['GET'])
def kernel_url():
    kernel_id = request.args.get('kernel_id')
    url = get_kernel_url(kernel_id)
    if url:
        return jsonify({'url': url})
    else:
        return jsonify({'error': 'Kernel ID not found'}), 404

def get_cell_content(notebook_path, cell_index):
    with open(notebook_path, 'r', encoding='utf-8') as file:
        notebook = nbformat.read(file, as_version=4)
    
    cells = notebook.cells
    cell_contents = []
    code_lines_count = 0

    # Fetch cells from the current index downward until at least 5 lines of code are found
    for i in range(cell_index, len(cells)):
        cell_contents.append(cells[i])
        if cells[i].cell_type == 'code':
            lines = cells[i].source.split('\n')
            code_lines_count += len(lines)
            if code_lines_count >= 5:
                break

    # If less than 5 lines of code are fetched, fetch from the current index upward
    if code_lines_count < 5:
        additional_cells = []
        for i in range(cell_index - 1, -1, -1):
            additional_cells.insert(0, cells[i])
            if cells[i].cell_type == 'code':
                lines = cells[i].source.split('\n')
                code_lines_count += len(lines)
                cell_contents = additional_cells + cell_contents
                if code_lines_count >= 5:
                    break

    # Trim excess lines if more than 5 lines are fetched
    final_cells = []
    accumulated_lines = 0
    for cell in cell_contents:
        if cell.cell_type == 'code':
            lines = cell.source.split('\n')
            if accumulated_lines + len(lines) > 5:
                lines_to_add = lines[:5 - accumulated_lines]
                cell.source = '\n'.join(lines_to_add)
                final_cells.append(cell)
                break
            else:
                accumulated_lines += len(lines)
                final_cells.append(cell)
        else:
            final_cells.append(cell)

    return final_cells

@app.route('/get_cell_content', methods=['GET'])
def get_cell_content_endpoint():
    notebook_title = request.args.get('title')
    cell_index_param = request.args.get('cell_index')

    # Ensure the notebook title includes the .ipynb extension
    if not notebook_title.endswith('.ipynb'):
        notebook_title += '.ipynb'
    
    # Handle potential ValueError for cell_index
    try:
        cell_index = int(cell_index_param)
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid cell index: {cell_index_param}'}), 400
    notebook_path = os.path.join(notebook_folder, notebook_title)
    try:
        cell_content = get_cell_content(notebook_path, cell_index)
        return jsonify(cell_content)
    except FileNotFoundError:
        return jsonify({'error': f'Notebook {notebook_title} not found. {notebook_path}'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)    # Change port to 5001