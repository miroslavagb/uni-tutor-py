from langchain.document_loaders import WebBaseLoader
from loader.document_loader import DocumentLoader


class WebDocumentLoader(DocumentLoader):
    def __init__(self, web_paths, bs_kwargs=None):
        self.web_paths = web_paths
        self.bs_kwargs = bs_kwargs

    def load(self):
        loader = WebBaseLoader(web_paths=self.web_paths, bs_kwargs=self.bs_kwargs)
        return loader.load()
