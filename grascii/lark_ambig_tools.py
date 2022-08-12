"""
MIT License

Copyright (c) 2022 chanicpanic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys
from functools import reduce
from itertools import chain, product, repeat
from typing import Any, Collection, Iterable, Iterator, Tuple, TypeVar

from lark import Tree, Transformer
from lark.visitors import Interpreter

if sys.version_info >= (3, 8):
    from math import prod
else:

    def prod(nums, start=1):
        return reduce(lambda x, y: x * y, nums, start)


T = TypeVar("T")


class CountedTree(Tree):
    """A tree subclass with an additional attribute, ``derivation_count``, that
    represents the total number of possible derivations of this tree.
    Derivations are counted based on the number and position of '_ambig' nodes.

    Take caution using the constructor directly. All tree children must be
    instances of ``CountedTree`` for the derivation count to be accurate.
    Changing the children after construction will not update the derivation count.
    """
    def __init__(self, data, children, meta=None):
        super().__init__(data, children, meta)
        derivation_counts = map(_get_derivation_count, children)
        self.derivation_count = (sum(derivation_counts) if data == "_ambig" else prod(derivation_counts))


class CountTrees(Transformer):
    """A transformer that transforms a ``Tree`` into a ``CountedTree``."""
    def __default__(self, data, children, meta):
        return CountedTree(data, children, meta)


def _get_derivation_count(tree: Any) -> int:
    return getattr(tree, "derivation_count", 1)


def _repeat_each(iterable: Iterable[T], n: int) -> Iterator[T]:
    """Repeat each element of the iterable n times.

    Recipe from more-itertools: https://github.com/more-itertools/more-itertools
    """
    return chain.from_iterable(map(repeat, iterable, repeat(n)))


def _ncycles(iterable: Iterable[T], n: int) -> Iterator[T]:
    """Return the elements of the iterable n times.

    This implementation evaluates the elements of the iterable lazily.
    """
    if n > 0:
        saved = []
        for element in iterable:
            yield element
            saved.append(element)
        yield from chain.from_iterable(repeat(saved, n - 1))


def _lazy_product(iterables: Collection[Iterable[T]], lengths: Collection[int]) -> Iterator[Tuple[T, ...]]:
    """Return the Cartesian Product of the iterables of the given lengths.

    This implementation takes advantage of the known lengths of the iterables
    to evaluate the iterables lazily in contrast to ``itertools.product``.
    This function generates tuples in the same order as ``itertools.product``.

    Preconditions: ``len(iterables) == len(lengths)`` and ``lengths[i]`` is the
    number of calls of `next` on an iterator of `iterables[i]` before
    ``StopIteration`` is raised.
    """
    cycle_count = 1
    repeat_count = prod(lengths)
    iterators = []
    for iterable, length in zip(iterables, lengths):
        repeat_count //= length
        iterators.append(_ncycles(_repeat_each(iterable, repeat_count), cycle_count))
        cycle_count *= length
    return zip(*iterators)


class Disambiguator(Interpreter):
    """An Interpreter that iterates over the unambiguous derivations of an
    ambiguous tree (one containing '_ambig' nodes).

    By lazily constructing trees, ``Disambiguator`` is more computationally and
    memory efficient than ``lark.visitors.CollapseAmbiguities``.

    When visiting a ``CountedTree``, ``Disambiguator`` takes advantage of the
    known derivation counts to be even more lazy and is ideal for the case in
    which you only need to find one tree that meets your requirements.

    If you are always going to iterate over all possible derivations, it is
    slightly faster to visit a regular ``Tree``.
    """
    def _ambig(self, tree: Tree) -> Iterator[Tree]:
        for child in tree.children:
            yield from self.visit(child)

    def __default__(self, tree: Tree) -> Iterator[Tree]:
        if isinstance(tree, CountedTree) and tree.derivation_count == 1:
            yield tree
        else:
            yield from self._generate_subtrees(tree)

    def _generate_subtrees(self, tree: Tree) -> Iterator[Tree]:
        sub_tree_iterators = [self.visit(child) if isinstance(child, Tree) else (child,) for child in tree.children]
        if isinstance(tree, CountedTree):
            derivation_counts = [_get_derivation_count(child) for child in tree.children]
            children_lists = _lazy_product(sub_tree_iterators, derivation_counts)
        else:
            children_lists = product(*sub_tree_iterators)
        for children_list in children_lists:
            yield Tree(tree.data, list(children_list))
