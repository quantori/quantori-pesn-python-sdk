# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<div style="margin: 10px 10px; padding: 6px 10px; border: solid 1px #f5f5f5;">
    <h2>name</h2>
    
    <div>
        <span>Modified: 01:01 01.06.2018</span>
    </div>
    
</div>'''
