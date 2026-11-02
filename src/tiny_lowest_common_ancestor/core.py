"""Preprocess a rooted tree to answer lowest common ancestor queries in O(1)."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional


class LowestCommonAncestor:
    """Answer lowest common ancestor queries on a rooted tree.

    The tree is given as a mapping from each node to a list of its children.
    The root must be supplied explicitly; nodes that appear only as children
    are discovered automatically.  After construction, :meth:`query` runs in
    constant time (aside from the dictionary lookups used to map nodes to
    internal indices).

    The implementation uses binary lifting: for every node we store its
    2**k-th ancestor for k up to floor(log2(n)).  This is the classic
    trade-off: O(n log n) preprocessing time and memory in exchange for
    O(1) queries, which is the right balance when the number of queries is
    large compared to the size of the tree.

    Node values may be any hashable object.  The root must be present as a
    key in the tree mapping (it may have an empty child list).
    """

    __slots__ = ("_nodes", "_index", "_parent", "_depth", "_up", "_log")

    def __init__(self, tree: Dict[object, List[object]], root: object) -> None:
        """Build the LCA structure for ``tree`` rooted at ``root``.

        Args:
            tree: Mapping from a node to a list of its children.  The root
                must be a key in this mapping.  Children that are not keys
                are treated as leaves with no children.
            root: The root node of the tree.

        Raises:
            ValueError: If ``root`` is not a key in ``tree``.
        """
        if root not in tree:
            raise ValueError("root must be a key in the tree mapping")

        # Discover every node reachable from the root.  We keep the order
        # stable so that indices are deterministic for testing.
        nodes: List[object] = []
        index: Dict[object, int] = {}
        parent: List[int] = []
        depth: List[int] = []

        # BFS from the root.  We record the parent index and depth as we go.
        queue: deque = deque()
        index[root] = 0
        nodes.append(root)
        parent.append(-1)
        depth.append(0)
        queue.append(root)

        while queue:
            node = queue.popleft()
            node_idx = index[node]
            for child in tree.get(node, ()):
                if child in index:
                    # A child that was already seen would mean the input is
                    # not a tree (cycle or duplicate edge).  We reject it
                    # rather than silently producing wrong answers.
                    raise ValueError("input is not a tree: cycle or duplicate edge")
                child_idx = len(nodes)
                index[child] = child_idx
                nodes.append(child)
                parent.append(node_idx)
                depth.append(depth[node_idx] + 1)
                queue.append(child)

        n = len(nodes)
        # log_table[i] = floor(log2(i)) for i >= 1, and 0 for i == 0.
        log_table = [0] * (n + 1)
        for i in range(2, n + 1):
            log_table[i] = log_table[i // 2] + 1

        # up[k][v] is the 2**k-th ancestor of v, or -1 if it does not exist.
        max_log = log_table[n] if n > 0 else 0
        up: List[List[int]] = [parent]
        for k in range(1, max_log + 1):
            prev = up[k - 1]
            curr = [0] * n
            for v in range(n):
                mid = prev[v]
                curr[v] = prev[mid] if mid != -1 else -1
            up.append(curr)

        self._nodes = nodes
        self._index = index
        self._parent = parent
        self._depth = depth
        self._up = up
        self._log = log_table

    def query(self, u: object, v: object) -> object:
        """Return the lowest common ancestor of ``u`` and ``v``.

        Args:
            u: A node in the tree.
            v: A node in the tree.

        Returns:
            The deepest node that is an ancestor of both ``u`` and ``v``.

        Raises:
            KeyError: If either ``u`` or ``v`` is not in the tree.
        """
        if u not in self._index:
            raise KeyError(u)
        if v not in self._index:
            raise KeyError(v)

        a = self._index[u]
        b = self._index[v]

        # Make sure a is the deeper node.
        if self._depth[a] < self._depth[b]:
            a, b = b, a

        # Lift a up to the same depth as b.
        diff = self._depth[a] - self._depth[b]
        bit = 0
        while diff:
            if diff & 1:
                a = self._up[bit][a]
            diff >>= 1
            bit += 1

        if a == b:
            return self._nodes[a]

        # Lift both nodes together until their ancestors meet.
        for k in range(len(self._up) - 1, -1, -1):
            if self._up[k][a] != self._up[k][b]:
                a = self._up[k][a]
                b = self._up[k][b]

        return self._nodes[self._parent[a]]
