from django.contrib import admin

from accounts.models.department import Department
from accounts.models.specialization import Specialization
from accounts.models.user import DoctorProfile, NurseProfile, PatientProfile, User

# Register your models here.
admin.site.register(Department)
admin.site.register(Specialization)
admin.site.register(User)
admin.site.register(DoctorProfile)
admin.site.register(NurseProfile)
admin.site.register(PatientProfile)
