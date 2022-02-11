import asyncio
import secrets
import string
from faker import Faker
from sqlalchemy.exc import IntegrityError
from containers import SDContainer

from models.db import db, DATABASE_URL
from models import *
from random import randint, getrandbits
from datetime import date, datetime
from SdTypes import DecisionTypes, MilestoneState
from datacreators import CreatePatient, CreateUser, CreateDecisionPoint
from itsdangerous import TimestampSigner
from config import config
from base64 import b64encode
from api import app
import traceback
app.container=SDContainer()

# Generate random 8 character password from [a-zA-Z0-9]
def password_generator():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(12))

# a class that has the properties of a dictionary too
# this is to emulate how Starlette's request class
# operates, as context has to be passed to some functions
# to get the db connection and user objects
class RequestPlaceholder(dict):
    pass

_CONTEXT={
    "db": db,
    "request":RequestPlaceholder()
}


created_pathways=[]
# this generates a placeholder cookie for use when connecting
# to the TIE as it's the only way to do so in one script w/
# authentication enabled
signer=TimestampSigner(config['SESSION_SECRET_KEY'])
cookie=signer.sign(b64encode(str(getrandbits(64)).encode("utf-8")))
_CONTEXT['request'].cookies={
    "SDSESSION":cookie.decode("utf-8")
}

async def insert_user():
    global created_pathways

    await Milestone.delete.where(Milestone.id >= 0).gino.status()
    await DecisionPoint.delete.where(DecisionPoint.id >= 0).gino.status()
    await OnPathway.delete.where(OnPathway.id >= 0).gino.status()
    await Session.delete.gino.status()
    await User.delete.where(User.id >= 0).gino.status()
    await Patient.delete.where(Patient.id >= 0).gino.status()
    await MilestoneType.delete.where(MilestoneType.id >= 0).gino.status()
    await Pathway.delete.where(Pathway.id >= 0).gino.status()

    created_pathways=[
        await Pathway.create(id=1, name="Lung Cancer"),
        await Pathway.create(id=2, name="Bronchiectasis")
    ]

    users = await User.query.gino.all()
    user_num = str(len(users))
    username = "user" + user_num
    password = password_generator()
    first_name = "John " + user_num
    last_name = "Doe " + user_num
    department = "Respiratory"
    default_pathway_id = 1
    try:
        user = await CreateUser(username, password, first_name, last_name, department, default_pathway_id)
        print("User inserted")
        print("Username: " + user['username'])
        print("Password: " + password)

        # the return data from `CreateUser` is a dict so it can be
        # directly output via gql. To emulate the request class, 
        # we set this as a user object as it would be normally
        _CONTEXT['request']['user']=User(
            id=user["id"],
            username=user['username'],
            department=user['department'],
            first_name=user['first_name'],
            last_name=user['last_name']
        )
    except IntegrityError as err:
        print("Error: " + str(err))

