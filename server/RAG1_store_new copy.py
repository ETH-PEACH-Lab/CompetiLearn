import sys
import nbformat
import os
from langchain.document_loaders import WikipediaLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings

print(sys.version)

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content[:60]}...', metadata={self.metadata})"

def get_metadata(notebook_path, markdown_content, first_cell_index):
    filename = os.path.basename(notebook_path)
    title = filename.replace('.ipynb', '')
    source = f"https://example.com/{filename}"
    return {
        'title': title,
        'summary': markdown_content,
        'source': source,
        'first_cell_index': str(first_cell_index) if first_cell_index is not None else 'None'
    }

def extract_notebook_content(path_to_notebook):
    with open(path_to_notebook, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        documents = []
        content_accumulator = ""
        first_cell_index = None
        last_cell_type = None
        cell_index = 0

        for cell in nb['cells']:
            if first_cell_index is None:
                first_cell_index = cell_index
            
            if cell['cell_type'] == 'markdown':
                if last_cell_type == 'code':
                    metadata = get_metadata(path_to_notebook, content_accumulator, first_cell_index)
                    document = Document(content_accumulator, metadata)
                    documents.append(document)
                    content_accumulator = ""
                    first_cell_index = None
                content_accumulator += cell['source'] + "\n\n"
                last_cell_type = 'markdown'
            elif cell['cell_type'] == 'code':
                content_accumulator += cell['source'] + "\n\n"
                last_cell_type = 'code'

            cell_index += 1

        if content_accumulator:
            metadata = get_metadata(path_to_notebook, content_accumulator, first_cell_index)
            document = Document(content_accumulator, metadata)
            documents.append(document)

    return documents

# Usage example
directory = 'F:/Desktop/PHD/RAG_project/RAG_project2/competition_19988_filter'
all_documents = []

for filename in os.listdir(directory):
    if filename.endswith(".ipynb"):
        full_path = os.path.join(directory, filename)
        doc_list = extract_notebook_content(full_path)
        all_documents.extend(doc_list)

embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'),
                              model='text-embedding-ada-002',
                              chunk_size=100)

store = Chroma.from_documents(
    all_documents, 
    embeddings, 
    ids=[f"{item.metadata['source']}-{index}" for index, item in enumerate(all_documents)],
    collection_name="kaggle_competition", 
    persist_directory='F:/Desktop/PHD/RAG_project/RAG_project2/ChromDB/19988_filter',
)
store.persist()
print('store success!')