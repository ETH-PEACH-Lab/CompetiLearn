from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import pprint
# from langchain.vectorstores import Chroma
from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
import os
# template = """You are a bot that answers questions about Wimbledon 2023, using only the context provided.
# If you don't know the answer, simply state that you don't know.

# {context}

# Question: {question}"""

# PROMPT = PromptTemplate(
#     template=template, input_variables=["context", "question"]
# )

embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'),
                              model = 'text-embedding-ada-002',
                                 chunk_size = 100) #each time submit chunk is depend on this chunk size
store = Chroma(persist_directory='/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/ChromDB/10737_filter_revise', embedding_function=embeddings)
# 'Mechanisms of Action (MoA) Prediction'
template = """You are a bot that answers questions about a Kaggle competition. 
The context includes other people's code that contains information necessary for answering the question. 
Please use only the provided context to answer the question. If you don't know the answer, simply state that you don't know.\n\n

Context: {context} \n\n

Question: {question}"""

PROMPT = PromptTemplate(
    template=template, input_variables=["context", "question"]
)

llm = ChatOpenAI(temperature=0, model="gpt-4-turbo",openai_api_key=os.environ.get('OPENAI_API_KEY'))

qa_with_source = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=store.as_retriever(
    search_type="mmr",  # max marginal relevance, Also test "similarity"
    search_kwargs={"k": 3},
    ),
    chain_type_kwargs={"prompt": PROMPT, },
    return_source_documents=True,
)

# 加一个kernel id-----能够返回确定的文件位置 todo
# vote的filter--------马太效应-----kernel id------前端查vote number
#精准定位cell

# pprint.pprint(
#     qa_with_source("how to check if some features is correlated?")
# )



# pprint.pprint(
#     qa_with_source("how to load the data?")  #need the markdown to specify the information
# )

# pprint.pprint(
#     qa_with_source("how to do principle component analysis?")  #need the markdown to specify the information
# )

# pprint.pprint(
#     qa_with_source("how many columns do we have in the dataset?")  #need the markdown to specify the information
# )

pprint.pprint(
    qa_with_source("What kind of analysis can we do for this data?")  #need the markdown to specify the information
)