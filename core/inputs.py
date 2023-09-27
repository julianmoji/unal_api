import graphene
from django.db import models
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.subclass_with_meta import SubclassWithMeta_Meta
from graphene_django.registry import get_global_registry
from graphene_django.types import construct_fields


class Input(graphene.InputObjectType):
    _model = None
    _only_fields = None
    _exclude_fields = None
    _optional_fields = None

    @classmethod
    def __init_subclass_with_meta__(
        cls, model=None, registry=None, only_fields=(), exclude_fields=(), optional_fields=(), **options
    ):
        if optional_fields and not only_fields:
            only_fields = optional_fields

        cls._model = model
        cls._optional_fields = optional_fields
        cls._exclude_fields = exclude_fields
        cls._only_fields = only_fields
        model_fields = {}

        if not registry:
            registry = get_global_registry()
        if model:
            model_fields = yank_fields_from_attrs(
                construct_fields(model, registry, only_fields, exclude_fields, False),
                _as=graphene.Field,
            )

        for key, value in model_fields.items():
            set_id_to_key = False  # Esta variable utilizada para configurar la key + _id para los foreignKey

            if isinstance(value, graphene.Dynamic):
                set_id_to_key = True
                value = graphene.GlobalID()

            field = model._meta.get_field(key)
            if isinstance(field, models.PositiveSmallIntegerField):
                choices = []
            else:
                choices = field.choices if hasattr(field, "choices") else []

            if isinstance(field, models.DecimalField):
                value = graphene.Field(graphene.Decimal, required=True)

            if choices:
                converted = registry.get_converted_field(f"{model._meta.model_name.lower()}_{key}")
                if converted:
                    value = converted
                else:
                    # Todo: Poner está lógica en un method de esta clase
                    tuples_list = [(i[0], i[0]) for i in choices]
                    keep_label_value_of_enums = options.get("keep_label_value_of_enums", [])
                    if key in keep_label_value_of_enums:
                        tuples_list = [(i[1], i[0]) for i in choices]
                    value = graphene.Enum(f"{model._meta.model_name.lower()}_{key}", tuples_list)(required=True)

            if key in optional_fields:
                if choices:
                    value.kwargs = {"required": False}
                else:
                    type_ = value.type if isinstance(value.type, SubclassWithMeta_Meta) else value.type.of_type
                    value = type_(description=value.description)

            setattr(cls, key if not set_id_to_key else f"{key}_id", value)
            if isinstance(value, graphene.Enum):
                registry.register_converted_field(f"{model._meta.model_name.lower()}_{key}", value)

        options = {}
        super(Input, cls).__init_subclass_with_meta__(**options)

    @staticmethod
    def get_default_optional_fields(model):
        """
        Por defecto el id es opcional para permitir actualizar con el mismo input
        """
        return ["id"]

    @staticmethod
    def get_default_exclude_fields(model):
        """
        Por defecto se excluyen todas las relaciones inversas
        """
        result = []
        for f in model._meta.get_fields():
            if isinstance(f, ManyToOneRel) or isinstance(f, ManyToManyRel):
                if hasattr(f, "related_name") and getattr(f, "related_name"):
                    result.append(getattr(f, "related_name"))
                else:
                    result.append(f"{f.name}_set")
            elif f.name in ["created", "created_by", "created_at", "modified", "modified_by", "modified_at"]:
                result.append(f.name)
        return result

    @staticmethod
    def get_defined_fields_on_model_class(model):
        return [field.name for field in model._meta._get_fields(reverse=False, include_parents=False)]
