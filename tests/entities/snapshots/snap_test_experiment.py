# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_html 1'] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:;base64,iVBORw0KGgo=">
    <title>name</title>
    <style>
        h1 {
            margin-top: 1.7rem;
            margin-bottom: 0.3rem;
            font-size: 1.6rem;
        }

        h2 {
            margin-top: 1.2rem;
            margin-bottom: 0.3rem;
            font-size: 1.2rem;
        }

        table.props th, table.props td {
            text-align: left;
            padding: 3px;
        }

        table.dataframe {
            border-collapse: collapse;
            min-width: 600px;
        }

        table.dataframe td, table.dataframe th {
            padding: 0.4rem 0.8rem;
            text-align: left;
            border: 1px solid #666;
            font-size: 0.7rem;
        }
    </style>
</head>
<body>
<table class="props">
    <tr>
        <th>Experiment name:</th>
        <td>name</td>
    </tr>
    <tr>
        <th>Description:</th>
        <td>text</td>
    </tr>
    <tr>
        <th>Last edited at:</th>
        <td>01:01:01 2018-06-01</td>
    </tr>
    <tr>
        <th>State:</th>
        <td></td>
    </tr>
</table>




</body>
</html>'''
