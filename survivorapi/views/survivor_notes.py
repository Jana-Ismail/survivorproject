from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import SurvivorLog, Survivor, SurvivorNote

class SurvivorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurvivorNote
        fields = ['id', 'survivor_log_id', 'text']

class SurvivorNotes(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations for notes about survivors in a season log
    """

    queryset = SurvivorNote.objects.all()
    serializer_class = SurvivorNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Method for a user to create a note instance for a survivor in a season log"""
        try:
            note = SurvivorNote.objects.create(
                survivor_log_id = request.data["survivor_log_id"],
                text = request.data["text"]
            )

            serializer = SurvivorNoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)