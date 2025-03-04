import strawberry
from users.schema import Query as UserQuery, Mutation as UserMutation
from articles.schema import Query as ArticleQuery, Mutation as ArticleMutation

@strawberry.type
class Query(UserQuery, ArticleQuery):
    pass

@strawberry.type
class Mutation(ArticleMutation, UserMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)