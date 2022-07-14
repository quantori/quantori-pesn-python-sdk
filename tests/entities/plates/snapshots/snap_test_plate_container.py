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
                
                    <th>Well ID</th>
                
                    <th>Row</th>
                
                    <th>Column</th>
                
                    <th>Plate</th>
                
                    <th>Order</th>
                
                    <th>Plate ID</th>
                
                </tr>
            </thead>
            <tbody>
                
                <tr>
                    
                        
                            <td>A1</td>
                        
                    
                        
                            <td>A</td>
                        
                    
                        
                            <td>1</td>
                        
                    
                        
                            <td>Plate-1</td>
                        
                    
                        
                            <td>1</td>
                        
                    
                        
                            <td></td>
                        
                    
                </tr>
                
                <tr>
                    
                        
                            <td>A2</td>
                        
                    
                        
                            <td>A</td>
                        
                    
                        
                            <td>2</td>
                        
                    
                        
                            <td>Plate-1</td>
                        
                    
                        
                            <td>1</td>
                        
                    
                        
                            <td></td>
                        
                    
                </tr>
                
            </tbody>
        </table>
    </div>
</div>
'''
