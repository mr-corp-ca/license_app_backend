from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework import status
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
from rest_framework import filters
import threading
import json
from copy import deepcopy

# Create your views here.
class CourseApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        request_data = deepcopy(request.data)

        # Extract fields with safe defaults
        title = request_data.get('title', '').strip()
        description = request_data.get('description', '').strip()
        price = request_data.get('price', '').strip()
        refund_policy = request_data.get('refund_policy', '').strip()
        lesson_numbers = int(request_data.get('lesson_numbers', 0))

        # Extract lists (ensure they are lists)
        services_list = request_data.getlist('services', [])
        license_category_list = request_data.getlist('license_category', [])

        # Parse lessons dynamically
        lessons = []
        for i in range(lesson_numbers):
            lesson_title = request_data.get(f'lessons[{i}][title]', '').strip()
            lesson_image = request_data.get(f'lessons[{i}][image]', None)
            if lesson_title and lesson_image:
                lessons.append({'title': lesson_title, 'image': lesson_image})

        # Validate lesson count
        if lesson_numbers != len(lessons):
            return Response(
                {
                    'success': False,
                    'response': {
                        'message': 'The total number of lessons should match the value provided in the lesson_numbers field.'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare data for serializer
        course_data = {
            'user': user.id,
            'title': title,
            'description': description,
            'price': price,
            'refund_policy': refund_policy,
            'lesson_numbers': lesson_numbers,
        }

        # Serialize and save
        serializer = CourseSerializer(data=course_data)
        if serializer.is_valid():
            course = serializer.save()

            # Add related many-to-many fields
            course.license_category.set(map(int, license_category_list))
            course.services.set(map(int, services_list))

            # Create lessons
            for lesson in lessons:
                Lesson.objects.create(course=course, title=lesson['title'], image=lesson['image'])

            # Serialize the saved course
            course_serializer = GETCourseSerializer(course)
            return Response(
                {"success": True, "response": {"data": course_serializer.data}},
                status=status.HTTP_201_CREATED
            )
        else:
            # Extract and format the first error
            first_field, errors = next(iter(serializer.errors.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!"
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, id):
        user = request.user
        services_list = request.POST.get('services')
        license_category_list = request.POST.get('license_category')
        course = Course.objects.filter(id=id).first()
        if not course:
            return Response({"success": False, "response": {"message": 'Course not found!'}}, status=status.HTTP_404_NOT_FOUND)

        if type(services_list) == str:
            services_list = json.loads(services_list) 

        if type(license_category_list) == str:
            license_category_list = json.loads(license_category_list)

        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            course = serializer.save()
            if license_category_list:
                course.license_category.clear()
                for category in license_category_list:
                    course.license_category.add(category)
            if services_list:
                course.services.clear()
                for service in services_list:
                    course.services.add(service)
            serializer = GETCourseSerializer(course)
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
        courses = Course.objects.filter(user=user).order_by('-created_at')
        serializer = GETCourseSerializer(courses, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)

    
    def delete(self, request, id):
        user = request.user
        course = Course.objects.filter(id=id).first()
        if not course:
            return Response({"success": False, "response": {"message": 'Course not found!'}}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response({"success": True, "response": {"message": 'Course delete successfully!'}}, status=status.HTTP_200_OK)


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
    permission_classes = [AllowAny]
    queryset = User.objects.filter(user_type='learner')
    serializer_class = LearnerSelectedPackageSerializer
    pagination_class = StandardResultSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['full_name', 'learner_user__courese_status']
    filterset_fields = []

class SchoolPackageDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        package = Package.objects.filter(id=id).first()

        if not package:
            return Response({"success": False, "message": "Package not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SchoolPackageDetailSerializer(package)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
