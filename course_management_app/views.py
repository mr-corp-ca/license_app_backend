from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
import json
# Create your views here.

class CourseApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        request_data = request.data
        services_list = request_data.get('services')
        license_category_list = request_data.get('license_category')
        lesson_numbers = request_data.get('lesson_numbers')
        lessons = request_data.get('lessons')

        if type(services_list) == str:
            services_list = json.loads(services_list) 

        if type(license_category_list) == str:
            license_category_list = json.loads(license_category_list) 

        if type(lessons) == str:
            lessons = json.loads(lessons)

        try:
            request.data._mutable = True
        except:
            pass

        lesson_count = len(lessons)
        if lesson_numbers != lesson_count:
            return Response(
                {'success': False, 'response': {'message': 'The total number of lessons in the lessons list should match the value provided in the lesson_numbers field.'}},
                status=status.HTTP_400_BAD_REQUEST)

        request.data['user'] = user.id
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            if license_category_list:
                for category in license_category_list:
                    course.license_category.add(category)
            if services_list:
                for service in services_list:
                    course.services.add(service)
            if lessons:
                for lesson in lessons:
                    Lesson.objects.create(course=course, title=lesson['title'], image=lesson['image'])
            serializer = GETCourseSerializer(course)
            return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            first_field, errors = next(iter(serializer.errors.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!"
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST)
        
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
