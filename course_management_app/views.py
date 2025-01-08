from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework import status
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from user_management_app.threads import *
from user_management_app.models import User
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from course_management_app.pagination import StandardResultSetPagination
from timing_slot_app.models import *
from rest_framework import filters
import threading
import json
from copy import deepcopy

# Create your views here.
class CourseApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        existing_course = Course.objects.filter(user=user).first()
        if existing_course:
            return Response(
                {
                    "success": False,
                    "response": {
                        "message": "You can only create one course. Please edit or delete the existing course."
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        request_data = request.data
        description = request.data.get('description', '').strip()
        price = request.data.get('price', 0.0)
        refund_policy = request.data.get('refund_policy', '').strip()
        lesson_numbers = int(request.data.get('lesson_numbers', 0))
        lessons = request_data.get('lessons')

        if len(lessons) != lesson_numbers:
            return Response(
                {
                    "success": False,
                    "response": {
                        "message": "The total number of lessons should match the value provided in lesson_numbers."
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        course_data = {
            "user": user.id,
            "description": description,
            "price": price,
            "refund_policy": refund_policy,
            "lesson_numbers": lesson_numbers,
        }
        serializer = SingleCourseSerializer(data=course_data)
        if serializer.is_valid():
            course = serializer.save()

            course.lesson.set(lessons)

            course_data = GETSingleCourseSerializer(course)
            return Response(
                {
                    "success": True,
                    "response": {"data": course_data.data}
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, id):
        user = request.user
        course = Course.objects.filter(id=id, user=user).first()
        if not course:
            return Response(
                {"success": False, "response": {"message": "Course not found!"}},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SingleCourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            course = serializer.save()
            return Response(
                {"success": True, "response": {"data": GETSingleCourseSerializer(course).data}},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        user = request.user

        try:
            school_profile = SchoolProfile.objects.get(user=user)
        except SchoolProfile.DoesNotExist:
            return Response(
                {"success": False, "response": {"message": "School Profile not found!"}},
                status=status.HTTP_404_NOT_FOUND
            )

        courses = Course.objects.filter(user=user).order_by('-created_at')

        serializer = SchoolGETSingleCourseSerializer(courses, many=True)

        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)


    def delete(self, request, id):
        user = request.user
        course = Course.objects.filter(id=id, user=user).first()
        if not course:
            return Response(
                {"success": False, "response": {"message": "Course not found!"}},
                status=status.HTTP_404_NOT_FOUND
            )
        course.delete()
        return Response(
            {"success": True, "response": {"message": "Course deleted successfully!"}},
            status=status.HTTP_200_OK
        )

class LessonApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)


class ServicesApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        objs = Service.objects.all()
        serializer = ServiceSerializer(objs, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)

class LicenseCategoryApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        objs = LicenseCategory.objects.all()
        serializer = LicenseCategorySerializer(objs, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)
    

class PackageApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        services_list = request.data.get('services')
        try:
            if type(services_list) == str:
                services_list = json.loads(services_list) 
        except:
            pass

        try:
            request.data._mutable = True
        except:
            pass

        request.data['user'] = user.id
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            pakage = serializer.save()
            if services_list:
                for service in services_list:
                    pakage.services.add(service)
            serializer = GETPackageSerializer(pakage)
            return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            first_field, errors = next(iter(serializer.errors.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!"
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user = request.user
        packages = Package.objects.filter(user=user).order_by('-created_at')
        serializer = GETPackageSerializer(packages, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        user = request.user
        package = Package.objects.filter(id=id).first()
        if not package:
            return Response({"success": False, "response": {"message": 'Package not found!'}}, status=status.HTTP_404_NOT_FOUND)
        package.delete()
        return Response({"success": True, "response": {"message": 'Package delete successfully!'}}, status=status.HTTP_200_OK)

class DiscountOfferApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            request.data._mutable = True
        except:
            pass

        request.data['user'] = user.id
        serializer = DiscountOfferSerializer(data=request.data)
        if serializer.is_valid():
            pakage = serializer.save()
            serializer = GETDiscountOfferSerializer(pakage)
            return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            first_field, errors = next(iter(serializer.errors.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!"
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user = request.user
        discounts = DiscountOffer.objects.filter(user=user).order_by('-created_at')
        serializer = GETDiscountOfferSerializer(discounts, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        user = request.user
        discount = DiscountOffer.objects.filter(id=id).first()
        if not discount:
            return Response({"success": False, "response": {"message": 'Discount not found!'}}, status=status.HTTP_404_NOT_FOUND)
        discount.delete()
        return Response({"success": True, "response": {"message": 'Discount delete successfully!'}}, status=status.HTTP_200_OK)

    def patch(self, request, id):
        user = request.user
        discount = DiscountOffer.objects.filter(id=id).first()
        if not discount:
            return Response({"success": False, "response": {"message": 'Discount offer object not found!'}}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DiscountOfferSerializer(discount, data=request.data, partial=True)
        if serializer.is_valid():
            discount = serializer.save()
            serializer = GETDiscountOfferSerializer(discount)
            return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            first_field, errors = next(iter(serializer.errors.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!"
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST)

class CertificateCreateAPIView(APIView):
    def post(self, request):
        user = request.user
        try:
            request.data._mutable = True
        except:
            pass
        
        request.data['created_by'] = user.id

        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'data': serializer.data}}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'response': {'errors': serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        image = request.data.get('image')
        email = request.data.get('email')

        certificate = Certificate.objects.get(id=id)


        if not image or not email:
            return Response({'success': False, 'response': {'message': 'Image and Email is required!'}}, 
                            status=status.HTTP_404_NOT_FOUND)

        serializer = CertificateSerializer(certificate, data=request.data, partial=True)
        if serializer.is_valid():
            certificate_image = serializer.save()

            try:
                t = threading.Thread(target=send_email_certificate,
                            args=[certificate_image.image.url, email],
                            )
                t.start()
            except Exception as e:
                pass
            return Response({'success': True, 'response': {'data': serializer.data}}, status=status.HTTP_200_OK)
        return Response({'success': False, 'response': {'errors': serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)
        

class AddVehicleApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            # Ensure the user is authenticated
            user = request.user

            vehicles = Vehicle.objects.filter(user=user)

            for vehicle in vehicles:

                if vehicle.booking_status == 'booked':
                    vehicle.booking_status = 'booked'
                else:
                    vehicle.booking_status = 'free'

            serializer = VehicleSerializer(vehicles, many=True)
            return Response({"status": True, "response": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": False, "response": {"message": "An error occurred.", "details": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self,request):
        try:
            
            user = request.user.id
            try:
                request.data._mutable = True

            except:
                pass
            
            request.data['user'] = user
            serializer = VehicleSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({'status': True,'response':{'data':serializer.data}}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
            {'status': False,'response':{'message': f"An error occurred.': {str(e)}"}}, 
            status=status.HTTP_400_BAD_REQUEST)

class LearnerListAPIView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_status = self.request.query_params.get('course_status', None)

        user = self.request.user
        school_setting, created = SchoolSetting.objects.get_or_create(user=user)
        learners = school_setting.learner.all()
        if course_status == 'completed':
            learners = learners.filter(courese_status='completed')
        elif course_status == 'on_going':
            learners = learners.filter(courese_status='in_progress')
        return learners

    serializer_class = LearnerSelectedPackageSerializer
    pagination_class = StandardResultSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['full_name']
    filterset_fields = []



class LessonRatingsForSchoolView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            course = Course.objects.filter(id=id).first()

            if not course:
                return Response(
                    {"status": False, "response": {"message": "No course found with this ID."}},
                    status=status.HTTP_404_NOT_FOUND,
                )

            course_ratings = SchoolRating.objects.filter(course=course)

            serializer = LessonRatingSerializer(course_ratings, many=True)

            return Response(
                {"status": True, "response": {"data": serializer.data}},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": False, "response": {"message": f"An error occurred: {str(e)}"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

class SchoolPackageDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        package = Package.objects.filter(id=id).first()

        if not package:
            return Response({"status": False, "response": {"message": "No Package found with this ID."}},
            status=status.HTTP_404_NOT_FOUND)

        serializer = SchoolPackageDetailSerializer(package)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class CoursesListAPIView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    queryset = Course.objects.filter(user__user_type='school')
    serializer_class = CoursesListSerializer
    pagination_class = StandardResultSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title']
    filterset_fields = ['title', 'price', 'lesson_numbers']


class PolicyApiview(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        try:
            general_policy = GeneralPolicy.objects.first()
            
            if general_policy:
                serializer = GeneralPolicySerializer(general_policy)
                return Response({'success':True, "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "response": {"message": "No Package found with this ID."}},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"status": False, "response": {"message": f"An error occurred: {str(e)}"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

class InstructorLessonsAPIView(APIView):
    def get(self, request):
        try:
            user = request.user
            print("----------------->",user)
            status_filter = request.query_params.get('status', 'today')
            today = date.today()

            # lessons = LearnerSelectedPackage.objects.filter(user__user_type='learner').first()
            # course_status = learner_selected_package.courese_status if learner_selected_package else None
            # print("------------------>",course_status)
            lessons = LearnerBookingSchedule.objects.filter(vehicle__user=user)
            if status_filter == 'today':
                lessons = lessons.filter(date=today)

            elif status_filter == 'upcoming':
                lessons = lessons.filter(date__gt=today)

            elif status_filter == 'completed':

                    lessons = lessons.filter(
                        date__lt=today, is_completed=True
                    )

            serializer = LearnerBookingScheduleSerializer(lessons, many=True)

            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        
        except Exception as e:
            return Response(
                {"status": False, "response": {"message": f"An error occurred: {str(e)}"}},
                status=status.HTTP_400_BAD_REQUEST,
            )