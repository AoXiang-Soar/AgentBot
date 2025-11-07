import hashlib, json, logging, os
from pathlib import Path
from typing import Literal

import openai
from openai import OpenAI, BadRequestError


current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))

with open(project_root+'/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_key = config['api-key']

class LLM(object):
    def __init__(self, model, base_url,
                 load_from_cache=True, save_to_cache=True):
        self.model, self.base_url = model, base_url
        openai.base_url = base_url
        self.cache_folder = project_root + '/' + config['base-chat-cache-folder'] + '/' + model
        self.load_from_cache = load_from_cache
        self.save_to_cache = save_to_cache
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def call(self, prompt: str|list[dict[Literal['role', 'content'], str]], num_of_samples=1,
             prefix=None) -> tuple[list[str], str, str]:
        """
        Call LLM
        :param prompt: the prompt to call llm
        :param num_of_samples: expected number of responses returned by the LLM. Note that not all models support this parameter (for example, Deepseek-V3).
        :param prefix: prefix of local cache files
        :return: response message, prompt token usage, completion token usage
        """
        response = None
        max_tokens = config['max-tokens']
        call_params = self.get_call_params(prompt, num_of_samples)
        cache_file_path = self.get_cache_file_path(prompt, num_of_samples, prefix)

        if type(prompt) == str:
            prompt = [{'role': 'user', 'content': prompt}]

        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

        if self.load_from_cache and self.cache_folder is not None:
            if Path(cache_file_path).is_file():
                with open(cache_file_path, "r") as file:
                    logging.info(f"Loading LLM's response from cache...")
                    try:
                        json_to_load = json.load(file)
                        response = json_to_load['response']
                    except Exception:
                        logging.warning("Failed to load LLM's response from cache.")

        if response is None:
            try:
                logging.info(f"Calling the LLM with prompt: {prompt}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=prompt,
                    n=1,
                    stream=False,
                    temperature=config['temperature'],
                    max_tokens=max_tokens
                ).model_dump_json()

            except BadRequestError as e:
                if "context_length_exceeded" in str(e):
                    response = {
                        'error': "context_length_exceeded",
                        'error_message': e.with_traceback(None),
                        'choices': [ {'message': {'content': ""}} ],
                        'usage': {'total_tokens': max_tokens}
                        }
                else: raise e

            if type(response) is str:
                response = json.loads(response)

            if self.save_to_cache and self.cache_folder is not None:
                with open(cache_file_path, "w") as file:
                    json_to_save = self.get_json_to_save(call_params, response)
                    file.write(json.dumps(json_to_save, indent=4, sort_keys=True))

        if 'error' in response.keys():
            if response['error'] == "context_length_exceeded":
                raise openai.OpenAIError(response['error_message'], None)
            
        response_message = [choice['message']['content'] for choice in response['choices']]

        completion_token_usage = response['usage']['completion_tokens']
        prompt_token_usage = response['usage']['prompt_tokens']

        logging.info(f"Responses are fetched. Input token usage: {prompt_token_usage}, output token usage: {completion_token_usage}")

        return response_message, prompt_token_usage, completion_token_usage
    
    def get_call_params(self, prompt, num_of_samples=1):
        return {
            "model": self.model,
            "messages": prompt,
            "n": num_of_samples,
            "temperature": 1,
            "top_p": 1,
        }

    def get_call_hash(self, prompt, num_of_samples=1):
        call_params = self.get_call_params(prompt, num_of_samples=num_of_samples)
        call_params=LLM.get_sorted_json_str(call_params)
        return hashlib.md5(call_params.encode('utf-8')).hexdigest()

    @staticmethod
    def get_sorted_json_str(data):
        if isinstance(data, list):
            sorted_list = sorted([LLM.get_sorted_json_str(item) if isinstance(item, (dict, list)) else item for item in data])
            json_str = json.dumps(sorted_list, sort_keys=True)
        elif isinstance(data, dict):
            sorted_dict = {k: LLM.get_sorted_json_str(v) for k, v in sorted(data.items())}
            json_str = json.dumps(sorted_dict, sort_keys=True)
        else:
            json_str = json.dumps(data, sort_keys=True)

        return json_str
    
    def get_cache_file_path(self, prompt, num_of_samples=1, prefix=None):
        call_hash = self.get_call_hash(prompt, num_of_samples)
        if prefix is not None:
            return f"{self.cache_folder}/{prefix}_{call_hash}.json"
        return f"{self.cache_folder}/{call_hash}.json"

    @staticmethod
    def get_json_to_save(call_params, response):
        return {
            "call": call_params,
            "response": response
        }

deepseek_v3 = LLM(model='deepseek-chat', base_url='https://api.deepseek.com')
gpt_4o = LLM(model='gpt-4o', base_url='https://api.openai.com/v1')
gpt_3d5 = LLM(model='gpt-3.5-turbo', base_url='https://api.openai.com/v1')
custom = LLM(model=config['model'], base_url=config['base-url'])