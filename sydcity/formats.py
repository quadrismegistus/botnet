from .imports import *

class Format:
    pass

class Screenplay(Format):
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
        return Convo(o)
        # return o


