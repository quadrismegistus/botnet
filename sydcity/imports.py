DEFAULT_SCREENPLAY_INTRO=''

## imports
import os,sys,time,asyncio,textwrap,string
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
# DEFAULT_MODEL_NAME='ggml-gpt4all-j-v1.3-groovy'
# DEFAULT_MODEL_NAME='ggml-gpt4all-l13b-snoozy'
# DEFAULT_MODEL_NAME='ggml-vicuna-7b-1.1-q4_2'
# DEFAULT_MODEL_NAME='ggml-wizard-13b-uncensored'

import gpt4all
from functools import lru_cache




###

from .utils import *
from .speech import *
from .convo import *
from .formats import *
from .textgen import *
from .bots import *