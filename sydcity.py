## imports
import os,sys,time
from functools import cached_property, lru_cache
cache = lru_cache(maxsize=None)

from io import StringIO 
import sys
import logging
logger = logging.getLogger()

from collections import UserList, UserDict, UserString
import re

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_HOME = os.path.expanduser('~')
PATH_GPT4ALL_DATA = os.path.abspath(os.path.join(PATH_HOME,'gpt4all_data'))
PATH_DATA = os.path.abspath(os.path.join(PATH_HOME,'sydcity_data'))
DEFAULT_MODEL_NAME='ggml-mpt-7b-chat'

import gpt4all
from functools import lru_cache as cache

@cache
def get_model(model_name:str=DEFAULT_MODEL_NAME):
    return gpt4all.GPT4All(model_name, model_path=PATH_GPT4ALL_DATA)

def generate_line(prompt, stops={'\n'}, model_name:str=DEFAULT_MODEL_NAME, gpt:'GPT4All'=None, **kwargs):
    if gpt is None: gpt=get_model(model_name)

    words = []
    def callback(token_id, response):
        word = response.decode('utf-8')
        words.append( word )
        return word not in stops or not ''.join(words).strip()

    gpt.model._response_callback = callback
    gpt.model.generate(prompt, streaming=True, **kwargs)

    return ''.join(words).strip()

