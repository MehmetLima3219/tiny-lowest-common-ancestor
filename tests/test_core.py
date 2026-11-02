import unittest

from tiny_lowest_common_ancestor import LowestCommonAncestor


class TestLowestCommonAncestor(unittest.TestCase):
    def test_single_node(self):
        lca = LowestCommonAncestor({1: []}, 1)
        self.assertEqual(lca.query(1, 1), 1)

    def test_simple_chain(self):
        tree = {1: [2], 2: [3], 3: [4], 4: []}
        lca = LowestCommonAncestor(tree, 1)
        self.assertEqual(lca.query(4, 3), 3)
        self.assertEqual(lca.query(4, 2), 2)
        self.assertEqual(lca.query(4, 1), 1)
        self.assertEqual(lca.query(2, 4), 2)
        self.assertEqual(lca.query(3, 3), 3)

    def test_branching_tree(self):
        #        1
        #      /   \
        #     2     3
        #    / \   / \
        #   4   5 6   7
        tree = {
            1: [2, 3],
            2: [4, 5],
            3: [6, 7],
            4: [],
            5: [],
            6: [],
            7: [],
        }
        lca = LowestCommonAncestor(tree, 1)
        self.assertEqual(lca.query(4, 5), 2)
        self.assertEqual(lca.query(6, 7), 3)
        self.assertEqual(lca.query(4, 6), 1)
        self.assertEqual(lca.query(5, 7), 1)
        self.assertEqual(lca.query(2, 4), 2)
        self.assertEqual(lca.query(3, 6), 3)

    def test_deep_tree(self):
        # A chain of 1000 nodes to exercise the binary lifting table.
        tree = {i: [i + 1] for i in range(1000)}
        tree[1000] = []
        lca = LowestCommonAncestor(tree, 0)
        self.assertEqual(lca.query(1000, 999), 999)
        self.assertEqual(lca.query(1000, 500), 500)
        self.assertEqual(lca.query(0, 1000), 0)
        self.assertEqual(lca.query(500, 501), 500)

    def test_wide_tree(self):
        # A root with many children, all leaves.
        tree = {0: list(range(1, 1001))}
        for i in range(1, 1001):
            tree[i] = []
        lca = LowestCommonAncestor(tree, 0)
        self.assertEqual(lca.query(1, 1000), 0)
        self.assertEqual(lca.query(500, 500), 500)

    def test_string_nodes(self):
        tree = {"a": ["b", "c"], "b": ["d"], "c": ["e"], "d": [], "e": []}
        lca = LowestCommonAncestor(tree, "a")
        self.assertEqual(lca.query("d", "e"), "a")
        self.assertEqual(lca.query("d", "b"), "b")
        self.assertEqual(lca.query("e", "c"), "c")

    def test_tuple_nodes(self):
        tree = {(0, 0): [(0, 1), (1, 0)], (0, 1): [(0, 2)], (1, 0): [], (0, 2): []}
        lca = LowestCommonAncestor(tree, (0, 0))
        self.assertEqual(lca.query((0, 2), (1, 0)), (0, 0))
        self.assertEqual(lca.query((0, 2), (0, 1)), (0, 1))

    def test_unknown_node_raises(self):
        lca = LowestCommonAncestor({1: [2], 2: []}, 1)
        with self.assertRaises(KeyError):
            lca.query(1, 99)
        with self.assertRaises(KeyError):
            lca.query(99, 1)

    def test_root_not_in_tree_raises(self):
        with self.assertRaises(ValueError):
            LowestCommonAncestor({1: [2], 2: []}, 3)

    def test_cycle_raises(self):
        # 1 -> 2 -> 1 is not a tree.
        tree = {1: [2], 2: [1]}
        with self.assertRaises(ValueError):
            LowestCommonAncestor(tree, 1)

    def test_duplicate_edge_raises(self):
        tree = {1: [2, 2], 2: []}
        with self.assertRaises(ValueError):
            LowestCommonAncestor(tree, 1)

    def test_child_not_a_key_is_leaf(self):
        # Node 2 is not a key, so it has no children.
        tree = {1: [2]}
        lca = LowestCommonAncestor(tree, 1)
        self.assertEqual(lca.query(1, 2), 1)
        self.assertEqual(lca.query(2, 2), 2)

    def test_self_query(self):
        tree = {1: [2, 3], 2: [4], 3: [5], 4: [], 5: []}
        lca = LowestCommonAncestor(tree, 1)
        for node in (1, 2, 3, 4, 5):
            self.assertEqual(lca.query(node, node), node)


if __name__ == "__main__":
    unittest.main()
