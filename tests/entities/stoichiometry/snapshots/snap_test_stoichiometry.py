# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_stoichiometry_get_html 1'] = '''<div>
    
        <h2>Reactants</h2>
        
<table border="1">
    <thead>
        <tr>
        
            <th>Name</th>
        
        </tr>
    </thead>
    <tbody>
    
        <tr>
        
            <td>HCl</td>
        
        </tr>
    
        <tr>
        
            <td>NaOH</td>
        
        </tr>
    
    </tbody>
</table>

    

    
        <h2>Products</h2>
        
<table border="1">
    <thead>
        <tr>
        
            <th>Name</th>
        
        </tr>
    </thead>
    <tbody>
    
        <tr>
        
            <td>H2O</td>
        
        </tr>
    
        <tr>
        
            <td>sodium chloride</td>
        
        </tr>
    
    </tbody>
</table>

    

    
        <h2>Solvents</h2>
        
<table border="1">
    <thead>
        <tr>
        
        </tr>
    </thead>
    <tbody>
    
        <tr>
        
        </tr>
    
    </tbody>
</table>

    

    
        <h2>Conditions</h2>
        
<table border="1">
    <thead>
        <tr>
        
        </tr>
    </thead>
    <tbody>
    
        <tr>
        
        </tr>
    
    </tbody>
</table>

    
</div>'''
