# Quantori Python SDK for PerkinElmer Signals Notebook
Copyright (c) 2022 Quantori.

`pesn-sdk` is a Python package that provides an interface between your Python application and PerkinElmer's external API of Signals Notebook.

## Pre-requisites

We assume, that you have already contacted with PerkinElmer and have a working instance of Signals Notebook.

### Obtain an API key

Visit the page `https://<your signals notebook instance>/snconfig/settings/apikey` and generate an API Key

## Installation

```shell
pip install pesn-sdk
```

## Usage

Import and initialize the API instance with your Signals Notebook host and API-token
```python
from signals_notebook.api import SignalsNotebookApi

SignalsNotebookApi.init('https://signalsnotebook.perkinelmer.cloud', '<your api key>')
```
Then you can perform CRUD operations with such entities as Notebook, Experiment, etc.

### Examples
Create a new Notebook
```python
from signals_notebook.entities.notebook import Notebook

notebook = Notebook.create(name='Test creation by SDK', description='Created by me')
```
change its fields
```python
notebook.name = 'Changed name'
notebook.save()
```
finally delete it
```python
notebook.delete()
```
Also, you can retrieve all existing notebooks
```python
notebooks = Notebook.get_list()
```
or one specified by id
```python
from signals_notebook.entities.entity_store import EntityStore
notebook = EntityStore.get("journal:111a8a0d-2772-47b0-b5b8-2e4faf04119e")
```
Deletion can be performed without retrieving the whole object if you know an id
```python
EntityStore.delete("journal:111a8a0d-2772-47b0-b5b8-2e4faf04119e")
```
Jupyter Notebooks with examples see in examples folder

## Additional information
 - [Examples of usage](examples)
 - [API Reference](https://quantori.github.io/quantori-pesn-python-sdk/signals_notebook/)
 - [Developers notes](DEVNOTES.md)

## License
Quantori Python SDK for PerkinElmer Signals Notebook is released under [Apache License, Version 2.0](LICENSE)
