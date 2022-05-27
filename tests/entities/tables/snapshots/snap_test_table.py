# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<div class="table-wrapper" style="margin: 10px 10px; padding: 6px 10px; border: solid 1px #f5f5f5;">
    <div class="table-scroll">
        <h2>name</h2>
        <table>
            <thead>
                <tr>
                
                    <th>Col. Text</th>
                
                    <th>Col. Date/Time</th>
                
                    <th>Col. Number</th>
                
                    <th>Col. Number w/Uni</th>
                
                    <th>Col. Ext. Hyperlink</th>
                
                    <th>Col. Autotext List</th>
                
                    <th>Col. Checkbox</th>
                
                    <th>Col. Internal Reference</th>
                
                    <th>Col. List</th>
                
                    <th>Col. Integer</th>
                
                    <th>Col. Multi Select List</th>
                
                    <th>Col. Attribute List</th>
                
                    <th>Col. Multi Attribute List</th>
                
                </tr>
            </thead>
            <tbody>
            
                <tr>
                
                    
                    <td>Text</td>
                    
                
                    
                    <td>2021-12-31 20:00:00+00:00</td>
                    
                
                    
                    <td>123</td>
                    
                
                    
                    <td>123 K</td>
                    
                
                    
                    <td>link</td>
                    
                
                    
                    <td>Autotext list option 1</td>
                    
                
                    
                    <td></td>
                    
                
                    
                    <td>ChemDraw Document</td>
                    
                
                    
                    <td>Option 1</td>
                    
                
                    
                    <td>123</td>
                    
                
                    
                    <td>
                        <div style="margin-bottom: 4px">
                            
                            <div style="margin-bottom: 4px; border-radius: 5px; background: #e6f6ff">
                                <div style="justify-content: center; padding: 4px">
                                    <p style="color: #00A0E1 !important;">Multi Option 1</p>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 4px; border-radius: 5px; background: #e6f6ff">
                                <div style="justify-content: center; padding: 4px">
                                    <p style="color: #00A0E1 !important;">Multi Option 2</p>
                                </div>
                            </div>
                            
                        </div>
                    </td>
                    
                
                    
                    <td>Option 1</td>
                    
                
                    
                    <td>
                        <div style="margin-bottom: 4px">
                            
                            <div style="margin-bottom: 4px; border-radius: 5px; background: #e6f6ff">
                                <div style="justify-content: center; padding: 4px">
                                    <p style="color: #00A0E1 !important;">Option 1</p>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 4px; border-radius: 5px; background: #e6f6ff">
                                <div style="justify-content: center; padding: 4px">
                                    <p style="color: #00A0E1 !important;">Option 2</p>
                                </div>
                            </div>
                            
                        </div>
                    </td>
                    
                
                </tr>
            
            </tbody>
        </table>
    </div>
</div>'''
