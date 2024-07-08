import sys
import nbformat
import os
from langchain.document_loaders import WikipediaLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings

print(sys.version)
directory = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/competition_10737_filter'

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content[:60]}...', metadata={self.metadata})"

def get_metadata(notebook_path, content, first_cell_index):
    filename = os.path.basename(notebook_path)
    title = filename.replace('.ipynb', '')
    source = directory + f"/{filename}"
    return {
        'title': title,
        'summary': content[:60] + '...',  # Or a different summary logic
        'source': source,
        'first_cell_index': str(first_cell_index) if first_cell_index is not None else 'None'
    }

def extract_notebook_content(path_to_notebook):
    with open(path_to_notebook, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        documents = []
        content_accumulator = ""
        first_cell_index = None
        in_code_section = False

        for cell_index, cell in enumerate(nb['cells']):
            if cell['cell_type'] == 'markdown':
                # If we are currently in a code section, it means we've just finished a chunk
                if in_code_section and content_accumulator:
                    # Save the document before processing the next markdown cell
                    metadata = get_metadata(path_to_notebook, content_accumulator, first_cell_index)
                    document = Document(content_accumulator, metadata)
                    documents.append(document)
                    # Reset accumulators
                    content_accumulator = ""
                    first_cell_index = None
                    in_code_section = False

                # Start accumulating content for the new document
                if first_cell_index is None:
                    first_cell_index = cell_index
                content_accumulator += cell['source'] + "\n\n"
            elif cell['cell_type'] == 'code':
                in_code_section = True
                content_accumulator += cell['source'] + "\n\n"

        # Check if there is any accumulated content left
        if content_accumulator:
            metadata = get_metadata(path_to_notebook, content_accumulator, first_cell_index)
            document = Document(content_accumulator, metadata)
            documents.append(document)

    return documents

# Usage example
all_documents = []

for filename in os.listdir(directory):
    if filename.endswith(".ipynb"):
        full_path = os.path.join(directory, filename)
        doc_list = extract_notebook_content(full_path)
        all_documents.extend(doc_list)

# Define the embedding with chunk size
embedding = OpenAIEmbeddings(show_progress_bar=True, chunk_size=100, openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002')

def split_list(input_list, chunk_size):
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]

# Adjust chunk size to handle the maximum batch size limitation
chunk_size = 5000  # Set to a value below the maximum batch size to avoid issues
split_docs_chunked = split_list(all_documents, chunk_size)

persist_directory = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/ChromDB/10737_filter_revise'

for split_docs_chunk in split_docs_chunked:
    vectordb = Chroma.from_documents(
        documents=split_docs_chunk,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()

print('Store success!')
