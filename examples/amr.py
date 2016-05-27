
"""
A Pegre-based AMR (Abstract Meaning Representation) parser.

Here's an example of AMR for "Did the girl find the boy?":

    (f / find-01
       :ARG0 (g / girl)
       :ARG1 (b / boy)
       :mode interrogative)
"""

from collections import namedtuple

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

AmrNode = namedtuple('AmrNode', ('identifier', 'relations'))

NODE = nonterminal('NODE')
NODEDEF = nonterminal('NODEDEF', value=lambda d: AmrNode(d[0], d[1]))
INSTANCE = nonterminal('INSTANCE', value=lambda i: (':instance-of', i[1]))
RELATION = nonterminal('RELATION', value=tuple)
VALUE = nonterminal('VALUE')
VAR = nonterminal('VAR')
SPACE = regex(r'\s*', value=Ignore)

grammar={
    'start': NODE,
    'NODE': bounded(regex(r'\(\s*'), NODEDEF, regex(r'\s*\)')),
    'NODEDEF': sequence(VAR, zero_or_more(choice(RELATION, INSTANCE))),
    'INSTANCE': sequence(regex(r'\s*\/\s*'), regex(r'[^\s()]+')),
    'RELATION': sequence(SPACE, regex(r':[^\s()/]+'), SPACE, VALUE),
    'VALUE': choice(NODE, VAR),
    'VAR': regex(r'\w+')
}

Amr = Peg(grammar)

# version that outputs triples

def triples(amrnode):
    def _triples(a, visited):
        if a.identifier in visited:
            return
        visited.add(a.identifier)
        ts = []
        for reln, tgt in a.relations:
            if isinstance(tgt, AmrNode):
                ts.append((a.identifier, reln, tgt.identifier))
                ts.extend(_triples(tgt, visited))
            else:
                ts.append((a.identifier, reln, tgt))
        return ts
    triples = []
    if amrnode:
        triples.append(('TOP', ':top', amrnode.identifier))
        for x, reln, y in _triples(amrnode, set()):
            if reln[-3:] == '-of':
                triples.append((y, reln[:-3], x))
            else:
                triples.append((x, reln, y))
    return triples

TRIPLETOP = nonterminal('TOP', value=triples)
triples_grammar = dict(grammar)
triples_grammar['start'] = TRIPLETOP
triples_grammar['TOP'] = NODE

AmrTriples = Peg(grammar=triples_grammar)

if __name__ == '__main__':
    s = '''( f / find-01
               :ARG0 (g / girl)
               :ARG1 (b / boy)
               :mode interrogative)'''
    print(Amr.parse(s))
    print(AmrTriples.parse(s))
