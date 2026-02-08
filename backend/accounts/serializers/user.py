from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers

from accounts.models.department import Department
from accounts.models.enum import UserRole
from accounts.models.specialization import Specialization
from accounts.models.user import DoctorProfile, NurseProfile, PatientProfile, User
from accounts.serializers.department import DepartmentSerializer
from accounts.serializers.specialization import SpecializationReadSerializer
from clinical.models.allergy import Allergy
from clinical.serializers.allergy import AllergySerializer

identity_card_number_validator = RegexValidator(
    regex=r"^\d{6}-\d{2}-\d{4}$",
    message="Identity card number must be in the format XXXXXX-XX-XXXX",
)


class DoctorProfileSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    specialization = SpecializationReadSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ["department", "specialization", "license_number"]


class NurseProfileSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = NurseProfile
        fields = ["department"]


class PatientProfileSerializer(serializers.ModelSerializer):
    allergies = AllergySerializer(many=True, read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = [
            "identity_card_number",
            "blood_group",
            "allergies",
            "date_of_birth",
            "age",
        ]

    def get_age(self, obj):
        return obj.age


class UserReadSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "gender",
            "profile",
        ]

    def get_profile(self, obj):
        if obj.role == "doctor" and hasattr(obj, "doctor_profile"):
            return DoctorProfileSerializer(obj.doctor_profile).data
        elif obj.role == "nurse" and hasattr(obj, "nurse_profile"):
            return NurseProfileSerializer(obj.nurse_profile).data
        elif obj.role == "patient" and hasattr(obj, "patient_profile"):
            return PatientProfileSerializer(obj.patient_profile).data
        else:
            return {}


class DoctorProfileWriteSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(
        source="department", queryset=Department.objects.all()
    )
    specialization_id = serializers.PrimaryKeyRelatedField(
        source="specialization", queryset=Specialization.objects.all()
    )

    class Meta:
        model = DoctorProfile
        fields = ["department_id", "specialization_id", "license_number"]

    def validate_license_number(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("License number cannot be empty.")
        if len(value) > 50:
            raise serializers.ValidationError(
                "License number max length is 50 characters."
            )
        return value


class NurseProfileWriteSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(
        source="department", queryset=Department.objects.all()
    )

    class Meta:
        model = NurseProfile
        fields = ["department_id"]


class PatientProfileWriteSerializer(serializers.ModelSerializer):
    allergies_ids = serializers.PrimaryKeyRelatedField(
        source="allergies", queryset=Allergy.objects.all(), many=True, required=False
    )

    class Meta:
        model = PatientProfile
        fields = [
            "identity_card_number",
            "date_of_birth",
            "blood_group",
            "allergies_ids",
        ]

    def validate_identity_card_number(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Identity card number is required.")
        if len(value) > 14:
            raise serializers.ValidationError(
                "Identity card number max length is 14 characters."
            )
        # Validate regex
        try:
            identity_card_number_validator(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message) from e
        return value

    def validate_date_of_birth(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value


class UserNestedWriteSerializer(serializers.ModelSerializer):
    # Nested role-specific serializers
    doctor_profile = DoctorProfileWriteSerializer(required=False)
    nurse_profile = NurseProfileWriteSerializer(required=False)
    patient_profile = PatientProfileWriteSerializer(required=False)

    # TODO: Add contraint - unique username

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "role",
            "gender",
            "doctor_profile",
            "nurse_profile",
            "patient_profile",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        return value

    def validate_email(self, value):
        if value:
            return value.strip().lower()
        return value

    def validate_password(self, value):
        # TODO: Uncomment
        # validate_password(value)
        return value

    def validate(self, attrs):
        role = attrs.get("role")
        # Ensure the correct profile is provided
        if role == "doctor" and "doctor_profile" not in attrs:
            raise serializers.ValidationError(
                {"doctor_profile": "This field is required for doctor role."}
            )
        elif role == "nurse" and "nurse_profile" not in attrs:
            raise serializers.ValidationError(
                {"nurse_profile": "This field is required for nurse role."}
            )
        elif role == "patient" and "patient_profile" not in attrs:
            raise serializers.ValidationError(
                {"patient_profile": "This field is required for patient role."}
            )
        return attrs

    def create(self, validated_data):
        # Pop nested profile data
        doctor_data = validated_data.pop("doctor_profile", None)
        nurse_data = validated_data.pop("nurse_profile", None)
        patient_data = validated_data.pop("patient_profile", None)

        # Handle password hashing
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create profile based on role
        if user.role == "doctor" and doctor_data:
            DoctorProfile.objects.create(user=user, **doctor_data)
        elif user.role == "nurse" and nurse_data:
            NurseProfile.objects.create(user=user, **nurse_data)
        elif user.role == "patient" and patient_data:
            allergies = patient_data.pop("allergies", [])
            patient_profile = PatientProfile.objects.create(user=user, **patient_data)
            if allergies:
                patient_profile.allergies.set(allergies)
        elif user.role == UserRole.ADMIN:
            user.is_staff = True
            user.save()

        return user
