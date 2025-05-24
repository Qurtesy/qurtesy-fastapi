from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, JSONAttribute


class StructureModel(Model):
    class Meta:
        table_name = 'structure'

    id = UnicodeAttribute(hash_key=True)
    category_config = JSONAttribute(null=True)
