# tiny-lowest-common-ancestor

Preprocess a rooted tree once, then answer lowest common ancestor queries in constant time.

## Usage

```python
from tiny_lowest_common_ancestor import LowestCommonAncestor

tree = {
    1: [2, 3],
    2: [4, 5],
    3: [6, 7],
    4: [],
    5: [],
    6: [],
    7: [],
}

lca = LowestCommonAncestor(tree, root=1)
print(lca.query(4, 5))  # 2
print(lca.query(4, 6))  # 1
print(lca.query(2, 4))  # 2
```

The tree is a mapping from each node to a list of its children.  Nodes that
appear only as children are treated as leaves.  The root must be a key in the
mapping (it may have an empty child list).  Node values can be any hashable
object: integers, strings, tuples, and so on.

## Why this exists

Lowest common ancestor is a building block for tree distance, path queries, and
hierarchical clustering.  A naive walk up from both nodes costs O(depth) per
query, which is fine for a handful of queries but wasteful when the same tree is
queried thousands of times.

This library makes the classic trade-off: it spends O(n log n) time and memory
up front to build a binary-lifting table, and then each query is O(1).  That is
the right balance when the number of queries is large compared to the size of
the tree.  If you only ever ask one question, a simple parent walk is cheaper;
if you ask many, this is the one to build.

The public API is a single class, `LowestCommonAncestor`, with two methods:
the constructor `LowestCommonAncestor(tree, root)` and `query(u, v)`.

## Edge cases

The awkward part is what counts as a valid tree.  This library requires the
input to be a genuine tree: the root must be a key, and no node may be reached
twice.  A cycle or a duplicate edge raises `ValueError` during construction
rather than producing silently wrong answers later.  A node that appears only as
a child is accepted and treated as a leaf, which is convenient when you build
the mapping lazily.

Querying a node that is not in the tree raises `KeyError`.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

