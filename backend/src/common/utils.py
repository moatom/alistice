# http://tanihito.hatenablog.com/entry/20110119/1295459297
from functools import wraps

def tail_recursive(func):
    self_func = [func]
    self_firstcall = [True]
    self_CONTINUE = [object()]
    self_argskwd = [None]
    
    @wraps(func)
    def _tail_recursive(*args, **kwd):
        if self_firstcall[0] == True:
            func = self_func[0]
            CONTINUE = self_CONTINUE
            self_firstcall[0] = False
            try:
                while True:
                    result = func(*args, **kwd)
                    if result is CONTINUE:  # update arguments
                        args, kwd = self_argskwd[0]
                    else: # last call
                        return result
            finally:
                self_firstcall[0] = True
        else: # return the arguments of the tail call
            self_argskwd[0] = args, kwd
            return self_CONTINUE
    return _tail_recursive