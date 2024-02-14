from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain, LLMChain, StuffDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import GigaChat
from api_getter import api_getter
import prompts


def summary(docs):
    token = api_getter()["access_token"]
    print(token)
    llm = GigaChat(access_token=token, verify_ssl_certs=False)

    map_template = prompts.MAP_SUM_PROMPT
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    # Reduce
    reduce_template = prompts.REDUCE_SUM_PROMPT
    reduce_prompt = PromptTemplate.from_template(reduce_template)

    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=20
    )
    split_docs = text_splitter.split_documents(docs)
    print('\n==============\n',split_docs, '\n==============\n')

    return map_reduce_chain.run(split_docs)


def qa_json_bilder_PDF(data):
    token = api_getter()["access_token"]
    print(token)
    llm = GigaChat(access_token=token, verify_ssl_certs=False, temperature=1)

    template = prompts.QA_JSON_PDF

    prompt = PromptTemplate(input_variables=['questions'], template=template)

    qa_chain = LLMChain(llm=llm, prompt=prompt)

    return qa_chain.run(data)


def qa_json_bilder_DOCX(data):
    token = api_getter()["access_token"]
    print(token)
    llm = GigaChat(access_token=token, verify_ssl_certs=False, temperature=1)

    template = prompts.QA_JSON_DOCX

    prompt = PromptTemplate(input_variables=['questions'], template=template)

    qa_chain = LLMChain(llm=llm, prompt=prompt)

    return qa_chain.run(data)


def qa_generation(docs):
    token = api_getter()["access_token"]
    print(token)
    llm = GigaChat(access_token=token, verify_ssl_certs=False)

    map_template = prompts.QA_MAP
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    # Reduce
    reduce_template = prompts.QA_MAP
    reduce_prompt = PromptTemplate.from_template(reduce_template)

    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=20
    )
    split_docs = text_splitter.split_documents(docs)
    print('\n==============\n', split_docs, '\n=============\n')

    print(map_reduce_chain.run(split_docs))

    return map_reduce_chain.run(split_docs)




