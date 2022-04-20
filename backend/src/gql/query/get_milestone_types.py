from .query_type import query
from dataloaders import MilestoneTypeLoader
from authentication.authentication import needsAuthorization
from graphql.type import GraphQLResolveInfo
from SdTypes import Permissions


@query.field("getMilestoneTypes")
@needsAuthorization([Permissions.MILESTONE_TYPE_READ])
async def resolve_get_milestone_types(
    obj=None,
    info: GraphQLResolveInfo = None
):
    return await MilestoneTypeLoader.load_all(info.context)
