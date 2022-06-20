import factory

from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry
from tests.entities.factories import EIDFactory


class StoichiometryFactory(factory.Factory):
    class Meta:
        model = Stoichiometry

    eid = factory.SubFactory(EIDFactory)
