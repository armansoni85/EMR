from django.db import transaction
from rest_framework import serializers
from support.models import AIChatSupport
from services.chatgpt import ChatGPT


class AIChatSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatSupport
        fields = ["id", "user", "question", "reply", "created_at", "modified_at"]
        read_only_fields = ("user", "reply", "created_at", "modified_at")

    @transaction.atomic
    def create(self, validated_data):
        # transaction is atomic if API fail,then donot save data into database
        chatgpt = ChatGPT()
        validated_data["user"] = self.context["request"].user
        validated_data["reply"] = (chatgpt.ai_chat_support(validated_data["question"]))
        return super().create(validated_data)
