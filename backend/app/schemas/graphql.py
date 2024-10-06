import ariadne


class User(ariadne.ObjectType):
    id = ariadne.ID()
    name = ariadne.String()

class Query(ariadne.ObjectType):
    users = ariadne.List(User)

    def resolve_users(self, info):
        return [User(id=1, name="John Doe"), User(id=2, name="Jane Smith")]

schema = ariadne.Schema(query=Query)
