import graphene


class MutationMixinErrors(object):
    error = graphene.Boolean()
    errors = graphene.String()
