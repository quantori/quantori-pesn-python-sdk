from decimal import Decimal
from enum import Enum
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class Cell(BaseModel):
    value: Union[bool, Decimal, str]
    display: Optional[str] = Field(default='')
    units: Optional[str]

    class Config:
        frozen = True


class Row(BaseModel):
    row_id: Union[int, UUID]
    inchi: Optional[str] = Field(default='')
    hash: Optional[str] = Field(default='')

    class Config:
        frozen = True


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

    class Config:
        frozen = True


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

    class Config:
        frozen = True


class Solvent(Row):
    solvent: Cell
    ratio: Cell
    volume: Optional[Cell]

    class Config:
        frozen = True


class Condition(Row):
    pressure: Optional[Cell]
    temperature: Optional[Cell]
    duration: Optional[Cell]

    class Config:
        frozen = True


class DataGrids(BaseModel):
    reactants: list[Reactant]
    products: list[Product]
    solvents: list[Solvent]
    conditions: list[Condition]


class DataGridKind(str, Enum):
    REACTANTS = 'reactants'
    PRODUCTS = 'products'
    SOLVENTS = 'solvents'
    CONDITIONS = 'conditions'
