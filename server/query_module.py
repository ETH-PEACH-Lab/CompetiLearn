import pandas as pd
import os
from typing import List
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from openai import OpenAI
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain.callbacks.base import BaseCallbackHandler
from queue import Queue
from threading import Thread
import json
from utils import documents_to_json
import sys
from pydantic import Field
import tiktoken
from flask import request, session

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

SHOW_INTERMEDIATE_LOG = os.getenv("SHOW_INTERMEDIATE_LOG", "True").lower() in ("true", "1")

# Load the data once and cache it
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file
csv_path = os.path.abspath(os.path.join(current_dir, '../data/middle_file3.csv'))
persist_directory = os.path.abspath(os.path.join(current_dir, '../data/ChromDB/10737_filter_revise_python'))
profile_images_folder = os.path.join(current_dir, '../data/profile_images_10737')
record_path = os.path.join(current_dir, '../record/record.csv')

middle_df = pd.read_csv(csv_path)

class QueueCallbackHandler(BaseCallbackHandler):
    """A queue that holds the result answer token buffer for streaming response."""

    def __init__(self, queue: Queue):
        self.queue = queue
        self.enter_answer_phase = False

    def on_llm_new_token(self, token: str, **kwargs):
        sys.stdout.write(token)
        sys.stdout.flush()
        self.queue.put(token)

    def on_llm_end(self, *args, **kwargs):
        self.enter_answer_phase = not self.enter_answer_phase
        return True

def get_kernel_vote(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalVotes']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalVotes']
    else:
        return 0

def get_kernel_view(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalViews']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalViews']
    else:
        return 0

def get_username(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['UserName']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['UserName']
    else:
        return "default"

def get_profile_image_path(username):
    # profile_images_dir = '/app/data/profile_images_10737'
    # profile_images_dir = '../../profile_images_19988'
    image_path = os.path.join(profile_images_folder, f"{username}.jpg")
    if not os.path.exists(image_path):
        image_path = os.path.join(profile_images_folder, "default.jpg")
    return image_path

def truncate_context(context: str, max_tokens: int = 1000) -> str:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(context)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return tokenizer.decode(tokens)

class CustomRetriever(BaseRetriever):
    documents: List[Document] = Field(default_factory=list)
    max_tokens: int = 1000 # maximum tokens for context

    def __init__(self, documents: List[Document], max_tokens: int = 1000):
        super().__init__()
        self.documents = documents
        self.max_tokens = max_tokens

    def get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Document]:
        return self._truncate_documents(self.documents)

    def _truncate_documents(self, documents: List[Document]) -> List[Document]:
        total_tokens = 0
        truncated_documents = []
        tokenizer = tiktoken.get_encoding("cl100k_base")

        for doc in documents:
            doc_tokens = len(tokenizer.encode(doc.page_content))
            if total_tokens + doc_tokens <= self.max_tokens:
                truncated_documents.append(doc)
                total_tokens += doc_tokens
            else:
                truncated_content = tokenizer.decode(tokenizer.encode(doc.page_content)[:self.max_tokens - total_tokens])
                truncated_documents.append(Document(page_content=truncated_content))
                break
        
        return truncated_documents

def store_query_data(query, response, session_id, ip_address):
    timestamp = pd.Timestamp.now()
    data = {
        'timestamp': [timestamp],
        'session_id': [session_id],
        'ip_address': [ip_address],
        'query': [query],
        'response': [response]
    }
    df = pd.DataFrame(data)
    if not os.path.exists(record_path):
        df.to_csv(record_path, index=False)
    else:
        df.to_csv(record_path, mode='a', header=False, index=False)
def store_query_data(query, response, session_id, ip_address, mode, search_mode):
    timestamp = pd.Timestamp.now()
    data = {
        'timestamp': [timestamp],
        'session_id': [session_id],
        'ip_address': [ip_address],
        'mode': [mode],
        'search_mode': [search_mode],
        'query': [query],
        'response': [response]
        
    }
    df = pd.DataFrame(data)
    if not os.path.exists(record_path):
        df.to_csv(record_path, index=False)
    else:
        df.to_csv(record_path, mode='a', header=False, index=False)
def get_query_result_gpt4o_stream(query, temperature=0.7,mode='gpt4o'):
    openai_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        temperature=temperature,
        stream=True
    )

    response_text = ''
    for chunk in openai_response:
        text = chunk.choices[0].delta.content
        if text:
            response_text += text
            yield f"Result: {text}$EOL"
    
    session_id = session.get('session_id')
    ip_address = request.remote_addr
    store_query_data(query, response_text, session_id, ip_address, mode, 'N/A')



def get_query_result_rag_stream(query, search_mode='relevance', temperature=0.7, return_source=False, mode=None):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002', chunk_size=100)
    store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    template = """Task: You are an expert in data science. Please answer questions about a Kaggle competition: "Quora Insincere Questions Classification" to help the user deal with his/her task, answer with code is preferable. \n
    Competition description: In this competition, Kagglers will develop models that identify and flag insincere questions. To date, Quora has employed both machine learning and manual review to address this problem. With your help, they can develop more scalable methods to detect toxic and misleading content.\n
    Note: The context includes other people's code that contains information necessary for answering the question. \n
    Please only use the provided context to answer the question. Assuming all the question is about this specific competition. If the context is empty, you should state 'there is no relevant information in previous notebooks' and then you can answer by yourself.\n\n

    Context: {context} \n\n

    Question: {question}"""

    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])
    output_queue = Queue()
    source_documents_holder = [None]

    llm = ChatOpenAI(
        temperature=temperature, 
        model="gpt-4o", 
        openai_api_key=os.environ.get('OPENAI_API_KEY'),
        callbacks=[QueueCallbackHandler(output_queue)],
        streaming=True
    )

    if search_mode == 'relevance':
        docs = store.search(query, search_type="mmr", k=3)
        print("Documents retrieved:", docs)  # Print the retrieved documents
        retriever = CustomRetriever(documents=docs)
    else:
        docs = store.search(query, search_type="mmr", k=10)
        if search_mode == 'votes':
            for doc in docs:
                doc.metadata['votes'] = get_kernel_vote(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('votes', 0), reverse=True)[:3]
        elif search_mode == 'views':
            for doc in docs:
                doc.metadata['views'] = get_kernel_view(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('views', 0), reverse=True)[:3]

        retriever = CustomRetriever(documents=docs)
    llm_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )


    def stream_callback(query):
        finished = object()
        response_text = ""

        def task():
            nonlocal response_text
            try:
                result = llm_chain.invoke(query)
                print(f"Result source documents: {result['source_documents']}")
                source_documents_holder[0] = documents_to_json(result['source_documents'])
                response_text = result['result']
                output_queue.put(finished)
            except Exception as e:
                print(f"LLM chain error: {e}")
                output_queue.put("\nInternal Server Error\n")
                output_queue.put(finished)

        t = Thread(target=task)
        t.start()

        while True:
            try:
                item = output_queue.get()
                if item is finished:
                    break
                yield f"Result: {item}$EOL"
            except Queue.Empty:
                continue
        if return_source:
            yield f"Source: {source_documents_holder[0]}$EOL"
        
        session_id = session.get('session_id')
        ip_address = request.remote_addr
        store_query_data(query, response_text, session_id, ip_address, mode, search_mode)


    def stream_generator():
        for res_dict in stream_callback(query):
            yield res_dict
    
    yield from stream_generator()