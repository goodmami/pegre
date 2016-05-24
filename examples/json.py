'''
A Pegre-based JSON parser.

This uses the *value* functionality to construct the JSON object as
it parses, rather than just producing an AST. The grammar is roughly
like this:

    start       <- Object / Array
    Object      <- OPENBRACE (KeyVal (COMMA KeyVal)*)? CLOSEBRACE
    Array       <- OPENBRACKET (Value (COMMA Value)*)? CLOSEBRACKET
    KeyVal      <- Key COLON Value
    Key         <- DQSTRING Spacing
    Value       <- (DQSTRING / Object / Array / Number / True / False / Null) Spacing
    DQSTRING    <- '"' (!'"' .)* '"'
    Number      <- Float / Int
    Float       <- Int FloatSuffix
    FloatSuffix <- '.' [0-9]+ 'e' [+-]? [0-9]+
                 / '.' [0-9]+
                 / 'e' [+-]? [0-9]+
    Int         <- '-'? (0 | [1-9][0-9]*)
    True        <- 'true'
    False       <- 'false'
    Null        <- 'null'
    OPENBRACE   <- '{' Spacing
    OPENBRACE   <- '}' Spacing
    OPENBRACKET <- '[' Spacing
    OPENBRACKET <- ']' Spacing
    COMMA       <- ',' Spacing
    COLON       <- ':' Spacing
    Spacing     <- [ \t\n]*

Note that string processing does not currently process escape
sequences. Because JSON strings can contain both unicode AND escaped
unicode, some custom processing is required. See this StackOverflow
answer: http://stackoverflow.com/a/24519338/1441112

'''

from pegre import (
    Ignore,
    literal,
    regex,
    nonterminal,
    sequence,
    choice,
    zero_or_more,
    bounded,
    delimited,
    Peg,
)


def qstrip(s):
    """
    Strip surrounding characters (e.g. quotes).
    """
    return s[1:-1]

OBJECT   = nonterminal('OBJECT', value=dict)
ARRAY    = nonterminal('ARRAY', value=list)
KEYVALS  = nonterminal('KEYVALS')
VALUES   = nonterminal('VALUES')
VALUE    = nonterminal('VALUE')
NUMBER   = nonterminal('NUMBER')
FLOAT    = regex(r'-?(0|[1-9]\d*)(\.\d+[eE][-+]?|\.|[eE][-+]?)\d+', value=float)
INT      = regex(r'-?(0|[1-9]\d*)', value=int)
DQSTRING = regex(r'"[^"\\]*(?:\\.[^"\\]*)*"', value=qstrip)
TRUE     = literal('true', value=True)
FALSE    = literal('false', value=False)
NULL     = literal('null', value=None)
COMMA    = regex(r'\s*,\s*')

Json = Peg(
    grammar={
        'start': choice(OBJECT, ARRAY),
        'OBJECT': bounded(regex(r'\{\s*'), KEYVALS, regex(r'\s*}')),
        'KEYVALS': delimited(nonterminal('KEYVAL'), COMMA),
        'KEYVAL': sequence(DQSTRING, regex(r'\s*:\s*', value=Ignore), VALUE),
        'ARRAY': bounded(regex(r'\[\s*'), VALUES, regex(r'\s*\]')),
        'VALUES': delimited(VALUE, COMMA),
        'VALUE': choice(DQSTRING, OBJECT, ARRAY, NUMBER, TRUE, FALSE, NULL),
        'NUMBER': choice(FLOAT, INT),
    }
)


if __name__ == '__main__':
    s = '''{
        "bool": [
            true,
            false
        ],
        "number": {
            "float": -0.14e3,
            "int": 1
        },
        "other": {
            "string": "string",
            "unicode": "あ",
            "null": null
        }
    }'''
    print(Json.parse(s))
    import timeit
    print(
        timeit.timeit(
            'Json.parse(s)',
            setup='from __main__ import Json, s',
            number=10000
        )
    )
