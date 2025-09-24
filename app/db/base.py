from app.db.base_class import Base  # ✅ import base class for all models
from app.db.models.credential import Credential
from app.db.models.patient import Patient # ✅ import all models here so Alembic sees them
from app.db.models.hospital import Hospital
from app.db.models.doctor import Doctor
from app.db.models.ambulance import Ambulance
from app.db.models.medical_records import MedicalRecord
from app.db.models.socket_log import SocketLog
from app.db.models.patient_assignment import PatientAssignment
from app.db.models.user_settings import UserSettings
