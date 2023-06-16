from .imports import *



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
