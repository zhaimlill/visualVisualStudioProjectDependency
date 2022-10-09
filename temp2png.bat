rem GraphViz must be installed first.
#python visualProjectDependency.py sample.sln
dot -Tpng temp.dot -o temp.png
start temp.png