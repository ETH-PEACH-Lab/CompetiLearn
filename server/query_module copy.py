# query_module.py
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
import os

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
print(OPENAI_API_KEY)

def get_query_result(query):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY,
                                  model='text-embedding-ada-002',
                                  chunk_size=100)  # each time submit chunk is depend on this chunk size
    store = Chroma(collection_name='kaggle_competition',
                   persist_directory='F:/Desktop/PHD/RAG_project/RAG_project5/ChromDB/19988_filter_revise',
                   embedding_function=embeddings)

    template = """You are a bot that answers questions about a Kaggle competition. 
    The context includes other people's code that contains information necessary for answering the question. 
    Please use only the provided context to answer the question. If you don't know the answer, simply state that you don't know.\n\n

    Context: {context} \n\n

    Question: {question}"""

    PROMPT = PromptTemplate(
        template=template, input_variables=["context", "question"]
    )

    llm = ChatOpenAI(temperature=0, model="gpt-4o", openai_api_key=os.environ.get('OPENAI_API_KEY'))

    qa_with_source = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=store.as_retriever(
            search_type="mmr",  # max marginal relevance, Also test "similarity"
            search_kwargs={"k": 3},
        ),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
    )

    result = qa_with_source(query)
    return result
