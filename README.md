This program will generate a dot file which includes the project dependencies involved in a solution.
You can visualize the dot file by using GraphViz if you'd like to.
Input : the full path of sln file.
Output: temp.dot

Note:
1. This python program is deveopped on python 3.x.
2. Works fine for 2010-2017 vs c++ sulution, not test on other version.

prerequisite:
1. pip install bs4
2. If you want to visualize the dependencies stored in temp.dot, please install GraphViz.