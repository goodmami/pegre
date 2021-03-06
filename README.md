# pegre

Functional PEG (Parsing Expression Grammar) in Python

There are many PEG parsers in Python (see
[Related Software](#related-software) for a partial list). Pegre
is a very simple parser (just 10 functions, a class, and a singleton),
and works by calling functions that return the functions that actually
parse a string.

##### Functional PEG

Because it's purely functional, the grammar must be passed to each
function call. The return value is (*remainder*, *obj*) where
*remainder* is the remaining unparsed portion of the input string, and
*obj* is the composed object. For example:

```python
>>> from pegre import literal, sequence
>>> s = 'abcdefghijklmnop'
>>> literal('abc')(s, {})  # {} is an empty grammar
('defghijklmnop', 'abc')
>>> sequence(literal('abc'), literal('def'))(s, {})
('ghijklmnop', ['abc', 'def'])
```

##### Value Passing and Interpretation

A *value* argument to a PEG function generator tells the parser how to
interpret the matched strings. When *value* is a callable, it is
called with the functions output as its argument. When *value* is not
callable, the exact value is returned. If no *value* argument is
given, the value is just passed up. A special value of `Ignore`
suppresses value passing in functions that return lists (`sequence`,
`zero_or_more`, and `one_or_more`). For example:

```python
>>> from pegre import regex, sequence, Ignore
>>> f = sequence(
...     regex('"[^"]*"', value=lambda s: s[1:-1]),  # strip quotes
...     regex(r'\s*:\s*', value=Ignore),            # remove
...     regex('\d+', value=int),                    # convert to int
... )
>>> f('"key": 123', {})
('', ['key', 123])
```

##### Grammars and the Peg class

Pegre is most useful when multiple functions are combined into a
grammar. The `nonterminal` function generator will call a function
in the grammar that is passed to the parsing functions.

```python
>>> from pegre import literal, nonterminal
>>> grammar = {
...     "start": nonterminal('Abc'),
...     "Abc": literal('abc')
... }
>>> grammar['start']('abcdefg', grammar)
('defg', 'abc')
```

This can be made more convenient with the `Peg` class. Continuing the
above:

```python
>>> from pegre import Peg
>>> p = Peg(grammar=grammar)
>>> p.parse('abcdefg')
'abc'
```

Note that `parse()` used the `start` production by default, and
returned only the parsed object (without the unparsed remainder).

## Related Software

* [Arpeggio](https://github.com/igordejanovic/Arpeggio)
* [parsimonius](https://github.com/erikrose/parsimonious)
