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
from datetime import datetime
import fcntl


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
log_path = os.path.join(current_dir, '../record/log.txt')

def read_csv_with_lock(path):
    with open(path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        df = pd.read_csv(file)
        fcntl.flock(file, fcntl.LOCK_UN)
    return df

middle_df = read_csv_with_lock(csv_path)
# middle_df = pd.read_csv(csv_path)

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


def get_kernel_score(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalVotes']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalVotes']
    else:
        return 0

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

def get_kernel_comment(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalComments']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalComments']
    else:
        return "default"
    
def get_kernel_title(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['Title']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['Title']
    else:
        return "default"
def get_date_difference(made_public_date_str):
    made_public_date = datetime.strptime(made_public_date_str, '%m/%d/%Y')
    current_date = datetime.now()
    difference = current_date - made_public_date
    
    days = difference.days
    weeks = days // 7
    months = days // 30
    years = days // 365
    
    if days < 7:
        return f"{days}d ago"
    elif days < 30:
        return f"{weeks} weeks ago"
    elif days < 365:
        return f"{months}m ago"
    else:
        return f"{years}y ago"

def get_kernel_date(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['MadePublicDate']]
    
    if not result.empty:
        made_public_date_str = result.iloc[0]['MadePublicDate']
        return get_date_difference(made_public_date_str)
    else:
        return "default"
def get_profile_image_path(username):
    # profile_images_dir = '/app/data/profile_images_10737'
    # profile_images_dir = '../../profile_images_19988'
    image_path = os.path.join(profile_images_folder, f"{username}.jpg")
    if not os.path.exists(image_path):
        image_path = os.path.join(profile_images_folder, "default.jpg")
    return image_path

class CustomRetriever(BaseRetriever):
    documents: List[Document] = Field(default_factory=list)
    max_tokens: int = 1000 # maximum tokens for context

    def __init__(self, documents: List[Document], max_tokens: int = 1000):
        super().__init__()
        self.documents = documents
        self.max_tokens = max_tokens

    def get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Document]:
        # return self._truncate_documents(self.documents)
        return self.documents

    # def _truncate_documents(self, documents: List[Document]) -> List[Document]:
    #     total_tokens = 0
    #     truncated_documents = []
    #     tokenizer = tiktoken.get_encoding("cl100k_base")

    #     for doc in documents:
    #         doc_tokens = len(tokenizer.encode(doc.page_content))
    #         if total_tokens + doc_tokens <= self.max_tokens:
    #             truncated_documents.append(doc)
    #             total_tokens += doc_tokens
    #         else:
    #             truncated_content = tokenizer.decode(tokenizer.encode(doc.page_content)[:self.max_tokens - total_tokens])
    #             truncated_doc = Document(
    #                 page_content=truncated_content,
    #                 metadata=doc.metadata
    #             )
    #             truncated_documents.append(truncated_doc)
    #             break

    #     return truncated_documents



def store_query_data(query, response, session_id, ip_address, mode, search_mode, num_source_docs):
    timestamp = pd.Timestamp.now()
    data = {
        'timestamp': [timestamp],
        'session_id': [session_id],
        'ip_address': [ip_address],
        'mode': [mode],
        'search_mode': [search_mode],
        'num_source_docs': [num_source_docs],
        'query': [query],
        'response': [response]
    }
    df = pd.DataFrame(data)
    with open(record_path, 'a') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        if not os.path.exists(record_path) or os.stat(record_path).st_size == 0:
            df.to_csv(file, index=False)
        else:
            df.to_csv(file, mode='a', header=False, index=False)
        fcntl.flock(file, fcntl.LOCK_UN)


def store_clear_history_signal(session_id, ip_address):
    timestamp = pd.Timestamp.now()
    data = {
        'timestamp': [timestamp],
        'session_id': [session_id],
        'ip_address': [ip_address],
        'mode': ['clear_history'],
        'search_mode': ['N/A'],
        'query': ['N/A'],
        'response': ['N/A']
    }
    df = pd.DataFrame(data)
    with open(record_path, 'a') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        if not os.path.exists(record_path) or os.stat(record_path).st_size == 0:
            df.to_csv(file, index=False)
        else:
            df.to_csv(file, mode='a', header=False, index=False)
        fcntl.flock(file, fcntl.LOCK_UN)



def get_history(session_id, mode, limit=3):
    def truncate_text(text: str, max_tokens: int) -> str:
        if not isinstance(text, str):
            text = str(text)
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(text)
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
        return tokenizer.decode(tokens)


    if not os.path.exists(record_path):
        return ""
    
    with open(record_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        df = pd.read_csv(file)
        fcntl.flock(file, fcntl.LOCK_UN)
    # df = pd.read_csv(record_path)
    session_records = df[df['session_id'] == session_id].iloc[::-1]
    
    history = []
    count = 0

    for i in range(len(session_records)):
        if session_records.iloc[i]['mode'] == 'clear_history':
            break
        if session_records.iloc[i]['mode'] != mode:
            break
        truncate_query = truncate_text(session_records.iloc[i]['query'], 300)
        truncated_response = truncate_text(session_records.iloc[i]['response'], 300)
        history.append(f"user query: {truncate_query}\nsystem response: {truncated_response}\n")
        count += 1
        if count >= limit:
            break

    if history:
        return "Previous conversation:\n" + "\n".join(history[::-1]) + "\n"
    return ""

def get_query_result_gpt4o_stream(query, temperature=0.7, mode=None):
    session_id = session.get('session_id')
    history = get_history(session_id, mode, limit=3)
    # print(f"Previous conversation: {history}")
    log_to_file(f"Previous conversation: {history}")
    pre_query = """Task: You are an expert in data science. Please answer questions about a Kaggle competition: "Quora Insincere Questions Classification" to help the user deal with his/her task, answer with code is preferable. \n
    Competition description: In this competition, Kagglers will develop models that identify and flag insincere questions. To date, Quora has employed both machine learning and manual review to address this problem. With your help, they can develop more scalable methods to detect toxic and misleading content.\n"""
    query = f"{pre_query}{history}Question: {query}"

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
    
    ip_address = request.remote_addr
    store_query_data(query, response_text, session_id, ip_address, mode, 'N/A','N/A')

def truncate_documents(documents: List[Document], max_tokens: int) -> List[Document]:
    total_tokens = 0
    truncated_documents = []
    tokenizer = tiktoken.get_encoding("cl100k_base")

    for doc in documents:
        doc_tokens = len(tokenizer.encode(doc.page_content))
        if total_tokens + doc_tokens <= max_tokens:
            truncated_documents.append(doc)
            total_tokens += doc_tokens
        else:
            truncated_content = tokenizer.decode(tokenizer.encode(doc.page_content)[:max_tokens - total_tokens])
            truncated_doc = Document(
                page_content=truncated_content,
                metadata=doc.metadata
            )
            truncated_documents.append(truncated_doc)
            break

    return truncated_documents
def log_to_file(log_message):
    with open(log_path, "a") as log_file:
        log_file.write(log_message + "\n")
def get_query_result_rag_stream(query, search_mode='relevance', temperature=0.7, return_source=False, mode=None,num_source_docs=3):
    if mode == 'rag_without_link':
        search_mode = 'relevance'
        num_source_docs = 3
        print(f"num_source_docs: {num_source_docs}")
    original_query = query
    session_id = session.get('session_id')
    history = get_history(session_id, mode, limit=3)
    # print(f"History: {history}")

    combined_query = f"{history}Question: {original_query}"
    
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002', chunk_size=100)
    store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    template = """Task: You are an expert in data science. Please answer questions about a Kaggle competition: "Quora Insincere Questions Classification" to help the user deal with his/her task, answer with code is preferable. \n
    Competition description: In this competition, Kagglers will develop models that identify and flag insincere questions. To date, Quora has employed both machine learning and manual review to address this problem. With your help, they can develop more scalable methods to detect toxic and misleading content.\n
    Note: The context includes other people's code that contains information necessary for answering the question. \n
    Please only use the provided context to answer the question. Assuming all the question is about this specific competition. If the context is empty, you should state 'there is no relevant information in previous notebooks' and then you can answer by yourself.\n\n

    Context: {context} \n\n

    {question}"""

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
        docs = store.search(original_query, search_type="mmr", k=num_source_docs)
        log_to_file("Documents retrieved:" + str(docs))  # Print the retrieved documents
        truncated_docs = truncate_documents(docs, max_tokens=1000)
        retriever = CustomRetriever(documents=truncated_docs)
    else:
        docs = store.search(original_query, search_type="mmr", k=10)
        if search_mode == 'votes':
            for doc in docs:
                doc.metadata['votes'] = get_kernel_vote(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('votes', 0), reverse=True)[:num_source_docs]
        elif search_mode == 'views':
            for doc in docs:
                doc.metadata['views'] = get_kernel_view(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('views', 0), reverse=True)[:num_source_docs]
        truncated_docs = truncate_documents(docs, max_tokens=1000)
        retriever = CustomRetriever(documents=truncated_docs)
        # retriever = CustomRetriever(documents=docs)
    # truncated_docs = truncate_documents(docs, max_tokens=1000)
    source_documents_json = documents_to_json(truncated_docs)
    # source_documents_json = documents_to_json(docs)
    log_to_file("Source documents:" + str(source_documents_json))
    llm_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )


    def stream_callback(combined_query):
        finished = object()
        response_text = ""

        def task():
            nonlocal response_text
            try:
                result = llm_chain.invoke(combined_query)
                # print(f"Result source documents: {result['source_documents']}")
                source_documents_holder[0] = documents_to_json(result['source_documents'])
                response_text = result['result']
                output_queue.put(finished)
            except Exception as e:
                print(f"LLM chain error: {e}")
                log_to_file(f"LLM chain error: {e}")
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
            yield f"Source: {source_documents_json}$EOL"
        
        # session_id = session.get('session_id')
        ip_address = request.remote_addr
        store_query_data(original_query, response_text, session_id, ip_address, mode, search_mode,num_source_docs)


    def stream_generator():
        for res_dict in stream_callback(combined_query):
            yield res_dict
    
    yield from stream_generator()