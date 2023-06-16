from .imports import *

class Speech(UserString):
    
    @staticmethod
    def quotative(
            who:str='', 
            what:str='', 
            how:str='', 
            upper:bool=True,
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
        if self.is_valid:
            return Speech.quotative(self.who,self.what,self.how)
        elif self.data:
            return self.data        
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
