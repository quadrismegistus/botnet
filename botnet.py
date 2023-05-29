## imports
import os,sys,time
from functools import cached_property, lru_cache
cache = lru_cache(maxsize=None)

from io import StringIO 
import sys
import logging
logger = logging.getLogger()

try:
    from IPython.display import Markdown, display, clear_output, HTML
except Exception:
    pass

from collections import UserList, UserDict, UserString
import re




PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_HOME = os.path.expanduser('~')
PATH_DATA = os.path.abspath(os.path.join(PATH_HOME,'botnet_data'))

DEFAULT_MODEL_UNFILTERED = 'gpt4all-lora-unfiltered-quantized'
DEFAULT_MODEL_FILTERED = 'gpt4all-lora-quantized'
DEFAULT_MODEL = DEFAULT_MODEL_UNFILTERED

MODEL_URLS = {
    'gpt4all-lora-unfiltered-quantized':'https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-unfiltered-quantized.bin',
    'gpt4all-lora-quantized':'https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized.bin',
}

CONVERTED_MODEL_URLS = {
    'gpt4all-lora-unfiltered-quantized':'https://www.dropbox.com/s/fjmvr8fghel6gl7/gpt4all-lora-unfiltered-quantized.ggml.bin?dl=1'
}

TOKENIZER_URL = 'https://huggingface.co/decapoda-research/llama-7b-hf/resolve/main/tokenizer.model'
TOKENIZER_PATH = os.path.join(PATH_DATA,'tokenizer.model')


QUERY_NUM = 0
QUERY_TIMESTAMP = 0

DEFAULT_PROMPT = ""
DEFAULT_PROMPT_PREFIX=""
DEFAULT_PROMPT_SUFFIX=""






## funcs





def get_model_path(model_name=DEFAULT_MODEL):
    return get_model_converted(model_name)


@cache
def get_model(model_name:str=DEFAULT_MODEL, **kwargs):
    ## @HACK @FIX @TODO: force disable stderr output    
    # def donothing(*x,**y): pass
    # sys.stderr.write = donothing
    ##

    from llama_cpp import Llama
    model_fn = get_model_converted(model_name)
    return Llama(model_fn, **kwargs)

def generate(
        prompt,
        stop=[],
        verbose_prompt=True,
        verbose_response=True,
        model_name=DEFAULT_MODEL,
        model_opts={},
        n_predict=50,
        keep_prompt=False,
        clear_prompt=True,
        **generate_opts
    ):
    global QUERY_NUM, QUERY_TIMESTAMP
    QUERY_NUM+=1
    QUERY_TIMESTAMP=time.time()

    vprompt = f'Prompt (Q{QUERY_NUM}, {nowstr(QUERY_TIMESTAMP)}) [stop={", ".join(stop)}]'
    if verbose_prompt: 
        printm_blockquote(prompt, vprompt)
    
    model = get_model(model_name, **model_opts)
    
    def gen(prompt):
        return model(
            prompt,
            max_tokens=n_predict,
            stop = stop,
            **generate_opts
        )
    
    try:
        resd = gen(prompt)
    except UnicodeDecodeError as e:
        try:
            from unidecode import unidecode
            resd = gen(unidecode(prompt))
        except Exception as e:
            logger.error(e)
            # get res -- however far it got
            # res = model.res #?
            resd = {}
    
    resl = resd.get('choices',[])
    res = resl[0]['text'] if resl else ''
    finish_reason = resl[0]['finish_reason'] if resl else ''

    # find response part
    true_res = res.split(prompt,1)[-1]
    
    if verbose_response:
        now=time.time()
        try:
            if clear_prompt: clear_output()
            printm_blockquote(f'{prompt}<b>{true_res}</b>', f'{vprompt}.... +{round(now-QUERY_TIMESTAMP,1)}s] (finished bc `{finish_reason}`)')
            # print(resd)
        except Exception as e:
            logger.error(e)
            pass
    
    return true_res if not keep_prompt else res


