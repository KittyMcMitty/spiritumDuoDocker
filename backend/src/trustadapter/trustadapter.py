import requests
import json
from models import Milestone, Patient, DecisionPoint, OnPathway
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import date, datetime
from config import config

class Patient_IE:
    def __init__(self, 
        id:int=None, 
        first_name:str=None, 
        last_name:str=None, 
        hospital_number:str=None,
        national_number:str=None, 
        communication_method:str=None,
        date_of_birth:date=None
    ):
        self.id=id
        self.first_name=first_name
        self.last_name=last_name
        self.hospital_number=hospital_number
        self.national_number=national_number
        self.communication_method=communication_method
        self.date_of_birth=date_of_birth

class Milestone_IE:
    def __init__(self, 
        id:int=None,
        hospital_number:str=None, 
        current_state:str=None, 
        added_at:date=None, 
        updated_at:date=None
    ):
        self.id=id
        self.hospital_number=hospital_number
        self.current_state=current_state
        self.added_at=added_at
        self.updated_at=updated_at
       


class TrustAdapter(ABC):
    """
    Integration Engine Abstract Base Class
    This class represents the interface SD uses to communicate with a backend hospital system.
    """

    @abstractmethod
    async def load_patient(self, hospitalNumber: str = None) -> Optional[Patient_IE]:
        """
        Load single patient
        :param record_id: String ID of patient
        :return: Patient if found, null if not
        """

    async def load_many_patients(self, hospitalNumbers:List=None) -> List[Optional[Patient_IE]]:
        """
        Load many patients
        :param record_ids: List of patient ids to load
        :return: List of patients, or empty list if none found
        """

    @abstractmethod
    async def create_milestone(self, milestone: Milestone = None) -> Milestone_IE:
        """
        Create a Milestone
        :param milestone: Milestone to create
        :return: String ID of created milestone
        """

    @abstractmethod
    async def load_milestone(self, recordId: str = None) -> Optional[Milestone_IE]:
        """
        Load a Milestone
        :param record_id: ID of milestone to load
        :return: Milestone, or null if milestone not found
        """

    @abstractmethod
    async def load_many_milestones(self, recordIds: str = None) -> List[Optional[Milestone_IE]]:
        """
        Load many milestones
        :param record_ids: IDs of milestones to load
        :return: List of milestones, or empty list if none found
        """
        
    
class TrustAdapterNotFoundException(Exception):
    """
    This is raised when a specified trust adapter
    cannot be found
    """

def GetTrustAdapter():
    try:
        return globals()[config['TRUST_ADAPTER_NAME']]
    except KeyError:
        raise TrustAdapterNotFoundException()
        

