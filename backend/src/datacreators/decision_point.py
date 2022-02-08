from models import DecisionPoint, Milestone, OnPathway
from gettext import gettext as _
from SdTypes import DecisionTypes
from typing import List, Dict
from containers import SDContainer
from trustadapter.trustadapter import TestResultRequest_IE, TrustAdapter
from dependency_injector.wiring import Provide, inject
from datetime import date, datetime

class ReferencedItemDoesNotExistError(Exception):
    """
        This occurs when a referenced item does not 
        exist and cannot be found when it should
    """
@inject
async def CreateDecisionPoint(
    context:dict=None, 
    on_pathway_id:int=None,
    clinician_id:int=None,
    decision_type:DecisionTypes=None,
    clinic_history:str=None,
    comorbidities:str=None,
    added_at:datetime=None,
    milestone_resolutions:List[int]=None,
    milestone_requests:List[Dict[str, int]]=None,
    trust_adapter: TrustAdapter = Provide[SDContainer.trust_adapter_service]
):
    if context is None:
        raise ReferencedItemDoesNotExistError("Context is not provided")
    on_pathway_id = int(on_pathway_id)
    clinician_id = int(clinician_id)

    decision_point_details={
        "on_pathway_id": on_pathway_id,
        "clinician_id": clinician_id,
        "decision_type": decision_type,
        "clinic_history": clinic_history,
        "comorbidities": comorbidities,
    }
    if added_at:
        decision_point_details['added_at']=added_at

    _decisionPoint:DecisionPoint=await DecisionPoint.create(
        **decision_point_details
    )

    if milestone_requests is not None:
        for requestInput in milestone_requests:
            testResultRequest=TestResultRequest_IE()
            testResultRequest.added_at=datetime.now()
            testResultRequest.updated_at=datetime.now()
            testResultRequest.type_id=requestInput['milestoneTypeId']
            
            # TODO: batch these
            if "currentState" in requestInput:
                testResultRequest.current_state=requestInput['currentState']
            if "addedAt" in requestInput:
                testResultRequest.added_at=requestInput['addedAt']
            if "updatedAt" in requestInput:
                testResultRequest.updated_at=requestInput['updatedAt']

            testResult=await trust_adapter.create_test_result(testResultRequest, auth_token=context['request'].cookies['SDSESSION'])

            await Milestone(
                on_pathway_id=int(_decisionPoint.on_pathway_id),
                decision_point_id=int(_decisionPoint.id),
                milestone_type_id=int(testResultRequest.type_id),
                test_result_reference_id = str(testResult.id),
                added_at = testResultRequest.added_at,
                updated_at = testResultRequest.updated_at
            ).create()

    if milestone_resolutions is not None:
        for milestoneId in milestone_resolutions:
            await Milestone.update.values(fwd_decision_point_id=int(_decisionPoint.id)).where(Milestone.id==int(milestoneId)).gino.status()

    await OnPathway.update\
        .where(OnPathway.id == on_pathway_id)\
        .where(OnPathway.under_care_of_id == None)\
        .values(under_care_of_id=context['request']['user'].id)\
        .gino.scalar()

    return {
        "decisionPoint":_decisionPoint
    }