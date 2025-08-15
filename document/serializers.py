from document.models import MedicalDocument
from rest_framework import serializers
from rest_framework.validators import ValidationError
from user.choices import RoleType
from strings import MEDICAL_DOCUMENT_CROSS_HOSPITAL_ERROR,MEDICAL_DOCUMENT_BOTH_PATIENT_ERROR


class MedicalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDocument
        fields = (
            "id",
            "file_name",
            "file",
            "belonging_department",
            "note",
            "uploaded_to",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("id", "created_at", "modified_at")

    def validate(self, attrs):
        data = super().validate(attrs)
        file=data.get("file")
        file_name=data.get("file_name",file.name if file else None)
        uploaded_to=data.get("uploaded_to")
        if self.context["request"].method == "PUT":
            file=file if file else self.instance.file
            file_name=file_name if file_name else self.instance.file_name
            uploaded_to=uploaded_to if uploaded_to else self.instance.uploaded_to
       
        current_user = self.context["request"].user
        if current_user.role==RoleType.patient.value[0] and uploaded_to.role==RoleType.patient.value[0]:
            raise ValidationError(MEDICAL_DOCUMENT_BOTH_PATIENT_ERROR)
        if (
            current_user.hospital_id != uploaded_to.hospital_id
            and current_user.role != RoleType.hospital_admin.value[0]
            and not current_user.is_superuser
        ):
            raise ValidationError(
                MEDICAL_DOCUMENT_CROSS_HOSPITAL_ERROR
            )

        data["file"]=file
        data["file_name"]=file_name
        data["uploaded_to_id"]=uploaded_to.id
        data["uploaded_by_id"] = self.context["request"].user.id
        return data
    
    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
