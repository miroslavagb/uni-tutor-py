from langchain.document_loaders import PyPDFLoader
from loader.document_loader import DocumentLoader


class PDFDocumentLoader(DocumentLoader):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def load(self):
        loader = PyPDFLoader(self.pdf_path)
        return loader.load()

    def load_pages(self):
        loader = PyPDFLoader(self.pdf_path)
        return loader.load_and_split()
