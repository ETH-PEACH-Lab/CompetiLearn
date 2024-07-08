import pandas as pd
from typing import List
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from openai import OpenAI
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

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

class CustomRetriever(BaseRetriever):
    documents: List[Document] = Field(default_factory=list)

    def __init__(self, documents: List[Document]):
        super().__init__()
        self.documents = documents

    def get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Document]:
        return self.documents

def get_query_result(query, search_mode='relevance', temperature=0.7):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'), model='text-embedding-ada-002', chunk_size=100)
    store = Chroma(collection_name='kaggle_competition', persist_directory='F:/Desktop/PHD/RAG_project/RAG_project5/ChromDB/profile_images_10737_filter_revise', embedding_function=embeddings)

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
        print("Documents retrieved:", docs)  # Print the retrieved documents
        if search_mode == 'votes':
            for doc in docs:
                doc.metadata['votes'] = get_kernel_vote(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('votes', 0), reverse=True)[:3]
        elif search_mode == 'views':
            for doc in docs:
                doc.metadata['views'] = get_kernel_view(doc.metadata['title'])
            docs = sorted(docs, key=lambda x: x.metadata.get('views', 0), reverse=True)[:3]

        print("Documents after sorting:", docs)  # Print the sorted documents

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

def test_query_modes(query, mode):
    print(f"Testing mode: {mode}")
    result = get_query_result(query, search_mode=mode)
    print(f"Query: {result['query']}")
    print(f"Result: {result['result']}")
    print(f"Source Documents: {result['source_documents']}\n")

if __name__ == "__main__":
    example_query = "how to analyze the data?"
    modes = ['votes', 'views']

    for mode in modes:
        test_query_modes(example_query, mode)
