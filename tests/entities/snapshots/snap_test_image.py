# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<div style="margin: 10px 10px; padding: 6px 10px; border: solid 1px #f5f5f5;">
    <h2>name</h2>
    
    <div class="parent">
        <div class="image-container">
            <img src="data:image/png;base64,aW1hZ2UgY29udGVudA==" alt="Image preview" style="width:100%;"/>
        </div>
    </div>
    
</div>'''