class PseudoTrustAdapter(TrustAdapter):
    """
    Pseudo Integration Engine

    This is the Integration Engine implementation for the pseudo-trust backend.
    """

    def __init__(self, auth_token: str = None):
        """
        Constructor. Requires an authentication token.
        :param auth_token: String token to be supplied to pseudo-trust with each request
        """
        self.authToken = auth_token
        self.TRUST_INTEGRATION_ENGINE_ENDPOINT="http://sd-pseudotie:8081"

    async def load_patient(self, hospitalNumber: str = None) -> Optional[Patient_IE]:
        result = requests.get(self.TRUST_INTEGRATION_ENGINE_ENDPOINT+"/patient/hospital/"+hospitalNumber, cookies={"SDSESSION":self.authToken})
        if result.status_code!=200:
            raise Exception(f"HTTP{result.status_code} received")
        record=json.loads(result.text)
        return Patient_IE(
            id=record['id'],
            first_name=record['first_name'], 
            last_name=record['last_name'], 
            hospital_number=record['hospital_number'], 
            national_number=record['national_number'], 
            communication_method=record['communication_method'],
            date_of_birth=datetime.strptime(record['date_of_birth'], "%Y-%m-%d").date()
        )

    async def load_many_patients(self, hospitalNumbers: List = None) -> List[Optional[Patient_IE]]:
        retVal=[]
        for hospNo in hospitalNumbers:
            result = requests.get(self.TRUST_INTEGRATION_ENGINE_ENDPOINT+"/patient/hospital/"+hospNo, cookies={"SDSESSION":self.authToken})
            if result.status_code!=200:
                raise Exception(f"HTTP{result.status_code} received")
            record=json.loads(result.text)
            retVal.append(
                Patient_IE(
                    id=record['id'],
                    first_name=record['first_name'], 
                    last_name=record['last_name'], 
                    hospital_number=record['hospital_number'], 
                    national_number=record['national_number'], 
                    communication_method=record['communication_method'],
                    date_of_birth=datetime.strptime(record['date_of_birth'], "%Y-%m-%d").date()
                )
            )
        return retVal

    async def create_milestone(self, milestone: Milestone = None) -> Milestone_IE:
        decision_point:DecisionPoint=await DecisionPoint.query.where(DecisionPoint.id==milestone.decision_point_id).gino.one()
        on_pathway:OnPathway=await OnPathway.query.where(OnPathway.id==decision_point.on_pathway_id).gino.one()
        patient:Patient=await Patient.query.where(Patient.id==on_pathway.patient_id).gino.one()
        if milestone.current_state:
            result = requests.post(self.TRUST_INTEGRATION_ENGINE_ENDPOINT+"/milestone", params={
                "currentState":milestone.current_state
            }, cookies={"SDSESSION":self.authToken})
        else:
            result = requests.post(self.TRUST_INTEGRATION_ENGINE_ENDPOINT+"/milestone",cookies={"SDSESSION":self.authToken})
        tie_milestone=json.loads(result.text)

        try:
            _added_at=datetime.strptime(tie_milestone['added_at'], "%Y-%m-%dT%H:%M:%S")
            _updated_at=datetime.strptime(tie_milestone['updated_at'], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            _added_at=datetime.strptime(tie_milestone['added_at'], "%Y-%m-%dT%H:%M:%S.%f")
            _updated_at=datetime.strptime(tie_milestone['updated_at'], "%Y-%m-%dT%H:%M:%S.%f")
        
        return Milestone_IE(
            id=tie_milestone['id'],
            current_state=tie_milestone['current_state'],
            added_at=_added_at,
            updated_at=_updated_at
        )

    async def load_milestone(self, recordId: str = None) -> Optional[Milestone_IE]:
        result = requests.get(self.TRUST_INTEGRATION_ENGINE_ENDPOINT+"/milestone/"+str(recordId), cookies={"SDSESSION":self.authToken})
        if result.status_code!=200:
            raise Exception(f"HTTP{result.status_code} received")
        record=json.loads(result.text)

        try:
            _added_at=datetime.strptime(record['added_at'], "%Y-%m-%dT%H:%M:%S")
            _updated_at=datetime.strptime(record['updated_at'], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            _added_at=datetime.strptime(record['added_at'], "%Y-%m-%dT%H:%M:%S.%f")
            _updated_at=datetime.strptime(record['updated_at'], "%Y-%m-%dT%H:%M:%S.%f")
        
        return Milestone_IE(
            id=record['id'],
            current_state=record['current_state'],
            added_at=_added_at,
            updated_at=_updated_at
        )

    async def load_many_milestones(self, recordIds: List = None) -> List[Optional[Milestone_IE]]:
        retVal=[]
        for recordId in recordIds:
            result = requests.get(self.TRUST_INTEGRATION_ENGINE_ENDPOINT+"/milestone/"+str(recordId), cookies={"SDSESSION":self.authToken})
            if result.status_code!=200:
                raise Exception(f"HTTP{result.status_code} received")
            record=json.loads(result.text)
            try:
                _added_at=datetime.strptime(record['added_at'], "%Y-%m-%dT%H:%M:%S")
                _updated_at=datetime.strptime(record['updated_at'], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                _added_at=datetime.strptime(record['added_at'], "%Y-%m-%dT%H:%M:%S.%f")
                _updated_at=datetime.strptime(record['updated_at'], "%Y-%m-%dT%H:%M:%S.%f")
            retVal.append(
                Milestone_IE(
                    id=record['id'],
                    current_state=record['current_state'],
                    added_at=_added_at,
                    updated_at=_updated_at
                )
            )
        return retVal