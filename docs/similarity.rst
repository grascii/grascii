
Similarity Resolution
#####################

When running a search, regular expressions are generated with alternatives
based on the given strokes. At a basic level, alternatives include
equivalent forms of the same stroke. When uncertainty is greater than 0,
similar strokes are also added as alternatives.

The similar strokes are defined by a similarity graph. The set of strokes
returned as being similar are all those within a distance equal to the
uncertainty from the target node when performing a breadth-first-search.

The similarity graph is shown below.

.. image:: images/sim_graph.png
  :width: 600px
