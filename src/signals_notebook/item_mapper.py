from typing import Type

from signals_notebook.entities import Entity


class ItemMapper:
    @staticmethod
    def get_item_class(item_name: str) -> Type['Entity']:
        return [
            subclass
            for subclass in Entity.get_subclasses()
            if subclass._get_entity_type() and subclass._get_entity_type().value == item_name
        ][0]
