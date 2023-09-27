import binascii

import graphene
from django.db.models import FloatField
from django.db.models.aggregates import Avg
from graphene.types.enum import EnumMeta
from graphql_relay import from_global_id


def clean_global_ids(data, exclude_fields=None):
    if exclude_fields is None:
        exclude_fields = []

    if type(data) is list:
        for index, item in enumerate(data):
            data[index] = clean_global_ids(item)

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                if key not in exclude_fields and "_id" in key or key == "id":
                    try:
                        data[key] = int(from_global_id(value.strip())[1])
                    except (UnicodeDecodeError, TypeError):
                        if key == "id" or key[-3:] == "_id":
                            raise ValueError(f"El valor para el campo {key} es inválido.")
                        data[key] = value.strip()
                    except (binascii.Error, ValueError):
                        if key == "id" or key[-3:] == "_id":
                            raise ValueError(f"El valor para el campo {key} es inválido.")
                else:
                    data[key] = value.strip()

            elif isinstance(value, dict):
                data[key] = clean_global_ids(value)

            elif isinstance(value, list):
                result = []
                for item in value:
                    result.append(clean_global_ids(item))
                data[key] = result

            elif type(value).__class__.__name__ == EnumMeta.__name__:
                data[key] = value.value
            elif type(value).__class__ == graphene.types.enum.EnumType:
                data[key] = value._value_
        return data

    if isinstance(data, str):
        try:
            return from_global_id(data.strip())[1]
        except (UnicodeDecodeError, TypeError, binascii.Error, ValueError):
            return data

    if type(data).__class__.__name__ == EnumMeta.__name__:
        return data.value
    elif type(data).__class__ == graphene.types.enum.EnumType:
        return data._value_

    return data


class AggregateConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    overall_average = graphene.Float()

    def resolve_overall_average(self, info, **kwargs):
        return self.iterable.aggregate(Avg("score", output_field=FloatField())).get("score__avg")
