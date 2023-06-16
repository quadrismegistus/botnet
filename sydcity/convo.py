from .imports import *

class Convo(UserList):
    @staticmethod
    def from_string(string, sep='\n\n'):
        speeches_l = []
        for substring in string.split(sep):
            sp = Speech.from_string(substring)
            if sp is not None:
                speeches_l.append(sp)

        return Convo(speeches_l, sep=sep, string=string)
    
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
            spl = Convo.from_string(data, sep=sep)
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

    def prompt_for(self, who:str='', how:str='', style='dialogue', **opts):
        if style=='screenplay':
            return self.screenplay_prompt_for(who,how,**opts)
        else:
            return self.dialogue_prompt_for(who,how,**opts)

    def dialogue_prompt_for(self, who:str='', how:str='', suffix:str=': ', sep=None, **opts):
        whohow = f'{who.upper()} ({how})' if how else who.upper()
        return f'{self}{self.sep if sep is None else sep}{whohow}{suffix}'
    
    def screenplay_prompt_for(self, who:str='', how:str='', suffix:str=': ', sep=None, intro=DEFAULT_SCREENPLAY_INTRO, **opts):
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
            style='dialogue', # also 'screenplay' 
            save=False, 
            **gen_kwargs):
        if not prompt:
            prompt = self.prompt_for(
                who=who, 
                how=how, 
                suffix=suffix, 
                sep=sep,
                style=style,
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
