from rest_framework import serializers
from employee.models import ProfessionalInformation,DutyDetail,Qualification,Certification
from base.utils import generate_unique_code

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Qualification
        fields=("id","name","description","organization","document")
        read_only_fields=("id",)

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Certification
        fields=("id","name","issued_by","valid_until","document")
        read_only_fields=("id",)

class ProfessionalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProfessionalInformation
        fields=("id","user","speciality","sub_speciality","medical_license_number","years_of_experience","profession_id")
        read_only_fields=("id","profession_id")
    
    def validate(self, attrs):
        # validate user can update qualification and certification of particular doctor only not other doctor
        return super().validate(attrs)

    def create(self, validated_data):
        if self.context['request'].method == "POST":
            
            existing_profession_ids=ProfessionalInformation.objects.all().values_list('profession_id',flat=True)
            while True:
                generated_profession_id=generate_unique_code(length=10)
                if generated_profession_id not in existing_profession_ids:
                    break

            validated_data['profession_id']=generated_profession_id
        return super().create(validated_data)

class DutyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=DutyDetail
        fields=("id","user","department_name","duty_start_time","duty_end_time","is_on_call","room_number")
        read_only_fields=("id",)

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Qualification
        fields=("id","user","name","description","organization","document")
        read_only_fields=("id",)

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Certification
        fields=("id","user","name","issued_by","valid_until","document")
        read_only_fields=("id",)