from aiodataloader import DataLoader
from models import OnPathway
from typing import List, Union

class OnPathwayByIdLoader(DataLoader):
    loader_name = "_on_pathway_loader"
    _db=None

    def __init__(self, db):
        super().__init__()
        self._db=db

    async def fetch(self, keys)->List[OnPathway]:
        result=None
        async with self._db.acquire(reuse=False) as conn:
            query=OnPathway.query.where(OnPathway.id.in_(keys))
            result=await conn.all(query)
        returnData={}
        for key in keys:
            returnData[key]=None
        for row in result:
            returnData[row.id]=row
            
        return returnData

    async def batch_load_fn(self, keys)->List[OnPathway]:
        unsortedDict=await self.fetch([int(i) for i in keys])
        sortedList=[]
        for key in keys:
            sortedList.append(unsortedDict.get(int(key)))
        return sortedList

    @classmethod
    async def load_from_id(cls, context=None, id=None)->Union[OnPathway, None]:
        if not id:
            return None
        if cls.loader_name not in context:
            context[cls.loader_name]=cls(db=context['db'])
        return await context[cls.loader_name].load(id)

    @classmethod
    async def load_many_from_id(cls, context=None, ids=None)->Union[List[OnPathway], None]:
        if cls.loader_name not in context:
            context[cls.loader_name] = cls(db=context['db'])
        return await context[cls.loader_name].load_many(ids)

class OnPathwaysByPatient:
    @staticmethod
    async def load_from_id(context=None, id=None)->Union[List[OnPathway], None]:
        if not context or not id:
            return None
        _gino=context['db']
        async with _gino.acquire(reuse=False) as conn:
            onPathways=await conn.all(OnPathway.query.where(OnPathway.patient==id))
        if OnPathwayByIdLoader.loader_name not in context:
            context[OnPathwayByIdLoader.loader_name]=OnPathwayByIdLoader(db=context['db'])
        for oP in onPathways:
            context[OnPathwayByIdLoader.loader_name].prime(oP.id, oP)
        return onPathways