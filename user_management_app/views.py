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
from .threads import *
from user_management_app.constants import sendSMS
from django.contrib.auth import authenticate
from rest_framework.response import Response
from user_management_app.threads import send_email_code
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.



class UserApiView(APIView):
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


    def get(self, request):
        user = request.user
        serializer = DefaultUserSerializer(user)
        return Response({"success": True, 'response': {"data": serializer.data}}, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True) 
        if serializer.is_valid():
            user = serializer.save()
            serializer = DefaultUserSerializer(user)
            return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"success": False, "response": {"message": "Invalid data", "errors": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        recover_account = request.data.get('recover_account', None)
        user_type = request.data.get('user_type', None)

        if not user_type:
            return Response({'success': False, 'response': {'message': "user_type field is missing"}},
                        status=status.HTTP_400_BAD_REQUEST)
                        
        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            if user.user_type == 'school' and not user.user_status == 'accepted':
                return Response({'success': False, 'response': {'message': "Your school's registration is pending approval or has not been accepted."}}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            user = User.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            hashed_password = make_password(phone_number)
            user = User.objects.create(
                username=phone_number,
                password=hashed_password,
                phone_number=phone_number,
                user_type=user_type,
            )
        
        user.user_type = user_type
        user.save()

        # if recover_account:
        #     user.is_deleted = False
        #     user.save()

        # if user.is_deleted:
        #     return Response({"success": False, 'response': {'message': 'Your account is deleted! are you want to recover your account?'}},
        #             status=status.HTTP_403_FORBIDDEN)
        
        # if user.role == 'Business':
        #     store = StoreInfo.objects.filter(user=user).first()
        #     if store:
        #         if store.status == 'pending':
        #             return Response({'success': False, 'response': {'message': "Please wait while your business account is under review for approval. We appreciate your patience!"}},
        #                         status=status.HTTP_400_BAD_REQUEST)                
        #         elif store.status == 'rejected':
        #                 return Response({'success': False, 'response': {'message': "Your business account has been rejected due to specific reasons. For further assistance, please reach out to our Help and Support team."}},
        #                             status=status.HTTP_400_BAD_REQUEST)                

        wallet, created = Wallet.objects.get_or_create(user=user)

        # for handling 0 should not come on Front
        first_digit = random.choice(string.digits[1:]) 

        remaining_digits = ''.join(random.choices(string.digits, k=3))

        random_digits_for_code = first_digit + remaining_digits

        user_verification, created = UserVerification.objects.get_or_create(
            user=user,
            defaults={'code': random_digits_for_code}
        )

        user_verification.is_verified = False
        user_verification.save()

        if not created:
            user_verification.code = random_digits_for_code
            user_verification.save()

        try:
            sendSMS(phone_number, random_digits_for_code)
        except Exception as e:
            print('*******************', e)
            pass

        return Response({'success': True,
                        'response': {'message': 'OTP sent to your mobile number, use OTP for login.'}},
                        status=status.HTTP_200_OK)
    
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        user = User.objects.filter(phone_number=phone_number).first()
        otp_code = UserVerification.objects.filter(user=user, code=code, is_varified=False).first()

        if not otp_code:
            return Response({"success": False, 'response': {"message":"your code did not match please try again with a valid code"}}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        otp_code.is_varified = True
        otp_code.save()

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        
        access_token = token.key
        
        serializer = DefaultUserSerializer(user)
        return Response({'success': True, 'response': {'data': serializer.data, 'access_token': access_token}},
                        status=status.HTTP_200_OK)

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


class LogoutApiView(APIView):

    def post(self, request):
        # fcm_device = FCMDevice.objects.filter(user__username=request.user.username)
        # if fcm_device.exists():
        #     fcm_device.delete()
        request.user.auth_token.delete()

        return Response({'success': True, 'response': {'message': 'User Logged Out Successfully'}},
                        status=status.HTTP_200_OK)


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


class SocialLoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email').lower().strip() if 'email' in request.data else None
        user_d_id = request.data.get('device_id', None)
        full_name = request.data.get('full_name', None)
        social_platform = request.data.get('social_platform', None)
        user_type = request.data.get('user_type', None)

        if not email or not user_d_id or not social_platform or not user_type:
            return Response({"success": False, 'response': {'message': 'email, device id, user_type and social_platform required!'}},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()        
        username = email.split('@')[0]
        if not user:
            hashed_password = make_password(username)
            user = User.objects.create(
                username=username,
                password=hashed_password,
                email=email,
                full_name=full_name,
                social_platform=social_platform,
                user_type=user_type,
            )

        user.is_active = True
        user.save()

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        
        access_token = token.key
        
        wallet, created = Wallet.objects.get_or_create(user=user)
        serializer = DefaultUserSerializer(user)
        
        # try:
        #     fcm_device = FCMDevice.objects.get(device_id=user.id)
        #     fcm_device.delete()
        # except:
        #     pass

        # if user_d_id:
        #     fcm_device, created = FCMDevice.objects.get_or_create(
        #         registration_id=user_d_id,
        #         defaults={'user': user, 'device_id': user_d_id}
        #     )

        return Response({'success': True, 'response': {'data': serializer.data, 'access_token': access_token}},
                        status=status.HTTP_200_OK)
    
class UserNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_filter = request.data.get('user_filter')
        noti_type = request.data.get('noti_type')
        all_users = User.objects.all()

        if user_filter:
            all_users = all_users.filter(id=user_filter)

        for user in all_users:
            try:
                request.data._mutable = True
            except:
                pass

            request.data['user'] = user.id

            if noti_type == 'push-notification':
                serializer = UserNotificationSerializer(data=request.data)
                if serializer.is_valid():
                    notification = serializer.save()
                    title = request.data.get('title', 'New Notification')
                    message = request.data.get('description', 'You have a new notification.')
                    send_push_notification(user, title, message)
                else:
                    return Response({"success": False, 'response': {"message": serializer.errors}},
                                     status=status.HTTP_400_BAD_REQUEST)

            elif noti_type == 'sms':
                message = request.data.get('description', 'You have a new notification.')
                send_sms(user.phone_number, message) 

            elif noti_type == 'email':
                subject = request.data.get('title', 'New Notification')
                message = request.data.get('description', 'You have a new notification.')
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            else:
                return Response(
                    {"success": False, 'response': {"message": "Invalid notification type."}},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response({"success": True, 'response': {"message": "Notifications sent successfully."}}, status=status.HTTP_200_OK)
