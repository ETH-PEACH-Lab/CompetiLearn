from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from openai import OpenAI
import pandas as pd
from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field
import os
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

# Function to get kernel votes
def get_username(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['UserName']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['UserName']
    else:
        print("No username found.")
        return "default"

def get_profile_image_path(username):
    profile_images_dir = 'F:/Desktop/PHD/RAG_project/RAG_project5/profile_images_19988'
    image_path = os.path.join(profile_images_dir, f"{username}.jpg")
    if not os.path.exists(image_path):
        image_path = os.path.join(profile_images_dir, "default.jpg")
    return image_path

def get_kernel_vote(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalVotes']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalVotes']
    else:
        print("No votes found.")
        return 0

# Function to get kernel views
def get_kernel_view(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalViews']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalViews']
    else:
        print("No views found.")
        return 0

# Custom retriever class
class CustomRetriever(BaseRetriever):
    documents: List[Document] = Field(default_factory=list)

    def __init__(self, documents: List[Document]):
        super().__init__()
        self.documents = documents

    def get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Document]:
        return self.documents

def get_query_result(query, temperature=0.7):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002', chunk_size=100)
    store = Chroma(collection_name='kaggle_competition', persist_directory='F:/Desktop/PHD/RAG_project/RAG_project5/ChromDB/19988_filter_revise', embedding_function=embeddings)

    template = """You are a bot that answers questions about a Kaggle competition. 
    The context includes other people's code that contains information necessary for answering the question. 
    Please use only the provided context to answer the question. If you don't know the answer, simply state that you don't know.\n\n

    Context: {context} \n\n

    Question: {question}"""

    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOpenAI(temperature=temperature, model="gpt-4o", openai_api_key=os.environ.get('OPENAI_API_KEY'))

    qa_with_source = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=store.as_retriever(search_type="mmr", search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
    )

    result = qa_with_source(query)
    return result

def get_query_result_no_link(query, temperature=0.7):
    # Similar to get_query_result but without returning the source documents
    result = get_query_result(query, temperature)
    result['source_documents'] = []
    return result

def get_query_result_gpt4o(query, temperature=0.7):
    """
    Uses GPT-4o to answer the query and returns the response in the expected format.

    Args:
        query: The user's query string.
        temperature: The temperature setting for the model.

    Returns:
        A dictionary containing the query, response, and empty source_documents list.
    """

    # Replace with your actual OpenAI API call
    openai_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        temperature=temperature
    )

    # Extract the GPT-4o generated response
    response = openai_response.choices[0].message.content

    # Return the result in the expected dictionary format
    return {
        "query": query,
        "result": response,
        "source_documents": []
    }

# New function to handle different search modes
def get_query_result_with_modes(query, search_mode='relevance', temperature=0.7):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002', chunk_size=100)
    store = Chroma(collection_name='kaggle_competition', persist_directory='F:/Desktop/PHD/RAG_project/RAG_project5/ChromDB/19988_filter_revise', embedding_function=embeddings)

    template = """You are a bot that answers questions about a Kaggle competition. 
    The context includes other people's code that contains information necessary for answering the question. 
    Please use only the provided context to answer the question. If you don't know the answer, simply state that you don't know.\n\n

    Context: {context} \n\n

    Question: {question}"""

    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOpenAI(temperature=temperature, model="gpt-4o", openai_api_key=os.environ.get('OPENAI_API_KEY'))

    if search_mode == 'relevance':
        retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 3})
    else:
        docs = store.search(query, search_type="mmr", k=10)
        # print("Documents retrieved:", docs)  # Print the retrieved documents
        if search_mode == 'votes':
            for doc in docs:
                doc.metadata['votes'] = get_kernel_vote(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('votes', 0), reverse=True)[:3]
        elif search_mode == 'views':
            for doc in docs:
                doc.metadata['views'] = get_kernel_view(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('views', 0), reverse=True)[:3]

        # print("Documents after sorting:", docs)  # Print the sorted documents

        # Create a custom retriever
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
