import json
import pytest
from hamcrest import assert_that, equal_to, has_item, not_
from models.User import User


# Feature: User account operations
# Scenario: a new user needs to be added into the system
@pytest.mark.asyncio
async def test_create_user_correct(context):
    """
    When: we create their user account
    """
    NEW_CLINICIAN = {
        "firstName": "JOHN",
        "lastName": "SMITH",
        "username": "JOHN.SMITH123",
        "password": "VERYSECUREPASSWORD",
        "department": "ONCOLOGY",
        "defaultPathwayId": context.PATHWAY.id,
        "isActive": True
    }

    create_user_account = await context.client.post(
        url="rest/createuser/",
        json=NEW_CLINICIAN
    )
    assert_that(create_user_account.status_code, equal_to(200))

    query_result = json.loads(create_user_account.text)

    assert_that(query_result, not_(has_item('error')))
    assert_that(query_result, has_item('user'))

    user_result = query_result['user']

    assert_that(user_result['username'], equal_to(NEW_CLINICIAN['username']))
    assert_that(
        user_result['firstName'], equal_to(NEW_CLINICIAN['firstName'])
    )
    assert_that(
        user_result['lastName'], equal_to(NEW_CLINICIAN['lastName'])
    )
    assert_that(
        user_result['department'], equal_to(NEW_CLINICIAN['department'])
    )
    assert_that(
        user_result['defaultPathwayId'], equal_to(context.PATHWAY.id)
    )


# Feature: User account operations
# Scenario: a new user needs to be added into the system but
# username already exists
@pytest.mark.asyncio
async def test_create_user_username_preexists(context):
    """
    When: we create their user account
    """

    await User.create(
        first_name="Michael",
        last_name="Myers",
        department="Scary Dept",
        username="michael",
        password="thisshouldbeahash",
        default_pathway_id=context.PATHWAY.id,
        is_active=True
    )

    NEW_CLINICIAN = {
        "firstName": "Michael",
        "lastName": "Johnson",
        "username": "michael",
        "password": "VERYSECUREPASSWORD",
        "department": "ONCOLOGY",
        "defaultPathwayId": context.PATHWAY.id,
        "isActive": True
    }

    create_user_account = await context.client.post(
        url="rest/createuser/",
        json=NEW_CLINICIAN
    )
    assert_that(create_user_account.status_code, equal_to(200))

    query_result = json.loads(create_user_account.text)

    assert_that(query_result, has_item('error'))
    assert_that(query_result, not_(has_item('user')))
