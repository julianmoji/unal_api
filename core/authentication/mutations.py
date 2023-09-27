import graphene
from django.contrib.auth import get_user_model

from core.authentication.types import UserType


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, username, password):
        User = get_user_model()
        new_user = User(email=email, username=username)
        new_user.set_password(password)
        new_user.save()
        return CreateUser(user=new_user)
