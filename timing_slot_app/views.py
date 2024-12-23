from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MonthlySchedule
from .serializers import MonthlyScheduleSerializer

class MonthlyScheduleAPIView(APIView):
    def patch(self, request):
        serializer = MonthlyScheduleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for item in serializer.validated_data:
                item['user'] = request.user
                schedule, created = MonthlySchedule.objects.update_or_create(
                    user=request.user, 
                    date=item['date'], 
                    defaults=item
                )
            return Response(
                {"success": True, "response": {"data": serializer.data}},
                status=status.HTTP_201_CREATED
            )
        else:
            first_error = serializer.errors[0] 
            first_field, errors = next(iter(first_error.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!" 
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST
            )

