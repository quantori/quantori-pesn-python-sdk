import sys
from os.path import abspath, dirname as d, join

root_dir = d(d(abspath(__file__)))

sys.path.append(join(root_dir, 'src'))
