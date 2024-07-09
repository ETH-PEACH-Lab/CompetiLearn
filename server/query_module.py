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

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

SHOW_INTERMEDIATE_LOG = os.getenv("SHOW_INTERMEDIATE_LOG", "True").lower() in ("true", "1")

# Load the data once and cache it
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file
csv_path = os.path.abspath(os.path.join(current_dir, '../data/middle_file3.csv'))
persist_directory = os.path.abspath(os.path.join(current_dir, '../data/ChromDB/10737_filter_revise'))
profile_images_folder = os.path.join(current_dir, '../data/profile_images_10737')


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

class CustomRetriever(BaseRetriever):
    documents: List[Document] = Field(default_factory=list)

    def __init__(self, documents: List[Document]):
        super().__init__()
        self.documents = documents

    def get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Document]:
        return self.documents

def get_query_result_with_modes(query, search_mode='relevance', temperature=0.7):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002', chunk_size=100)
    store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    template = """
    Task: You are an expert in data science. Please answer questions about a Kaggle competition: "Quora Insincere Questions Classification" to help the user deal with his/her task, answer with code is preferable. \n
    Competition description: In this competition, Kagglers will develop models that identify and flag insincere questions. To date, Quora has employed both machine learning and manual review to address this problem. With your help, they can develop more scalable methods to detect toxic and misleading content.\n
    Note: The context includes other people's code that contains information necessary for answering the question. \n
    Please use only the provided context to answer the question. If the context do not provide any relevant information, you should state 'there is no relevant information in previous notebooks' and then you can answer by yourself.\n\n

    Context: {context} \n\n

    Question: {question}"""

    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOpenAI(temperature=temperature, model="gpt-4o", openai_api_key=os.environ.get('OPENAI_API_KEY'))

    if search_mode == 'relevance':
        retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 3})
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

    qa_with_source = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
    )

    result = qa_with_source(query)
    return result

def get_query_result_no_link(query, temperature=0.7):
    result = get_query_result_with_modes(query, temperature=temperature)
    result['source_documents'] = []
    return result

def get_query_result_gpt4o(query, temperature=0.7):
    openai_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        temperature=temperature
    )

    response = openai_response.choices[0].message.content

    return {
        "query": query,
        "result": response,
        "source_documents": []
    }

def get_query_result_gpt4o_stream(query, temperature=0.7):
    openai_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        temperature=temperature,
        stream=True
    )

    # Stream the response
    for chunk in openai_response:
        text = chunk.choices[0].delta.content
        if text:
            yield f"Result: {text}$EOL"


def get_query_result_rag_stream(query, search_mode='relevance', temperature=0.7, return_source=False):
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

        def task():
            try:
                result = llm_chain.invoke(query)
                print(f"Result source documents: {result['source_documents']}")
                source_documents_holder[0] = documents_to_json(result['source_documents'])
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

    def stream_generator():
        import codecs

        chat_response = ""
        for res_dict in stream_callback(query):
            yield res_dict
    
    yield from stream_generator()
