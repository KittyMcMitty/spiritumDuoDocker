from ariadne import gql
from .mutation_type import mutation
from api.datacreation import CreateUser
type_defs=gql(
    """
        extend type Mutation{
            createUser(input:CreateUserInput): User
        }
        input CreateUserInput{
            firstName:String!
            lastName:String!
            username:String!
            password:String!
            isStaff:Boolean!
            isSuperuser:Boolean!
            
            department:String!
        }
    """
)

@mutation.field("createUser")
async def resolve_create_user(_=None, into=None, input=None):
    try:
        newUser=await CreateUser(
            first_name=input["firstName"],
            last_name=input["lastName"],
            username=input["username"],
            password=input["password"],
            is_staff=input["isStaff"],
            is_superuser=input["isSuperuser"],

            department=input["department"]
        )
        return newUser
    except:
        return None