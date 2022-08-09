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
            color: #00A0E1;
        }

        table.props th, table.props td {
            text-align: left;
            padding: 3px;
        }
        .table-scroll {
            overflow:auto;
        }
        .table-wrapper {
            position:relative;
        }
        table, th, td {
            border: 1px solid #cccccc;
            border-collapse: collapse;
            table-layout: fixed;
        }
        .table-wrapper th, td {
            padding: 10px 20px;
        }
        .table-wrapper table td {
            text-align: center;
            vertical-align: middle;
            padding: 5px;
        }
        .parent {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            aspect-ratio: auto;
        }
        .image-container {
            width: 60%;
            height: 60%;
            overflow: hidden;
        }

        .image-container img {
            width: 100%;
            min-height: 100%;
            object-fit: cover;
        }

    </style>
</head>
<body>
<table class="props" style="margin: 10px 10px; padding: 6px 10px;">
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
