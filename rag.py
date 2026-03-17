from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import tempfile
import os

def pdf_isle(uploaded_files):
    tum_chunks = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)
        tum_chunks.extend(chunks)
        os.unlink(tmp_path)

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(tum_chunks, embeddings)
    return vectordb

def ozet_cikar(uploaded_file, dil="Türkçe"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    os.unlink(tmp_path)
    
    metin = " ".join([d.page_content for d in documents[:5]])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_template("""
Aşağıdaki metni {dil} dilinde 5 madde halinde özetle. 
Her madde tek cümle olsun.

Metin: {metin}
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"metin": metin[:3000], "dil": dil})

def soru_sor(vectordb, soru, dil="Türkçe"):
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_template("""
Aşağıdaki bağlamı kullanarak soruyu {dil} dilinde yanıtla.
Bağlamda cevap yoksa "{dil} dilinde: Bu bilgi belgede bulunmuyor." de.

Bağlam: {context}
Soru: {question}
""")
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough(), "dil": lambda _: dil}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain.invoke(soru)