from gpt_helper.gpt_helper import GPTHelper, Message
import json
from database.databaseHelper import get_db, get_test_db
from database.db_classes import Diary, User
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


class DiaryHelper:
    def __init__(self):
        self.gpt = GPTHelper(model='gpt-4o-mini')

    def generate_content(self, user_input):
        self._set_user_input(user_input)
        tasks = self._get_tasks()
        print(tasks)
        self.tasks = json.loads(tasks)
        if not self.tasks['has_tasks']:
            return self.tasks['answer'], False
        self.descriptions = self._generate_diary_descriptions()

        return self.descriptions, True

    def _set_user_input(self, message):
        self.user_input = message

    def _get_tasks(self):
        assert hasattr(self, 'user_input'), "User input is not set"

        prompt_system = '''
        You are an assistant who can manage user's daily schedule.
        The user would give you a list of tasks or events that they already have done.
        Your role is to generate a list of descriptions for each task or event according to the user's input.
        You cannot guess the detail of the experiences.
        Please only use the information provided by the user.
        If the user input does not include any tasks or events, please ask the user what happened today in Korean.
        Your answer is formatted in JSON like below.
        {
            "has_tasks": true or false,
            "answer": "task1, task2, task3" or "오늘 무슨 일이 있으셨어요?"
        }
        '''
        prompt_user = f'''
        {self.user_input}
        '''
        message_system = Message(role='system', content_type='text', content=prompt_system)
        message_user = Message(role='user', content_type='text', content=prompt_user)

        try:
            response = self.gpt.send_messages([message_system, message_user])
            return response
        except Exception as e:
            raise Exception(f"Error generating descriptions: {str(e)}")

    def _generate_diary_descriptions(self):
        prompt_system = '''
        You are an assistant who writes the diary content for the user.
        The user would give you a list of tasks or events that they already have done.
        Your role is to generate simple sentences according to user's input.
        The output should be in Korean and just like writing in a diary.
        '''
        prompt_user = f'''
        {self.tasks}
        '''
        message_system = Message(role='system', content_type='text', content=prompt_system)
        message_user = Message(role='user', content_type='text', content=prompt_user)
        try:
            response = self.gpt.send_messages([message_system, message_user])
            return response
        except Exception as e:
            raise Exception(f"Error generating descriptions: {str(e)}")

    def _load_history(self):
        db = next(get_test_db())
        diaries = db.query(Diary).all()
        history = ""
        for diary in diaries:
            history += f'''
            {diary.date}의 일기는 다음과 같다.
            {diary.content}\n
            '''
        return history

    def _get_retriever(self, history):

        doc = Document(page_content=history)

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents([doc])

        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)

        return db.as_retriever()

    def _get_qa_chain(self, retriever, model_name="gpt-4o-mini"):
        llm = ChatOpenAI(model_name=model_name, temperature=0)

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

    def execute_rag(self, query):
        history = self._load_history()
        retriever = self._get_retriever(history)

        qa = self._get_qa_chain(retriever)
        print(query)
        result = qa({"query": query})
        print(result)
        return result["result"]
