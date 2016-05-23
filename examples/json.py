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

'''


from pegre import (
    Ignore,
    literal,
    regex,
    nonterminal,
    sequence,
    choice,
    zero_or_more,
    Peg,
)


def qstrip(s):
    """
    Strip surrounding characters (e.g. quotes).
    """
    return s[1:-1]

Json = Peg(
    grammar={
        'start': choice(nonterminal('OBJECT'), nonterminal('ARRAY')),
        'OBJECT': sequence(
            regex(r'{\s*'),
            zero_or_more(
                nonterminal('KEYVAL'),
                delimiter=regex(r'\s*,\s*', value=Ignore)
            ),
            regex(r'\s*}'),
            value=lambda x: dict(x[1])
        ),
        'KEYVAL': sequence(
            nonterminal('DQSTRING'),
            regex(r'\s*:\s*', value=Ignore),
            nonterminal('VALUE'),
        ),
        'ARRAY': sequence(
            regex(r'\[\s*'),
            zero_or_more(
                nonterminal('VALUE'),
                delimiter=regex(r'\s*,\s*', value=Ignore),
            ),
            regex(r'\s*\]'),
            value=lambda x: x[1]
        ),
        'VALUE': choice(*map(
            nonterminal,
            ['DQSTRING', 'OBJECT', 'ARRAY', 'NUMBER', 'TRUE', 'FALSE', 'NULL']
        )),
        'DQSTRING': regex(r'"[^"\\]*(?:\\.[^"\\]*)*"', value=qstrip),
        'NUMBER': choice(nonterminal('FLOAT'), nonterminal('INT')),
        'FLOAT': regex(r'-?(0|[1-9]\d*)(\.\d+[eE][-+]?|\.|[eE][-+]?)\d+',
                       value=float),
        'INT': regex(r'-?(0|[1-9]\d*)', value=int),
        'TRUE': literal('true', value=True),
        'FALSE': literal('false', value=False),
        'NULL': literal('null', value=None),
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
