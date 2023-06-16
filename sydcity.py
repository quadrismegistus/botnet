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

@lru_cache(maxsize=None)
def get_model(model_name:str=DEFAULT_MODEL_NAME):#, **kwargs):
    kwargs={}
    if 'wizard' in model_name: kwargs['model_type']='llama'
    return gpt4all.GPT4All(model_name, model_path=PATH_GPT4ALL_DATA, **kwargs)

def generate(
        prompt:str, 
        stops={}, 
        stop_para=True,
        model_name:str=DEFAULT_MODEL_NAME, 
        gpt:'GPT4All'=None, 
        callback_at={'\n'},
        callback_at_func=None,
        verbose:bool=False,
        logits_size: int = 0,
        tokens_size: int = 0,
        n_past: int = 0,
        n_ctx: int = 1024,
        n_predict: int = 128,
        top_k: int = 40,
        top_p: float = 0.9,
        temp: float = 1.0,
        n_batch: int = 8,
        repeat_penalty: float = 1.2,
        repeat_last_n: int = 10,
        context_erase: float = 0.5,
        streaming: bool = False,
        **kwargs):
    
    if gpt is None: gpt=get_model(model_name)

    words = []
    allwords = []

    def is_valid(l):
        return len([
            w
            for w in l
            if w.strip() 
            and w.strip().isalpha()
        ])>1
    
    def callback_words():
        asyncio.create_task(
            callback_at_func(
                ''.join(
                    words.pop(0)
                    for i in range(len(words))
                )
            )
        )

    def callback(token_id, response):
        try:
            word = response.decode('utf-8')
            sys.stderr.write(word)
            sys.stderr.flush()
            words.append(word)
            allwords.append(word)

            if callback_at_func is not None and word in callback_at and is_valid(words):
                callback_words()

            done = (
                (word in stops) 
                or 
                (stop_para and has_para_break(''.join(allwords)))
            ) and is_valid(allwords)
        except Exception:
            done = False
        return not done

    if words: callback_words()

    gpt.model._response_callback = callback
    sys.stderr.write(f'## PROMPT:\n{prompt}')
    sys.stderr.flush()
    gpt.model.generate(
        prompt,
        logits_size=logits_size,
        tokens_size=tokens_size,
        n_past=n_past,
        n_ctx=n_ctx,
        n_predict=n_predict,
        top_k=top_k,
        top_p=top_p,
        temp=temp,
        n_batch=n_batch,
        repeat_penalty=repeat_penalty,
        repeat_last_n=repeat_last_n,
        context_erase=context_erase,
        streaming=streaming,
    )

    return ''.join(allwords).strip()







class Speech(UserString):
    
    @staticmethod
    def quotative(
            who:str='', 
            what:str='', 
            how:str='', 
            upper:bool=False,
            before:str='',
            between:str=': ',
            after:str=''):
        name = f'{who.upper() if upper else who}'
        namehow = f'{name} ({how})' if how else name
        return before + namehow + between + what + after


    def __init__(self, data:str='', who:str='', what:str='', how:str='', _convo=None):
        super().__init__(data)
        self.who=who.strip()
        self.what=what.strip()
        self.how=how.strip()
        self._convo=_convo

    def __str__(self):
        if self.data:
            return self.data
        elif self.is_valid:
            return Speech.quotative(self.who,self.what,self.how)
        else:
            return self.what
        
    def __repr__(self): return str(self).replace('\n', ' ').strip()

    def screenplay(self, width=35):
        if self.is_valid:
            namehow = f'{self.who.upper()}\n{" "*15}({self.how})' if self.how else self.who.upper()
            return f'{" "*20}{namehow}\n{textwrap.indent(textwrap.fill(stripp(self.what), width), " "*10)}'
        else:
            return f"{textwrap.fill(stripp(self.data),  60)}"

    @property
    def is_valid(self): return bool(self.who) and bool(self.what)

    def _repr_html_(self):
        if not self.is_valid:
            return f'<p class="nonspeech" style="opacity:0.5">{self.data}</p>'
        else:
            how=f' (<i>{self.how}</i>)' if self.how else ''
            return  f'<p class="speech" style="margin-bottom:1em;"><b>{self.who.upper()}{how}</b>: {self.what}</p>'

    def save(self):
        if self._convo is not None: 
            self._convo.speeches.add_speech(self)
    
    @staticmethod
    def from_string(line:str, between:str=':'):
        if between in line:
            whohow,what = line.strip().split(between,1)
            prefs='([:'
            who = whohow
            for p in prefs: who = who.split(p)[0].strip()
            how = whohow[whohow.index(who)+len(who):]
            while how and not how[0].isalpha(): how=how[1:]
            while how and not how[-1].isalpha(): how=how[:-1]
            return Speech(line, who=who, what=what, how=how)
        else:
            return Speech(line)
        

    def __add__(self, other):
        return Speech(
            data=self.data + other.data,
            who=self.who or other.who,
            what=self.what + (other.what if other.what else other.data) if self.what else '',
            how=self.how + other.how if self.how and other.how else self.how,
        )




