# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<div>
    <h2>name</h2>
    <table border="1">
        <tbody>
            <tr>
            
            </tr>
        </tbody>
    </table>
    <table border="1">
        <tbody>
            <tr>
            
                <td>Modified: 01:01 01.06.2018</td>
            
            
                <td>Description: text</td>
            
            </tr>
        </tbody>
    </table>
</div>'''