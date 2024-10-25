from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import SurvivorLog, SurvivorNote

class SurvivorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurvivorNote
        fields = ['id', 'survivor_log_id', 'text']

class SurvivorNotes(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations for survivor (log) notes in a season log
    """

    # queryset = SurvivorNote.objects.all()
    serializer_class = SurvivorNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filters notes based on user permissions
        - Admin users can see all notes
        - Regular users can only view their own notes
        """
        user = self.request.auth.user
        if user.is_staff:
            return SurvivorNote.objects.all()

        return SurvivorNote.objects.filter(
            survivor_log__user=user
        )

    def create(self, request, *args, **kwargs):
        """Method for a user to create a note instance for a survivor in a season log"""
        try:
            survivor_log = SurvivorLog.objects.get(
                pk=request.data["survivor_log_id"],
                user=request.user
            )
            note = SurvivorNote.objects.create(
                survivor_log_id = survivor_log.id,
                text = request.data["text"]
            )

            serializer = SurvivorNoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)