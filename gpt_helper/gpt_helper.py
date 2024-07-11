import os

from PIL import Image
from io import BytesIO
import base64
from dataclasses import dataclass
import requests
from typing import Any
import openai
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
import json
from openai import OpenAI
import numpy as np


@dataclass
class Parameter:
    name: str
    description: str
    required: bool = True
    type: str = 'string'
    enum: list = None

    def __repr__(self):
        return f'Parameter({self.name}, {self.type}, {self.description}, {self.enum})'


@dataclass
class Function:
    name: str
    description: str
    parameters: list
    function: Any

    def __repr__(self):
        return f'Function({self.name}, {self.description}, {self.parameters})'

    def _build_parameters(self):
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for parameter in self.parameters:
            parameters['properties'][parameter.name] = {
                "type": parameter.type,
                "description": parameter.description,
            }
            if parameter.enum:
                parameters['properties'][parameter.name]['enum'] = parameter.enum
            if parameter.required:
                parameters['required'].append(parameter.name)
        return parameters

    def _get(self):
        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': self.description,
                'parameters': self._build_parameters()}
        }


@dataclass
class Message:
    role: str
    content_type: str
    content: Any

    def __repr__(self):
        if self.content_type == 'text':
            return f'Text(role={self.role}, content_type={self.content_type}, content={self.content})'
        elif self.content_type == 'image_url':
            if isinstance(self.content, str):
                return f'Image(role={self.role}, content_type={self.content_type}, content={self.content})'
            else:
                return f'Image(role={self.role}, content_type={self.content_type}, content=Pillow Image)'

    def __init__(self, role, content, content_type='text'):
        assert role in ['system', 'user', 'assistant'], f'role must be either system or user, but got {role}'
        assert content_type in ['text', 'image_url'], \
            f'content_type must be either text or image_url, but got {content_type}'
        self.role = role
        self.content_type = content_type
        self.content = content

    def _get_as_text(self):
        payload = {
            "role": self.role,
            "content": [{"type": self.content_type,
                         self.content_type: self.content}]
        }
        return payload

    def _get_as_image_url(self):
        img = self._encode_img(self.content)
        payload = {
            "role": self.role,
            "content": [{"type": self.content_type,
                         self.content_type: {"url": f"data:image/jpeg;base64,{img}"}}]
        }
        return payload

    def _get(self):
        if self.content_type == 'text':
            return self._get_as_text()
        elif self.content_type == 'image_url':
            return self._get_as_image_url()

    @staticmethod
    def _encode_img(img):
        if isinstance(img, str):
            img = Image.open(img)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        img_str = img_str.decode('utf-8')
        return img_str


