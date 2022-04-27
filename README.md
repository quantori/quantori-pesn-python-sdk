# PerkinElmer Signals Notebook Python SDK

## Installation
There are two ways to install the library: by https and ssh

### By https
```shell
pip install git+https://bitbucket.org/quantori/pesn-python-sdk
```
You will be asked for the username and password.

### By ssh
You need to register your ssh key [here](https://bitbucket.org/account/settings/ssh-keys/) before using this way.
```shell
pip install git+ssh://git@bitbucket.org/quantori/pesn-python-sdk.git
```

## Usage

Import and initialize the API instance with your Signals Notebook host and API-token
```python
from signals_notebook.api import SignalsNotebookApi

SignalsNotebookApi.init(
    "https://signalsnotebook.perkinelmer.cloud",
    "uA0nIQMT1tMc5iGvjawju3MYsmPDFc==",
)
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
