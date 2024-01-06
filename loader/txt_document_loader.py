from langchain.document_loaders import TextLoader
from loader.document_loader import DocumentLoader


class TextDocumentLoader(DocumentLoader):
    def __init__(self, txt_path):
        self.txt_path = txt_path

    def load(self):
        loader = TextLoader(self.txt_path)
        return loader.load()