class Speeches(UserList):

    @staticmethod
    def from_string(string, sep='\n\n'):
        speeches_l = []
        for substring in string.split(sep):
            sp = Speech.from_string(substring)
            if sp is not None:
                speeches_l.append(sp)

        return Speeches(speeches_l, sep=sep, string=string)
    
    @staticmethod
    def from_script(script, sep='\n\n'):
        return Screenplay.parse(script)
    
    

    def __init__(
        self, 
        data=[],
        string='',
        sep='\n\n',
        _convo=None
        ):

        # init as list
        super().__init__()
        self.sep=sep
        self._convo = _convo
        
        if type(data) == str and not string:
            spl = Speeches.from_string(data, sep=sep)
            self.data = spl.data
            self.string = data
        else:
            self.data = []
            self.string=string
            add_to_string=not bool(self.string)
            for sp in data:
                self.add_speech(sp, add_to_string=add_to_string)


    def __str__(self): return self.sep.join(str(sp) for sp in self)

    def has_speech(self, speech):
        return any((speech is x) for x in self)

    def add_speech(self, speech, force=False, add_to_string=True):
        if force or not self.has_speech(speech):
            self.data.append(speech)
            if add_to_string: self.string+=speech.data

    def _repr_html_(self):
        selfmd = '\n\n'.join(utt._repr_html_() for utt in self)
        anames = ", ".join(list(set(utt.who for utt in self if utt and utt.who)))
        return f'''<div style="border:0px solid gray; padding:0 0.75em; margin:0; margin-bottom:1em;"><h4>Dialogue</h4><ol style="margin:0; padding:0; margin-left: 1em; margin-bottom:1em;">{selfmd}</ol></div>'''   


    def screenplay(self):
        return self.sep.join(sp.screenplay() for sp in self)



    def prompt_for(self, who:str='', how:str='', suffix:str=': ', sep=None):
        whohow = f'{who.upper()} ({how})' if how else who.upper()
        return f'{self}{self.sep if sep is None else sep}{whohow}{suffix}'
    
    def screenplay_prompt_for(self, who:str='', how:str='', suffix:str=': ', sep=None, intro='INT. CHAT ROOM - NIGHT'):
        namehow = f'{who.upper()}\n{" "*15}({how})' if how else f'{who.upper()}'
        sep = sep if sep is not None else self.sep
        if intro:
            while not intro.endswith('\n\n'): intro+="\n"
        return f'{intro}{self.screenplay()}{sep}{" "*20}{namehow}\n'
    

    def generate_for(
            self, 
            who:str='', 
            how:str='', 
            suffix:str=': ', 
            sep=None, 
            prompt = None, 
            prompt_func=None,
            prompt_style='dialogue', # also 'screenplay' 
            save=False, 
            **gen_kwargs):
        if not prompt:
            if not prompt_func:
                if prompt_style == 'screenplay':
                    prompt_func = self.screenplay_prompt_for
                else:
                    prompt_func = self.prompt_for
            prompt = prompt_func(
                who=who, 
                how=how, 
                suffix=suffix, 
                sep=sep,
            )
        res = generate(prompt, **gen_kwargs)
        
        if res.strip():
            sp = Speech(who=who, what=res, how=how)
            if save: self.add_speech(sp)
            return sp
        
        return res

    def screenplay_generate_for(self, who:str='', **kwargs):
        kwargs['prompt_func'] = self.screenplay_prompt_for
        return self.generate_for(who=who, **kwargs)
    
    def dialogue_generate_for(self, who:str='', **kwargs):
        kwargs['prompt_func'] = self.prompt_for
        kwargs['stops'] = {'\n'}
        return self.generate_for(who=who, **kwargs)










class Screenplay:
    def parse(script):
        script_lines = script.split('\n')
        # split into paras
        paras = []
        para = []
        for slinex in script_lines:
            sline = slinex.strip()
            if not sline and para:
                paras.append(para)
                para = []
            elif sline:
                para.append(slinex)
        if para: paras.append(para)

        def indentsize(ln):
            return len(ln) - len(ln.lstrip())

        o = []
        for para in paras:
            who,how='',''
            if len(para)>1 and (indentsize(para[0])>indentsize(para[1]) or (para[0] == para[0].upper())):
                who,para = para[0],para[1:]
            if len(para)>1 and para[0].lstrip().startswith('(') or para[0].lstrip().startswith('['):
                how,para = para[0].strip(),para[1:]
                how=how.strip(string.punctuation)
            what=stripp(' '.join(para))
            if who:
                sp = Speech(who=who, what=what, how=how)
            else:
                sp = Speech(what)
            o.append(sp)
        return Speeches(o)
        # return o






def stripp(x):
    x=x.strip()
    while '  ' in x: x=x.replace('  ',' ')
    return x


def has_para_break(s, nb=2):
    n=0
    for x in s:
        if x in {'\n','\r'}: n+=1
        elif x.strip(): n=0    
        if n>=nb: return True
    return False
        

def nodblspc(x):
    # x=x.replace('\n', ' ')
    while '  ' in x: x=x.replace('  ',' ')
    return x
