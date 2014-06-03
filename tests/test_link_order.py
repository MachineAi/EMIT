__author__ = 'tonycastronova'


import unittest
import networkx as n

class test_link_order(unittest.TestCase):

    def setUp(self):

        self.g = n.DiGraph()
        # add some nodes to simulate models
        self.g.add_node('m1')
        self.g.add_node('m2')
        self.g.add_node('m3')
        self.g.add_node('m4')
        self.g.add_node('m5')

    def tearDown(self):
        del self.g

    def test_determine_execution_order(self):
        from coordinator import main
        self.sim = main.Coordinator()
        # add models
        mdl1 = '/Users/tonycastronova/Documents/projects/iUtah/EMIT/tests/data/multiplier.mdl'
        id1 = self.sim.add_model(mdl1)
        mdl2 = '/Users/tonycastronova/Documents/projects/iUtah/EMIT/tests/data/random.mdl'
        id2 = self.sim.add_model(mdl2)

        # create link
        linkid = self.sim.add_link(id2,'OUTPUT1',id1,'INPUT1')

        # get execution order
        order = self.sim.determine_execution_order()

        self.assertTrue(order.index(id1) > order.index(id2))

    def test_basic(self):
        """

        m1 -> m2 -> m3 -> m4 -> m5 -> m6
        """

        # add some edges to simulate links
        self.g.add_edge('m1','m2')
        self.g.add_edge('m2','m3')
        self.g.add_edge('m3','m4')
        self.g.add_edge('m4','m5')
        self.g.add_edge('m5','m6')

        order = n.topological_sort(self.g)

        self.assertTrue(''.join(order) == 'm1m2m3m4m5m6')

        #self.sim.__linknetwork = g

    def test_simple_tree(self):
        """
              m1 -> m2
                        -> m3
        m6 -> m5 -> m4
        """
        self.g.add_edge('m1','m2')
        self.g.add_edge('m2','m3')

        self.g.add_edge('m6','m5')
        self.g.add_edge('m5','m4')
        self.g.add_edge('m4','m3')


        order = n.topological_sort(self.g)

        self.assertTrue(order.index('m1') < order.index('m2'))
        self.assertTrue(order.index('m6') < order.index('m5'))
        self.assertTrue(order.index('m5') < order.index('m4'))
        self.assertTrue(order.index('m3') == 5)


    def test_loop(self):
        """

        m6 -> m5 -> m4 \
        ^               \
        |                -> m3
         <- |m1| -> m2 /

        """

        self.g.add_edge('m1','m2')
        self.g.add_edge('m1','m6')

        self.g.add_edge('m2','m3')
        self.g.add_edge('m6','m5')
        self.g.add_edge('m5','m4')
        self.g.add_edge('m4','m3')

        order = n.topological_sort(self.g)

        self.assertTrue(order.index('m1') == 0)
        self.assertTrue(order.index('m6') < order.index('m5'))
        self.assertTrue(order.index('m5') < order.index('m4'))
        self.assertTrue(order.index('m3') == 5)