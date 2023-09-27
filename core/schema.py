import graphene

import core.authentication.schema
import core.grade_scoring.schema


class Query(graphene.ObjectType, core.authentication.schema.Query, core.grade_scoring.schema.Query):
    class Meta:
        pass


class Mutation(graphene.ObjectType, core.authentication.schema.Mutation, core.grade_scoring.schema.Mutation):
    class Meta:
        pass


schema = graphene.Schema(query=Query, mutation=Mutation)
