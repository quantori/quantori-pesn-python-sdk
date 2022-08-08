# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<div style="margin: 10px 10px; padding: 6px 10px; border: solid 1px #f5f5f5;">
    <h2>nature</h2>
    
    
    <a href="data:text/csv;base64,UGxhdGUsV2VsbCxSb3csQ29sdW1uLE5hbWUNCg==" download="nature.csv">DOWNLOAD .CSV FILE</a>
    
    
</div>'''
