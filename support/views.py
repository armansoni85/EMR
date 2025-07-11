from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.response import Response
import openai

openai.api_key = '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'

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show messages from conversations owned by user
        return Message.objects.filter(conversation__user=self.request.user)

    def perform_create(self, serializer):
        # Step 1: Save user message
        message = serializer.save()  # serializer already contains validated data

        # Step 2: Generate AI response only for user message
        if message.sender == "user":
            try:
                ai_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant for medical and pharmacy topics only. "
                                "Answer only health-related questions. Politely decline others."
                            )
                        },
                        {"role": "user", "content": message.content}
                    ]
                )
                ai_reply = ai_response.choices[0].message.content
            except Exception:
                ai_reply = "Sorry, I'm unable to respond right now."

            # Step 3: Save AI reply
            Message.objects.create(
                conversation=message.conversation,
                sender="ai",
                content=ai_reply
            )

		 
