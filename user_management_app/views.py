import string
import threading
from .models import *
from .serializers import *
from random import choice
from itertools import chain
from django.db.models import Q
from rest_framework import status
from django.core.mail import send_mail
from rest_framework.views import APIView
from user_management_app.constants import sendSMS
from django.contrib.auth import authenticate
from rest_framework.response import Response
from user_management_app.threads import send_email_code
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY_TEST

# Create your views here.



class SignUpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        mobile_number = request.data.get('mobile_number')
        full_name = request.data.get('full_name')
        confirm_password = request.data.get('confirm_password')
        user_type = request.data.get('user_type')

        if not  email or not password or not mobile_number or not confirm_password or not user_type:
            return Response({"message": "Missing fields required"}, status=status.HTTP_400_BAD_REQUEST)

        
        email_user = User.objects.filter(email=email).first()
        if email_user:
            return Response({"message": "This email already exist in the system!"}, status=status.HTTP_400_BAD_REQUEST)

        mobile_user = User.objects.filter(mobile_number=mobile_number).first()
        if mobile_user:
            return Response({"message": "This Mobile Number already exist in the system!"}, status=status.HTTP_400_BAD_REQUEST)


        if password != confirm_password:
            return Response({"message": "password did not match"}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = make_password(request.data['password'])
        username = email.split('@')[0]
        user = User.objects.filter(username=username).first()
        if user:
            chars = string.digits
            dynamic = ''.join(choice(chars) for _ in range(4))
            username = f'{username}{dynamic}'

        user = User.objects.create(email=email, password=hashed_password, username=username, user_type=user_type, mobile_number=mobile_number, full_name=full_name)
        
        wallet = Wallet.objects.create(user=user)
        
        chars = string.digits
        first_digit = choice(chars[1:])
        other_digits = ''.join(choice(chars) for _ in range(4))
        random_code = first_digit + other_digits
        email_code, created = UserVerification.objects.get_or_create(user=user)
        email_code.code = random_code
        email_code.save()

        try:
            sendSMS(mobile_number, random_code)

        except Exception as e:
            pass
            print('******************', e)

        # try:
        #     thrd = threading.Thread(target=send_email_code, args=[random_code, user])
        #     thrd.start()
        # except Exception as e:
        #     print('******************', e)
        return Response({"success": True, 'response': {"message":"User created successfully"}}, status=status.HTTP_201_CREATED)




class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserGETSerializer(user)
        return Response({"success": True, 'response': {"data": serializer.data}}, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = UserGETSerializer(user, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            print('************', serializer)
            return Response({"success": True, "response": {"message": "Profile updated successfully!", "data": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"success": False, "response": {"message": "Invalid data", "errors": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email_or_mobile = request.data.get('email_or_mobile')
        password = request.data.get('password')

        if not email_or_mobile or not password:
            return Response({"success": False, 'response': {"message": "Email or mobile number and password are required!"}}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(Q(email=email_or_mobile) | Q(mobile_number=email_or_mobile)).first()
        if not user:
            return Response({"success": False, 'response': {"message": "User does not exist!"}}, status=status.HTTP_404_NOT_FOUND)

        login_user = authenticate(username=user, password=password)
        if login_user:
            token, created = Token.objects.get_or_create(user=login_user)
            serializer = UserSerializer(login_user)
            return Response({"success": True, 'response': {"data": serializer.data, 'token': str(token.key)}}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, 'response': {"message": "Invalid credentials!"}}, status=status.HTTP_400_BAD_REQUEST)

class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        user = User.objects.filter(email=email).first()
        otp_code = UserVerification.objects.filter(user=user, code=code, is_varified=False).first()

        if not otp_code:
            return Response({"success": False, 'response': {"message":"your code did not match please try again with a valid code"}}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        otp_code.is_varified = True
        otp_code.save()

        return Response({"success": True, 'response': {"message":'Email verified successfully'}}, status=status.HTTP_201_CREATED)


class MobileNumberVerifyAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        code = request.data.get('code')

        user = User.objects.filter(mobile_number=mobile_number).first()
        otp_code = UserVerification.objects.filter(code=code, is_varified=False).first()

        if not otp_code:
            return Response({'success':False, 'response':{'message': 'your code did not match please try again with a valid code'}}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.mobile_number_varified = True
        user.save()
        otp_code.is_varified = True
        otp_code.save()
        return Response({'success':True, 'response':{'message':'phone number verified successfully '}}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        if token:
            return Response({"success": True, "response": {"message": "Successfully logged out"}}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "response": {"message": "Error occurred while logging out"}}, status=status.HTTP_400_BAD_REQUEST)



class DriverProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        institude_name = request.data.get('institude_name')
        trainer_name = request.data.get('trainer_name')
        license_no = request.data.get('license_no')
        address = request.data.get('address')
        total_lesson = request.data.get('total_lesson')
        price = request.data.get('price')

        if not institude_name or not trainer_name or not license_no or not address or not total_lesson or not price:
            return Response({'success':False, 'response':{'message': 'Missing fields required!'}})


        serializer = DriverProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "response": {"message": "Driver profile created successfully!", "data": serializer.data}}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "response": {"message": "Invalid data", "errors": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        try:
            driver_profile = DriverProfile.objects.get(user=request.user)
            serializer = DriverProfileSerializer(driver_profile)
            return Response({"success": True, 'response': {"data": serializer.data}}, status=status.HTTP_200_OK)
        except DriverProfile.DoesNotExist:
            return Response({"success": False, 'response': {"message": "Driver profile does not exist"}}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            driver_profile = DriverProfile.objects.get(user=request.user)
        except DriverProfile.DoesNotExist:
            return Response({"success": False, "response": {"message": "Driver profile does not exist"}}, status=status.HTTP_404_NOT_FOUND)

        serializer = DriverProfileSerializer(driver_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "response": {"message": "Profile updated successfully!", "data": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"success": False, "response": {"message": "Invalid data", "errors": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if user:
            chars = string.digits
            first_digit = choice(chars[1:])
            other_digits = ''.join(choice(chars) for _ in range(4))
            random_code = first_digit + other_digits

            email_code, created = UserVerification.objects.get_or_create(user=user)
            email_code.code = random_code
            email_code.is_varified = False
            email_code.save()

            try:
                thrd = threading.Thread(target=send_email_code, args=[random_code, user])
                thrd.start()
            except Exception as e:
                print('******************', e)

            return Response({"success": True, 'response': {"message": "OTP code resent successfully"}}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not email or not otp or not new_password or not confirm_password:
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) <= 8:
            return Response({'success':False, 'response':{'message': 'password should be greater than 8 characters'}})

        if new_password != confirm_password:
            return Response({"message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            email_code = UserVerification.objects.get(user=user, code=otp, is_varified=False)
        except (User.DoesNotExist, UserVerification.DoesNotExist):
            return Response({"message": "Invalid OTP or user does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user.password = make_password(new_password)
        user.save()

        email_code.is_varified = True
        email_code.save()

        return Response({"success": True, 'response': {"message": "Password reset successfully"}}, status=status.HTTP_200_OK)



class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        rating = request.data.get('rating')

        if not rating:
            return Response({'success': False, 'response': {'message': 'Rating is required!'}}, status=status.HTTP_400_BAD_REQUEST)

        user_review = Review.objects.filter(user=user).exists()
        if user_review:
            return Response({'success': False, 'response': {'message': 'You have already submitted a review!'}}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"success": True, "response": {"message": "Review submitted successfully!", "data": serializer.data}}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "response": {"message": "Invalid data", "errors": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)

class SocialLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email').lower().strip() if 'email' in request.data else None
        # user_d_id = request.data.get('device_id', None)
        full_name = request.data.get('full_name', None)
        social_platform = request.data.get('social_platform')

        if not email or not social_platform:
            return Response({"success": False, 'response': {'message': 'Email and social platform are required!'}},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if not user:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            username = email.split('@')[0]

        
            if User.objects.filter(username=username).exists():
                username = f"{username}_{random.randint(1000, 9999)}"

            user = User(
                email=email,
                username=username,
                password=make_password(password),
                is_active=True,
                full_name=full_name,
            )
            user.save()

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)

        access_token = token.key

        return Response({"success": True, 'response': {'message': 'Login successful', 'access_token': access_token}}, status=status.HTTP_200_OK)



class CreateDepositIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            amount = int(float(request.data.get('amount')) * 100)
            currency = 'cad'

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=['card'],
            )
            return Response({'client_secret': payment_intent.client_secret}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmDepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            payment_intent_id = request.data.get('payment_intent_idamount')

            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if payment_intent.status == 'succeeded':
                wallet = Wallet.objects.get_or_create(user=user)
                amount = payment_intent.amount / 100

                wallet.balance += amount
                wallet.save()

                transaction = TransactionHistroy.objects.create(
                    wallet=wallet, 
                    amount=amount, 
                    transaction_type='deposit'
                )
                transaction.save()

                return Response({"success": True, "message": "Deposit successful!", "balance": wallet.balance}, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Payment not confirmed!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

