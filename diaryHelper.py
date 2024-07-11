from gpt_helper.gpt_helper import GPTHelper, Message
from fastAPIMessage import FastAPIMessage


class DiaryHelper:
    def __init__(self):
        self.gpt = GPTHelper(model='gpt-4o-2024-05-13')

    def __call__(self, user_input):
        self._set_user_input(user_input)
        self.tasks = self._get_tasks()
        if self.tasks == '':
            return '오늘 있었던 일을 간략하게 적어주세요 :)'
        self.descriptions = self._generate_diary_descriptions()

        print(f'''
        user_input: {self.user_input}
        tasks: {self.tasks}
        descriptions: {self.descriptions}
        ''')

        return self.descriptions

    def _set_user_input(self, message: FastAPIMessage):
        self.user_input = message.content

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