async def insert_test_data():
    _Faker:Faker=Faker()

    general_milestone_types={
        "referral_letter": await MilestoneType.create(name="Referral letter", ref_name="Referral letter (record artifact)", is_checkbox_hidden=True),
        "pathology": await MilestoneType.create(name="Pathology", ref_name="Pathology report (record artifact)", is_checkbox_hidden=True),
        "prehad_referral": await MilestoneType.create(name="Prehad referral", ref_name="Prehabilitation (regime/therapy)", is_discharge=True),
        "dietician_referral": await MilestoneType.create(name="Dietician referral", ref_name="Patient referral to dietitian (procedure)", is_discharge=True),
        "smoking_cessation_referral": await MilestoneType.create(name="Smoking cessation referral", ref_name="Referral to smoking cessation service (procedure)"),
        "chest_xray": await MilestoneType.create(name="Chest X-ray", ref_name="Plain chest X-ray (procedure)"),
        "ct_chest": await MilestoneType.create(name="CT chest", ref_name="Computed tomography of chest (procedure)"),
    }

    selectable_milestone_types=[
        await MilestoneType.create(name="PET-CT", ref_name="Positron emission tomography with computed tomography (procedure)"),
        await MilestoneType.create(name="CT head - contrast", ref_name="Computed tomography of head with contrast (procedure)"),
        await MilestoneType.create(name="MRI head", ref_name="Magnetic resonance imaging of head (procedure)"),
        await MilestoneType.create(name="Lung function tests", ref_name="Measurement of respiratory function (procedure)"),
        await MilestoneType.create(name="ECHO", ref_name="Echocardiography (procedure)"),
        await MilestoneType.create(name="CT guided biopsy thorax", ref_name="Biopsy of thorax using computed tomography guidance (procedure)"),
        await MilestoneType.create(name="EBUS", ref_name="Transbronchial needle aspiration using endobronchial ultrasonography guidance (procedure)"),
        await MilestoneType.create(name="ECG", ref_name="Electrocardiogram analysis (qualifier value)"),
        await MilestoneType.create(name="Thoracoscopy", ref_name="Thoracoscopy (procedure)"),
        await MilestoneType.create(name="Bronchoscopy", ref_name="Bronchoscopy (procedure)"),
        await MilestoneType.create(name="Pleural tap", ref_name="Thoracentesis (procedure)"),
        await MilestoneType.create(name="CPET", ref_name=" Cardiopulmonary exercise test (procedure)"),
        await MilestoneType.create(name="Bloods", ref_name="Blood test (procedure)"),
    ]
    
    for i in range(0, 50):
        first_name=_Faker.first_name()
        last_name=_Faker.last_name()

        hospital_number="fMRN" + str(randint(10000,99999))
        if len(str(i))==1:
            hospital_number+= "0"
        hospital_number+=str(i)

        national_number="fNHS" + str(randint(10000000,99999999))
        if len(str(i))==1:
            national_number+= "0"
        national_number+=str(i)

        year = randint(1950, 1975)
        month = randint(1, 12)
        day = randint(1, 28)
        dob = date(year, month, day)
        
        _patientObject=None
        try:
            _patientObject = await CreatePatient(
                context=_CONTEXT,
                first_name=first_name,
                last_name=last_name,
                hospital_number=hospital_number,
                national_number=national_number,
                date_of_birth=dob,
                communication_method="LETTER",
                pathwayId=created_pathways[0].id,
                milestones=[
                    {
                        "milestoneTypeId": general_milestone_types["referral_letter"].id,
                        "currentState": MilestoneState.COMPLETED
                    },
                    {
                        "milestoneTypeId": general_milestone_types["chest_xray"].id,
                        "currentState": MilestoneState.COMPLETED
                    },
                    {
                        "milestoneTypeId": general_milestone_types["ct_chest"].id,
                        "currentState": MilestoneState.COMPLETED
                    }
                ]
            )
            print(f"Creating patient: {first_name} {last_name}")
        except Exception as e:
            traceback.print_exc()

        on_pathways={
            await OnPathway.query.where(
                OnPathway.patient_id==_patientObject['patient'].id
            ).where(
                OnPathway.pathway_id==created_pathways[0].id
            ).gino.one_or_none(),
            await OnPathway.create(
                patient_id = _patientObject['patient'].id,
                pathway_id = created_pathways[1].id
            )
        }

        on_pathway_counter=0
        for on_pathway in on_pathways:
            on_pathway_counter=on_pathway_counter+1
            if on_pathway_counter==1 or (on_pathway_counter!=1 and bool(getrandbits(1))):
                print(f"OnPathway is {(await Pathway.get(on_pathway.pathway_id)).name}")
                is_patient_new=bool(getrandbits(1))
                if is_patient_new:
                    """
                    is the patient new to the pathway? if they are, we don't
                    want to add any decision points as they will need to be triaged
                    """
                    print(f"Not creating any decision points")
                else:
                    await on_pathway.update(
                        under_care_of_id=_CONTEXT["request"]["user"].id
                    ).apply()

                    number_of_milestones=randint(1,2)
                    possible_milestone_types=[
                        selectable_milestone_types[randint(0, len(selectable_milestone_types)-1)],
                        selectable_milestone_types[randint(0, len(selectable_milestone_types)-1)]
                    ]

                    while (possible_milestone_types[0]==possible_milestone_types[1]):
                        possible_milestone_types[1]=selectable_milestone_types[randint(0, len(selectable_milestone_types)-1)]
                    milestone_requests=[]
                    for i in range(0, number_of_milestones):
                        milestone_requests.append(
                            {"milestoneTypeId": possible_milestone_types[i].id}
                        )
                    
                    await CreateDecisionPoint(
                        context=_CONTEXT,
                        on_pathway_id=on_pathway.id,
                        clinician_id=_CONTEXT["request"]["user"].id,
                        decision_type=DecisionTypes.TRIAGE,
                        clinic_history=_Faker.text(),
                        comorbidities=_Faker.text(),
                        milestone_requests=milestone_requests
                    )
                    print(f"Created TRIAGE decision point")
                    await on_pathway.update(
                        awaiting_decision_type=DecisionTypes.CLINIC
                    ).apply()

                    has_clinic=bool(getrandbits(1))
                    if has_clinic:
                        await CreateDecisionPoint(
                            context=_CONTEXT,
                            on_pathway_id=on_pathway.id,
                            clinician_id=_CONTEXT["request"]["user"].id,
                            decision_type=DecisionTypes.CLINIC,
                            clinic_history=_Faker.text(),
                            comorbidities=_Faker.text(),
                            milestone_requests=[
                                {"milestoneTypeId": selectable_milestone_types[randint(0, len(selectable_milestone_types)-1)].id}
                            ]
                        )
                        print(f"Created CLINIC decision point")
                        await on_pathway.update(
                            awaiting_decision_type=DecisionTypes.MDT
                        ).apply()

loop = asyncio.get_event_loop()
engine = loop.run_until_complete(db.set_bind(DATABASE_URL))
loop.run_until_complete(insert_user())
loop.run_until_complete(insert_test_data())