class GPTHelper:
    _PRICE_DICTIONARY = {
        'gpt-4-1106-preview': {'input': 0.01, 'output': 0.03},
        'gpt-4-vision-preview': {'input': 0.01, 'output': 0.03},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-32k': {'input': 0.06, 'output': 0.12},
        'gpt-3.5-turbo-0125': {'input': 0.0005, 'output': 0.0015},
        'gpt-3.5-turbo-instruct': {'input': 0.0015, 'output': 0.002},
        'gpt-4o-2024-05-13': {'input': 0.005, 'output': 0.005},
    }
    _API_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key=None, model='gpt-4-vision-preview', max_tokens=1000, function=None):
        assert model in self._PRICE_DICTIONARY.keys(), f"model must be one of {self._PRICE_DICTIONARY.keys()}"
        # if model != 'gpt-4-vision-preview':
        #     raise NotImplementedError("Only gpt-4-vision-preview is supported at the moment")

        self.client = OpenAI()
        self.api_key = api_key if api_key else os.environ['OPENAI_API_KEY']
        self.model = model
        self.max_tokens = max_tokens
        self.total_tokens = self._initialize_token_usage()
        self.total_completion_tokens = self._initialize_token_usage()
        self.total_prompt_tokens = self._initialize_token_usage()
        self.previous_tokens = self._initialize_token_usage()
        self.previous_completion_tokens = self._initialize_token_usage()
        self.previous_prompt_tokens = self._initialize_token_usage()
        self.last_answer = None
        self.functions = function if function else []
        self._add_default_function()

    def _add_default_function(self):
        self.functions.append(Function(name="make_dict",
                                       description='Get a key and a value make it into dictionary.',
                                       parameters=[
                                           Parameter(name='key', type='string', description='Key of the dictionary'),
                                           Parameter(name='value', type='string', description='Value of the dictionary')
                                       ],
                                       function=lambda key, value: {key: value}))

    def _initialize_token_usage(self):
        return {model: 0 for model in self._PRICE_DICTIONARY.keys()}

    def _function_calling(self, tool_calls):
        available_functions = {function.name: function.function for function in self.functions}
        response_list = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            response_list.append(function_to_call(**function_args))
        return response_list

    def get_price(self):
        input_price = 0
        output_price = 0
        exchange_ratio = 1391.46
        for model in self._PRICE_DICTIONARY.keys():
            input_price += self.total_prompt_tokens[model] * self._PRICE_DICTIONARY[model]['input'] / 1000.
            output_price += self.total_completion_tokens[model] * self._PRICE_DICTIONARY[model]['output'] / 1000.
        return f"Total: {input_price + output_price} USD\n" \
               f"Input: {input_price} USD\n" \
               f"Output: {output_price} USD\n" \
               f"Total: {exchange_ratio * (input_price + output_price)} KRW\n" \
               f"Input: {exchange_ratio * (input_price)} KRW\n" \
               f"Output: {exchange_ratio * (output_price)} KRW\n"

    def __repr__(self):
        return f"GPT({self.model}) \n" \
               f"total_tokens: {self.total_tokens} \n" \
               f"total_completion_tokens: {self.total_completion_tokens} \n" \
               f"total_prompt_tokens: {self.total_prompt_tokens}"

    def _get_payload(self, message_list):
        return {"model": self.model,
                "messages": [message._get() for message in message_list],
                "max_tokens": self.max_tokens}

    def _get_header(self):
        return {"Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"}

    def _update_token_usage(self, usage, model=None):
        if model is None:
            model = self.model
        if not isinstance(usage, dict):
            self.previous_tokens[model] = usage.total_tokens
            self.previous_completion_tokens[model] = usage.completion_tokens
            self.previous_prompt_tokens[model] = usage.prompt_tokens
            self.total_tokens[model] += usage.total_tokens
            self.total_completion_tokens[model] += usage.completion_tokens
            self.total_prompt_tokens[model] += usage.prompt_tokens
        else:
            self.previous_tokens[model] = usage['total_tokens']
            self.previous_completion_tokens[model] = usage['completion_tokens']
            self.previous_prompt_tokens[model] = usage['prompt_tokens']
            self.total_tokens[model] += usage['total_tokens']
            self.total_completion_tokens[model] += usage['completion_tokens']
            self.total_prompt_tokens[model] += usage['prompt_tokens']

    def send_messages(self, message_list):
        response = requests.post(self._API_URL,
                                 headers=self._get_header(),
                                 json=self._get_payload(message_list))
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}, "
                            f"message: {response.json()['error']['message']}")
        else:
            response = response.json()
            self._update_token_usage(response['usage'])
            self.last_answer = Message(
                role='assistant',
                content_type='text',
                content=response['choices'][0]['message']['content'])
            return self.last_answer.content

    def ask_function(self, message):
        return self._check_message_need_function_calling(message)

    def add_function(self, function):
        self.functions.append(function)

    def _check_message_need_function_calling(self, message):
        if len(self.functions) == 0:
            return None
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[message._get()],
            tools=[function._get() for function in self.functions],
            tool_choice="auto",
        )
        self._update_token_usage(response.usage, "gpt-3.5-turbo-1106")
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            return self._function_calling(tool_calls)
        else:
            return None

    def generate_image(self, prompt, size="1024x1024"):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            response_format="b64_json"
        )
        b64 = response.data[0].b64_json
        imgdata = base64.b64decode(b64)
        img = Image.open(BytesIO(imgdata))

        # Convert to numpy array
        img_array = np.array(img)

        return img_array
