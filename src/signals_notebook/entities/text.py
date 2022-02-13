from signals_notebook.entities.entity import Entity
from signals_notebook.types import EntitySubtype


class Text(Entity):
    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.TEXT

    @classmethod
    def create(cls, *, container: Entity, name: str, content: str = '', force: bool = True) -> 'Text':
        return container.add_child(name=name, content=content, child_class=cls, content_type='text/plain', force=force)
