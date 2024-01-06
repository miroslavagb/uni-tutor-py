import os

import bs4
from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.vectorstores import Chroma

from loader.pdf_document_loader import PDFDocumentLoader

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# docs = WebDocumentLoader(
#     web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             class_=("post-content", "post-title", "post-header")
#         )
#     ),
# )

docs = PDFDocumentLoader("advanced-alg-758.pdf")
# docs = PDFDocumentLoader("bitcoin-official.pdf")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs.load())

# split it into chunks
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0) - what's the difference?
# docs = text_splitter.split_documents(documents)

# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# load it into Chroma
vectorstore = Chroma.from_documents(splits, embedding_function, persist_directory="./chroma_db")

loaded_vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = loaded_vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def print_retrieved_context(retriever):
    retrieved_docs = retriever.get_relevant_documents("What is Wedderburn’s main theorem?")
    for doc in retrieved_docs:
        print("Retrieved Context:")
        print(doc.page_content)
        print("\n" + "=" * 50 + "\n")  # Separation line between documents


# Print the retrieved context
print_retrieved_context(retriever)

rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)
