# importing drf library
from base.filters import FilterBaseSet, filters

# importing the models from the consultation app
from .models import Consultation, ConsultationRecording


class ConsultationFilterset(FilterBaseSet):
    next_follow_up_date_gte = filters.DateFilter(
        method="filter_next_follow_up_date_gte"
    )

    class Meta:
        model = Consultation
        fields = [
            "appointment",
            "recording_ai_voice_note_status",
            "is_started",
            "is_finished",
        ]

    def filter_next_follow_up_date_gte(self, queryset, name, value):
        return queryset.filter(follow_up_date__gte=value)


class ConsultationRecordingFilterset(FilterBaseSet):
    class Meta:
        model = ConsultationRecording
        fields = [
            "consultation",
        ]