def download_model_orig(model_name:str=DEFAULT_MODEL, force:bool=False):
    model_fn = model_name+'.bin'
    model_fnfn = os.path.join(PATH_DATA, model_fn)
    model_url = MODEL_URLS.get(model_name)
    if model_url:
        if force or not os.path.exists(model_fnfn):
            print(f'Downloading {model_name} to:\n\n{model_fnfn}\n\nIf you already have a file, please a symbolic link to it from that location.\n')
            download(model_url, model_fnfn)
    return model_fnfn

def download_tokenizer_orig(force:bool=False):
    if force or not os.path.exists(TOKENIZER_PATH):
        download(TOKENIZER_URL,TOKENIZER_PATH)
    return TOKENIZER_PATH

def convert_model_orig(model_name:str=DEFAULT_MODEL, force:bool=False, exec_name:str='pyllamacpp-convert-gpt4all'):
    newmodel_fn = os.path.join(PATH_DATA, model_name+'.ggml.bin')
    if force or not os.path.exists(newmodel_fn):
        model_fn = download_model_orig(model_name)
        tokenizer_fn = download_tokenizer_orig()    
        cmd=f'{exec_name} {model_fn} {tokenizer_fn} {newmodel_fn}'
        print('>>',cmd)
        os.system(cmd)
    return newmodel_fn

def convert_unfiltered_model(): convert_model_orig(DEFAULT_MODEL_UNFILTERED)
def convert_filtered_model(): convert_model_orig(DEFAULT_MODEL_FILTERED)



def download_model_converted(model_name:str=DEFAULT_MODEL, force:bool=False):
    # @TODO
    
    pass

def get_model_converted(model_name:str=DEFAULT_MODEL, force:bool=False, force_convert:bool=False):
    resfn = ''
    if not force_convert: resfn = download_model_converted(model_name, force=force)
    if not resfn: resfn = convert_model_orig(model_name, force=force)
    return resfn















### utils

def printm(*x,joiner=' ',**y):
    try:
        from IPython.display import Markdown, display
        display(Markdown(joiner.join(str(xx) for xx in x)))
    except Exception:
        print(*x,**y)


def printm_blockquote(content, header = ''):
    o=f"#### {header}\n" if header else ""
    o+=f"<blockquote>\n\n{content}\n\n</blockqute>"
    printm(o)


def nowstr(now=None):
    import datetime as dt
    if not now:
        now=dt.datetime.now()
    elif type(now) in [int,float,str]:
        now=dt.datetime.fromtimestamp(now)

    return '{0}-{1}-{2} {3}:{4}:{5}'.format(now.year,str(now.month).zfill(2),str(now.day).zfill(2),str(now.hour).zfill(2),str(now.minute).zfill(2),str(now.second).zfill(2))




#!/usr/bin/env python 
__author__  = "github.com/ruxi"
__license__ = "MIT"
def download(url, filename=False, verbose = False, desc=None):
    """
    Download file with progressbar
    """


    import requests 
    from tqdm import tqdm
    import os.path


    if not filename:
        local_filename = os.path.join(".",url.split('/')[-1])
    else:
        local_filename = filename

    ensure_dir(os.path.dirname(local_filename))
    
    r = requests.get(url, stream=True)
    file_size = r.headers.get('content-length')
    chunk = 1
    chunk_size=1024
    num_bars = int(file_size) // chunk_size if file_size else None
    if verbose>0:
        print(dict(file_size=file_size))
        print(dict(num_bars=num_bars))

    
    with open(local_filename, 'wb') as fp:
        iterr=tqdm(
            r.iter_content(chunk_size=chunk_size),
            total=num_bars,
            unit='KB',
            desc = local_filename if not desc else desc,
            leave = True
        )
        for chunk in iterr:
            fp.write(chunk)
    return

def ensure_dir(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as e:
            pass
