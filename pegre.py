
import re
from functools import wraps

__all__ = [
    'Ignore',
    'literal',
    'regex',
    'nonterminal',
    'and_next',
    'not_next',
    'sequence',
    'choice',
    'optional',
    'zero_or_more',
    'one_or_more',
    'Peg',
]

Ignore = object()  # just a singleton for identity checking

def valuemap(f):
    """
    Decorator to help PEG functions handle value conversions.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'value' in kwargs:
            val = kwargs['value']
            del kwargs['value']
            _f = f(*args, **kwargs)
            def valued_f(*args, **kwargs):
                result = _f(*args, **kwargs)
                if result is not None:
                    s, obj = result
                    if callable(val):
                        return (s, val(obj))
                    else:
                        return (s, val)
            return valued_f
        else:
            return f(*args, **kwargs)
    return wrapper

@valuemap
def literal(x):
    """
    Create a PEG function to consume a literal.
    """
    xlen = len(x)
    def match_literal(s, grm):
        if s[:xlen] == x:
            return (s[xlen:], x)
        return None
    return match_literal

@valuemap
def regex(r):
    """
    Create a PEG function to match a regular expression.
    """
    p = re.compile(r)
    def match_regex(s, grm):
        m = p.match(s)
        if m is not None:
            return (s[m.end():], m.group())
        return None
    return match_regex

@valuemap
def nonterminal(n):
    """
    Create a PEG function to match a nonterminal.
    """
    def match_nonterminal(s, grm):
        expr = grm[n]
        return expr(s, grm)
    return match_nonterminal

@valuemap
def and_next(e):
    """
    Create a PEG function for positive lookahead.
    """
    def match_and_next(s, grm):
        if e(s, grm):
            return (s, Ignore)
        return None    
    return match_and_next

@valuemap
def not_next(e):
    """
    Create a PEG function for negative lookahead.
    """
    def match_not_next(s, grm):
        if not e(s, grm):
            return (s, Ignore)
        return None    
    return match_not_next

@valuemap
def sequence(*es):
    """
    Create a PEG function to match a sequence.
    """
    def match_sequence(s, grm):
        data = []
        for e in es:
            result = e(s, grm)
            if result is None:
                return None
            s, obj = result
            if obj is not Ignore:
                data.append(obj)
        return (s, data)
    return match_sequence

@valuemap
def choice(*es):
    """
    Create a PEG function to match an ordered choice.
    """
    def match_choice(s, grm):
        for e in es:
            result = e(s, grm)
            if result is not None:
                return result
        return None
    return match_choice

@valuemap
def optional(e):
    """
    Create a PEG function to optionally match an expression.
    """
    def match_optional(s, grm):
        result = e(s, grm)
        if result is not None:
            return result
        return (s, Ignore)
    return match_optional

@valuemap
def zero_or_more(e, delimiter=None):
    """
    Create a PEG function to match zero or more expressions.

    Args:
        e: the expression to match
        delimiter: an optional expression to match between the
            primary *e* matches.
    """
    def match_zero_or_more(s, grm):
        result = e(s, grm)
        if result is not None:
            data = []
            while result is not None:
                s, obj = result
                if obj is not Ignore:
                    data.append(obj)
                if delimiter is not None:
                    result = delimiter(s, grm)
                    if result is None:
                        break
                    s, obj = result
                    if obj is not Ignore:
                        data.append(obj)
                result = e(s, grm)
            return (s, data)
        return (s, Ignore)
    return match_zero_or_more

@valuemap
def one_or_more(e, delimiter=None):
    """
    Create a PEG function to match one or more expressions.

    Args:
        e: the expression to match
        delimiter: an optional expression to match between the
            primary *e* matches.
    """
    def match_one_or_more(s, grm):
        result = e(s, grm)
        if result is not None:
            data = []
            while result is not None:
                s, obj = result
                if obj is not Ignore:
                    accumulate(data, obj)
                if delimiter is not None:
                    result = delimiter(s, grm)
                    if result is None:
                        break
                    s, obj = result
                    if obj is not Ignore:
                        data.append(obj)
                result = e(s, grm)
            return (s, data)
        return None
    return match_one_or_more


class Peg(object):
    """
    A class to assist in parsing using a grammar of PEG functions.
    """
    def __init__(self, grammar, start='start'):
        self.start = start
        self.grammar = grammar

    def parse(self, s):
        result = self.grammar[self.start](s, self.grammar)
        if result:
            return result[1]
