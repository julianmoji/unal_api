import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required

from core.authentication.mutations import CreateUser
from core.authentication.types import UserType
from django.contrib.auth import get_user_model


class Query(object):
    hello = graphene.String(default_value="Hi!")
    users = graphene.List(UserType)

    @login_required
    def resolve_users(self, info):
        return get_user_model().objects.all()

    logged_in = graphene.Field(UserType)

    @login_required
    def resolve_logged_in(self, info):
        return info.context.user


class Mutation(object):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_user = CreateUser.Field()
