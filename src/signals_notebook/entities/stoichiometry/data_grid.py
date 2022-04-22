from decimal import Decimal
from enum import Enum
from typing import Any, Generic, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.generics import GenericModel


class Cell(BaseModel):
    value: Union[bool, Decimal, str]
    display: Optional[str] = Field(default='')
    units: Optional[str]

    class Config:
        frozen = True


class Row(BaseModel):
    row_id: Union[UUID, str]

    class Config:
        frozen = True


RowClass = TypeVar('RowClass', bound=Row)


class Rows(GenericModel, Generic[RowClass]):
    __root__: list[RowClass]
    _rows_by_id: dict[Union[str, UUID], RowClass] = PrivateAttr(default={})

    def __init__(self, **data: Any):
        super(Rows, self).__init__(**data)

        for row in self.__root__:
            self._rows_by_id[row.row_id] = row

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, index: Union[int, str, UUID]) -> RowClass:
        if isinstance(index, int):
            return self.__root__[index]

        if isinstance(index, str):
            try:
                return self._rows_by_id[index]
            except KeyError:
                return self._rows_by_id[UUID(index)]

        if isinstance(index, UUID):
            return self._rows_by_id[index]

        raise IndexError('Invalid index')


class Reactant(Row):
    rxnid: Cell
    name: Optional[Cell]
    cas: Optional[Cell]
    formula: Cell
    mf: Cell
    mw: Cell
    em: Cell
    limit: Optional[Cell]
    eq: Optional[Cell]
    sm: Optional[Cell]
    moles: Optional[Cell]
    loading: Optional[Cell]
    molarity: Optional[Cell]
    volume: Optional[Cell]
    density: Optional[Cell]
    wt: Optional[Cell]
    supplier: Optional[Cell]
    lot: Optional[Cell]
    iupac_name: Cell = Field(alias='IUPACName')
    barcode: Optional[Cell]
    material_id: Optional[Cell] = Field(alias='materialId')
    container_id: Optional[Cell] = Field(alias='containerId')
    inchi: Optional[str]
    hash: Optional[str]

    class Config:
        frozen = True


class Reactants(Rows[Reactant]):
    pass


class Product(Row):
    rxnid: Cell
    product_id: Cell = Field(alias='productId')
    name: Optional[Cell]
    formula: Cell
    mf: Cell
    mw: Cell
    em: Cell
    theo_mass: Optional[Cell] = Field(alias='theoMass')
    actual_mass: Optional[Cell] = Field(alias='actualMass')
    purity: Optional[Cell]
    density: Optional[Cell]
    yield_: Optional[Cell] = Field(alias='yield')
    theo_mol: Optional[Cell] = Field(alias='theoMol')
    actual_mol: Optional[Cell] = Field(alias='actualMol')
    conversion: Optional[Cell]
    iupac_name: Cell = Field(alias='IUPACName')
    barcode: Optional[Cell]
    material_id: Optional[Cell] = Field(alias='materialId')
    container_id: Optional[Cell] = Field(alias='containerId')
    inchi: Optional[str]
    hash: Optional[str]

    class Config:
        frozen = True


class Products(Rows[Product]):
    pass


class Solvent(Row):
    solvent: Cell
    ratio: Cell
    volume: Optional[Cell]

    class Config:
        frozen = True


class Solvents(Rows[Solvent]):
    pass


class Condition(Row):
    pressure: Optional[Cell]
    temperature: Optional[Cell]
    duration: Optional[Cell]

    class Config:
        frozen = True


class Conditions(Rows[Condition]):
    pass


class DataGrids(BaseModel):
    reactants: Reactants
    products: Products
    solvents: Solvents
    conditions: Conditions


class DataGridKind(str, Enum):
    REACTANTS = 'reactants'
    PRODUCTS = 'products'
    SOLVENTS = 'solvents'
    CONDITIONS = 'conditions'
