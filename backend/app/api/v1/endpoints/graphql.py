from ariadne import QueryType, graphql_sync, make_executable_schema
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocket

from app.core.db import get_database_session

type_defs = """
    type Query {
        hello: String!
    }
"""

query = QueryType()

@query.field("hello")
def resolve_hello(_, info):
    return "Hello, GraphQL!"

schema = make_executable_schema(type_defs, query)

# Custom context setup method
def get_context_value(request_or_ws: Request | WebSocket, _data) -> dict:
    return {
        "request": request_or_ws,
        "db": request_or_ws.scope["db"],
    }

router = APIRouter()


# Create GraphQL App instance
graphql_app = GraphQL(
    schema,
    debug=True,
    context_value=get_context_value,
    websocket_handler=GraphQLTransportWSHandler(),
)

@router.post("/graphql")
async def graphql_server(request: Request):
    data = await request.json()
    success, result = graphql_sync(schema, data)
    status_code = 200 if success else 400
    return JSONResponse(result, status_code=status_code)

# Handle GET requests to serve GraphQL explorer
# Handle OPTIONS requests for CORS
@router.get("/graphql/")
@router.options("/graphql/")
async def handle_graphql_explorer(request: Request):
    return await graphql_app.handle_request(request)

# Handle POST requests to execute GraphQL queries
@router.post("/graphql/")
async def handle_graphql_query(
    request: Request,
    db = Depends(get_database_session),
):
    # Expose database connection to the GraphQL through request's scope
    request.scope["db"] = db
    return await graphql_app.handle_request(request)


# Handle GraphQL subscriptions over websocket
@router.websocket("/graphql")
async def graphql_subscriptions(
    websocket: WebSocket,
    db = Depends(get_database_session),
):
    # Expose database connection to the GraphQL through request's scope
    websocket.scope["db"] = db
    await graphql_app.handle_websocket(websocket)
