import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from database.databaseHelper import TestSessionLocal
db = TestSessionLocal()
from database.db_classes import Diary


# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

diaries = db.query(Diary).all()
input_text = ""
for diary in diaries:
    input_text += f'''
    {diary.date}의 일기는 다음과 같다.
    {diary.content}\n
    '''

# Create a Document object
doc = Document(page_content=input_text)

# Split the document into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents([doc])

# Create embeddings and store them in a vector database
embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(texts, embeddings)

# Create a retriever
retriever = db.as_retriever()


def get_qa_chain(model_name="gpt-4o-mini"):
    """
    Create a QA chain with the specified model.
    Available models include:
    - gpt-3.5-turbo
    - gpt-3.5-turbo-16k
    - gpt-4
    - gpt-4-32k
    """
    llm = ChatOpenAI(model_name=model_name, temperature=0)

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )


# Example usage
model_name = "gpt-4o-mini"  # You can change this to any supported model
qa = get_qa_chain(model_name)

# Example usage
query = "7월에는 술을 몇 번이나 마셨어?"
result = qa({"query": query})
print("Answer:", result["result"])
print("\nSource documents:")
for doc in result["source_documents"]:
    print(doc.page_content)
print()
