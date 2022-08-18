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
                
                    <th>Task ID</th>
                
                    <th>Task Type</th>
                
                    <th>Reference ID</th>
                
                </tr>
            </thead>
            <tbody>
            
                <tr>
                
                    
                        
                        <td><a href="task:VALUE"> Task-4 </a></td>
                        
                    
                
                    
                        
                        <td> Task </td>
                        
                    
                
                    
                        
                        <td><a href="experiment:VALUE">  </a></td>
                        
                    
                
                </tr>
            
            </tbody>
        </table>
    </div>
</div>
'''
