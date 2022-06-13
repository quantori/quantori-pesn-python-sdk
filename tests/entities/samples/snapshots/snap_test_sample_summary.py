# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''
<div class="table-wrapper" style="margin: 10px 10px; padding: 6px 10px; border: solid 1px #f5f5f5;">
    <div class="table-scroll">
        <h2>name</h2>
        <table>
            <thead>
                <tr>
                
                    <th>Name</th>
                
                    <th>ID</th>
                
                    <th>Created Date</th>
                
                    <th>Description</th>
                
                    <th>Comments</th>
                
                    <th>Amount</th>
                
                    <th>Attached Docs</th>
                
                    <th>Template</th>
                
                </tr>
            </thead>
            <tbody>
            
                <tr>
                
                    <td>Sub-experiment-1</td>
                
                    <td>Sample-1764</td>
                
                    <td>2022-06-06T08:54:51.677884071Z</td>
                
                    <td>Description 1</td>
                
                    <td>Comments 1</td>
                
                    <td>1 g</td>
                
                    <td>0</td>
                
                    <td>Sample</td>
                
                </tr>
            
                <tr>
                
                    <td>Sub-experiment-3</td>
                
                    <td>Sample-1774</td>
                
                    <td>2022-06-08T10:35:27.346810619Z</td>
                
                    <td></td>
                
                    <td></td>
                
                    <td></td>
                
                    <td>0</td>
                
                    <td>Sample</td>
                
                </tr>
            
            </tbody>
        </table>
    </div>
</div>
'''
