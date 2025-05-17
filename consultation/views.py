# import from drf libraries
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from django.db.models import Q
from django.db import transaction

# import from base
from base.base_views import (
    CustomViewSetV2,
    CustomAPIView,
)
from base.utils import get_full_file_path, success_response, error_response

# import from the apps
from .serializers import (
    ConsultationRecordingSerializer,
    ConsultationSerializer,
    ConsultationDetailSerializer,
)
from .models import ConsultationRecording, Consultation
from .permissions import CanCreateUpdateConsultation
from .filters import ConsultationRecordingFilterset, ConsultationFilterset
from user.choices import RoleType

# importing the services
from services.chatgpt import ChatGPT


class ConsultationAPI(CustomViewSetV2):
    """
    This API is to view,create and update the Consultation
    """

    permission_classes = (CanCreateUpdateConsultation,)
    serializer_class = ConsultationSerializer
    model_class = Consultation
    queryset = Consultation.objects.select_related("appointment").all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ConsultationFilterset

    search_fields = (
        "appointment__doctor__fist_name",
        "appointment__doctor__last_name",
    )

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "GET" and self.kwargs.get("pk"):
            self.serializer_class = ConsultationDetailSerializer
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        user_hospital_id = user.hospital_id
        user_id = user.id
        user_role = user.role
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            pass
        elif user_role == RoleType.hospital_admin.value[0]:
            qs = qs.filter(
                (
                    Q(appointment__doctor__hospital_id=user_hospital_id)
                    | Q(appointment__patient__hospital_id=user_hospital_id)
                )
            )
        elif user_role == RoleType.doctor.value[0]:
            qs = qs.filter(appointment__doctor_id=user_id)
        else:
            qs = qs.filter(appointment__patient_id=user_id)
        # if request method is GET detail then pull all recording associated with that consultion
        if self.request.method == "GET" and self.kwargs.get("pk"):
            # qs=qs.annotate(recordings=ConsultationRecording.objects.filter(consultation=OuterRef('id')).only('recording_audio'))
            qs = qs.prefetch_related("consultation_recordings")
        return qs

    def get_serializer_context(self):
        context = super(ConsultationAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class ConsultationRecordingAPI(CustomViewSetV2):
    """
    This API is to view upload consultations recording
    """

    permission_classes = (CanCreateUpdateConsultation,)
    serializer_class = ConsultationRecordingSerializer
    model_class = ConsultationRecording
    queryset = ConsultationRecording.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ConsultationRecordingFilterset

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        user_hospital_id = user.hospital_id
        user_id = user.id
        user_role = user.role
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            return qs
        elif user_role == RoleType.hospital_admin.value[0]:
            return qs.filter(
                (
                    Q(consultation__appointment__doctor__hospital_id=user_hospital_id)
                    | Q(
                        consultation__appointment__patient__hospital_id=user_hospital_id
                    )
                )
            )
        elif user_role == RoleType.doctor.value[0]:
            return qs.filter(consultation__appointment__doctor_id=user_id)
        else:
            return qs.filter(consultation__appointment__patient_id=user_id)

    def get_serializer_context(self):
        context = super(ConsultationRecordingAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ConsultationRecordingAnalyze(CustomAPIView):
    # This API is to view upload consultations recording analysis
    @transaction.atomic
    def get(self, request, consultation_id: str, *args, **kwargs):
        if consultation_id:
            consultation_instance = (
                Consultation.objects.select_related("appointment")
                .filter(id=consultation_id, appointment__doctor_id=request.user.id)
                .prefetch_related("consultation_recordings")
                .first()
            )
            if consultation_instance:
                recordings = consultation_instance.consultation_recordings.all()
                if recordings.exists():
                    chatgpt = ChatGPT()
                    # Process all recordings and concatenate the AI consultation results
                    recording_texts = [
                        chatgpt.get_doctor_ai_consultation(
                            get_full_file_path(recording.recording_audio.name)
                        )
                        for recording in recordings
                    ]
                    # Combine results into a single string
                    consultation_instance.recording_ai_voice_note = "\n".join(
                        recording_texts
                    )
                    consultation_instance.save()
                    return success_response(
                        data=ConsultationSerializer(
                            instance=consultation_instance
                        ).data,
                        message="ok",
                    )
                return success_response(
                    message="No recordings found for this consultation."
                )
            return success_response(
                message=f"Consultation with this {consultation_id} not found."
            )
