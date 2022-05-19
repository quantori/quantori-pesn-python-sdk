# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<div>
    <h1>name</h1>

    
        <p><img src="data:image/png;base64,aW1hZ2UgY29udGVudA==" alt="Image preview" style="width:100%;"/></p>
    

</div>'''
