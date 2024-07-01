from flask import Flask, request, jsonify
from flask_cors import CORS
from query_module import get_query_result, get_query_result_no_link, get_query_result_gpt4o
from kaggle_post_retrieve_module import get_kernel_url
import nbformat
app = Flask(__name__)
CORS(app)

def document_to_dict(doc):
    return {
        'page_content': doc.page_content,
        'metadata': doc.metadata
    }

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    mode = data.get('mode', 'rag_with_link')
    print(f'Received search query: {query}, mode: {mode}')
    
    # Call the appropriate query function based on the mode
    if mode == 'rag_with_link':
        result = get_query_result(query)
    elif mode == 'rag_without_link':
        result = get_query_result_no_link(query)
    elif mode == 'gpt4o':
        result = get_query_result_gpt4o(query)
    else:
        return jsonify({'error': 'Invalid mode specified'}), 400
    
    # Convert the result to a JSON serializable format
    result_serializable = {
        'query': result.get('query', ''),
        'result': result.get('result', ''),
        'source_documents': [document_to_dict(doc) for doc in result.get('source_documents', [])]
    }
    
    print(result_serializable)
    
    return jsonify(result_serializable)

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

    # Fetch cells from the current index downward until the first code cell is found
    for i in range(cell_index, len(cells)):
        cell_contents.append(cells[i])
        if cells[i].cell_type == 'code':
            code_lines_count += len(cells[i].source.split('\n'))
            if code_lines_count >= 5:
                break

    # If less than 5 lines of code are fetched, fetch from the current index upward
    if code_lines_count < 5:
        additional_cells = []
        for i in range(cell_index - 1, -1, -1):
            additional_cells.insert(0, cells[i])
            if cells[i].cell_type == 'code':
                code_lines_count += len(cells[i].source.split('\n'))
                cell_contents = additional_cells + cell_contents
                if code_lines_count >= 5:
                    break

    if cell_contents:
        return cell_contents
    else:
        return {'error': f'Notebook does not have enough cells.'}



@app.route('/get_cell_content', methods=['GET'])
def get_cell_content_endpoint():
    notebook_title = request.args.get('title')
    cell_index = int(request.args.get('cell_index'))

    # Ensure the notebook title includes the .ipynb extension
    if not notebook_title.endswith('.ipynb'):
        notebook_title += '.ipynb'
    
    notebook_path = f'F:/Desktop/PHD/RAG_project/RAG_project5/competition_19988_filter/{notebook_title}'
    
    try:
        cell_content = get_cell_content(notebook_path, cell_index)
        return jsonify(cell_content)
    except FileNotFoundError:
        return jsonify({'error': f'Notebook {notebook_title} not found.'}), 404




if __name__ == '__main__':
    app.run(debug=True)
