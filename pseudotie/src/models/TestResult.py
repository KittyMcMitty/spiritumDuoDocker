from .db import db
from sqlalchemy import func, Enum
from RecordTypes import TestResultState

class TestResult(db.Model):
    __tablename__ = "tbl_test_result"

    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(), nullable=True)
    type_reference_name = db.Column(db.String(), nullable=False)
    current_state = db.Column(
        Enum(TestResultState, native_enum=False), default=TestResultState.INIT.value,
        server_default=TestResultState.INIT.value, nullable=False, native_enum=False
    )
    added_at = db.Column(db.DateTime(), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(), server_default=func.now(), nullable=False)