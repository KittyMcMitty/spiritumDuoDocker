from ariadne.objects import ObjectType
from dataloaders import (
    MilestoneTypeLoaderByPathwayId,
)
from models import MilestoneType
from graphql.type import GraphQLResolveInfo

PathwayObjectType = ObjectType("Pathway")


@PathwayObjectType.field("milestoneTypes")
async def resolve_pathways(
    obj: MilestoneType = None, info: GraphQLResolveInfo = None, *_
):
    return await MilestoneTypeLoaderByPathwayId.load_from_id(
        context=info.context, id=obj.id)
