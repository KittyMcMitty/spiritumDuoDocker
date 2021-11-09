import graphene

from api.dao.RoleDAO import RoleDAO

class _RoleQueries(graphene.ObjectType):
    def _resolve_roles(root, info): # Gets all data 
        return RoleDAO.read()
    def _resolve_role_search(root, info, id, name): # Gets specified data only
        return RoleDAO.read(id=id, name=name)