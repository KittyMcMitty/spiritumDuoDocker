import graphene

from api.dao.PathwayDAO import PathwayDAO

class _PathwayQueries(graphene.ObjectType):
    def _resolve_pathways(root, info): # Gets all data 
        return PathwayDAO.read()
    def _resolve_pathway_search(root, info, id=None, name=None): # Gets specified data only
        return PathwayDAO.read(id=id, name=name)
    def _resolve_patient_pathways(root, info, patientId=None):
        return PathwayDAO.readRelations(patientId=patientId)
    def _resolve_pathway_patients(root, info, pathwayId=None):
        return PathwayDAO.readRelations(pathwayId=pathwayId)