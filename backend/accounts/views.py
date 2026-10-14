from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"id":request.user.id,"username":request.user.get_username(),
            "display_name":request.user.get_full_name() or request.user.get_username(),"roles":request.user.role_codes()})
