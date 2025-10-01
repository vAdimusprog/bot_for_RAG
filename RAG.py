from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader



class Model():
    pass

class Text():
    def __init__(self, name):
        self.name = name
        self.docs = []


    def procces(self):

        loader = TextLoader(self.name, encoding="utf-8")
        documents = loader.load()

        # Если файл большой - разделить на чанки
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )
        docs = text_splitter.split_documents(documents)

        self.docs = docs

    def get_docs(self):
        return self.docs


txt = Text("saved_txt.txt")
txt.procces()
print(txt.get_docs())
