import sys
import nbformat
import os
from langchain.document_loaders import WikipediaLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings

print(sys.version)
directory = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/competition_10737_filter_python'
class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content[:60]}...', metadata={self.metadata})"

def get_metadata(notebook_path, content, first_cell_index):
    filename = os.path.basename(notebook_path)
    title = filename.replace('.ipynb', '')
    source = directory+f"/{filename}"
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
# directory = 'F:/Desktop/PHD/RAG_project/RAG_project2/competition_profile_images_10737_filter'
all_documents = []

for filename in os.listdir(directory):
    if filename.endswith(".ipynb"):
        full_path = os.path.join(directory, filename)
        doc_list = extract_notebook_content(full_path)
        all_documents.extend(doc_list)

embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'),
                              model='text-embedding-ada-002',
                              chunk_size=70)

store = Chroma.from_documents(
    all_documents, 
    embeddings, 
    ids=[f"{item.metadata['source']}-{index}" for index, item in enumerate(all_documents)],
    collection_name="kaggle_competition", 
    persist_directory='/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/ChromDB/10737_filter_revise_python',
)
store.persist()
print('store success!')
