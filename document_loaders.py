from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import TokenTextSplitter

def docx_loader(path):
    loader = Docx2txtLoader(path)
    data = loader.load()
    return data


def pdf_loader(path):
    loader = PyPDFLoader(path)
    pages = loader.load_and_split()
    return pages


def txt_splitter(doc):
    text_splitter = TokenTextSplitter(chunk_size=10000, chunk_overlap=30)
    page_data = doc[0]
    texts = text_splitter.split_text(page_data.page_content)

    return texts


