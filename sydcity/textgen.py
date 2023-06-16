from .imports import *


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



