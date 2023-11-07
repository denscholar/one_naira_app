from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.core.exceptions import PermissionDenied
from rest_framework import generics
from django.http import HttpResponse
from django.conf import settings
from rest_framework.request import Request
from decimal import Decimal


from .serializers import (
    Depositserializer,
    PaymentSerializer,
    QRCodeSerializer,
    TransactionSerializer,
    WalletSerializer,
    TransactionChangePinSerializer,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from accounts.models import CustomUser
from rest_framework import filters
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import (
    IsAuthenticated,
    BasePermission,
    IsAdminUser,
    AllowAny,
)
from rest_framework.generics import ListAPIView
from .models import (
    Payment,
    Transaction,
    # TransactionCharges,
    # TransactionFee,
    # Wallet,
)
from rest_framework.viewsets import ModelViewSet
from datetime import datetime, timedelta
from accounts.utils import send_otp
from accounts.serializers import TransactionPinSerializer
from io import BytesIO

# from .models import QrBarCode
# from .serializers import QRCodeSerializer
from rest_framework.authentication import TokenAuthentication
import qrcode
import random


class CustomPaginator(PageNumberPagination):
    page_size = 1
    page_query_param = "page"
    page_size_query_param = "page_size"


# create a transaction pin
# class TransactionPinCreateView(APIView):
#     serializer_class = TransactionPinSerializer
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_summary="This endpoint is responsible for creating a transaction pin",
#         operation_description="This endpoint creates a transaction pin for a user",
#         request_body=TransactionPinSerializer,
#     )
#     def post(self, request):
#         data = request.data
#         serializer = TransactionPinSerializer(instance=request.user, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             response = {"message": "transaction pin created"}
#             return Response(data=response, status=status.HTTP_201_CREATED)
#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST


class QRCreateView(APIView):
    serialzer_class = QRCodeSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for QRcode for the authenticated user",
        operation_description="This endpoint creates QR-code for the authenticated user",
        request_body=QRCodeSerializer,
    )
    def post(self, request):
        serializer = self.serialzer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the user information from the request headers
        user = request.user

        # Create the QR code object
        qr_code = serializer.save(user=user)

        # Generate QR code data
        qr_data = f"{qr_code.wallet_id}"

        # generate the qr code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        img = qr.make_image(fill_color="black", back_color="white")
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert image to response
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        response = HttpResponse(image_data, content_type="image/png")
        # response['Content-Disposition'] = f'attachment; filename="{qr_code.pk}.png"'

        return response


# trasanctions list view
class TransactionmodelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = ["payee_wallet_address", "amount", "timestamp"]
    pagination_class = CustomPaginator

    @swagger_auto_schema(
        operation_summary="This endpoint lists all transactions for the current user",
        operation_description="""
        This endpoint retrieves all transactions for a logged in user.
        
        ### Filtering Options
        
        The following filtering options are supported:
        
        - `payee_wallet_address`: Filter transactions by payee wallet address.
        - `amount`: Filter transactions by amount.
        - `timestamp`: Filter transactions by timestamp.
        
        ### Usage
        
        To apply filtering, include the desired filter parameters as query parameters in the request URL. Examples:
        
        - Filter by payee_wallet_address: `GET /transactions?payee_wallet_address=7038320362`
        - Filter by amount: `GET /transactions?amount=150.00`
        - Filter by timestamp: `GET /transactions?timestamp=2023-06-28T10:00:00`
        
        You can also combine multiple filters by including multiple query parameters in the request.
        
        If no filters are provided, the API will return all transactions by default.
    """,
    )
    def get(self, request):
        user = request.user
        transactions = Transaction.objects.get(user=user)
        serializer = TransactionSerializer(transactions, many=True)
        response = {
            "message": "All Transactions",
            "data": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)

    # @swagger_auto_schema(
    #     operation_summary="This endpoint creates a transaction for a logged-in user",
    #     operation_description="""
    #     This endpoint allows the authenticated user to create a transaction.

    #     The request should include the necessary details for the transaction in the request body,
    #     following the structure defined in the `TransactionSerializer`.

    #     If the request is valid and the transaction is successfully created,
    #     the API will return a success message along with the created transaction in the response data.
    #     """,
    #     request_body=TransactionSerializer,
    # )
    # def post(self, request):
    #     serializer = TransactionSerializer(
    #         data=request.data, context={"request": request}
    #     )
    # if serializer.is_valid():
    #     transaction = serializer.save()
    #     response = {
    #         "message": "Transaction successful",
    #         # "data": TransactionSerializer(transaction).data,
    #     }
    #     return Response(data=response, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Transaction Detail
class TransactionDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for retrieving the details of a transaction for a logged in user",
        operation_description="""
        This endpoint allows you to retrieve the details of a transaction using its unique transaction reference.

        To retrieve the transaction details, make a GET request to this endpoint with the transaction reference
        included as a query parameter.

        The API will return the details of the transaction, including the transaction reference, description,
        payee wallet address, amount, transaction type, status, and timestamp.

        ---
        responses:
          200:
            description: Transaction details retrieved successfully
          404:
            description: Transaction not found
        """,
    )
    def get(self, request, transaction_ref):
        user = request.user
        transaction = get_object_or_404(Transaction, pk=transaction_ref, user=user)
        serializer = TransactionSerializer(transaction)
        response = {
            "message": "transactions details",
            "data": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


# Payment views
class PaymentModelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # filter_backends = [
    #     DjangoFilterBackend,
    # ]
    # filterset_fields = ["payee_wallet_address", "amount", "timestamp"]
    # pagination_class = CustomPaginator

    # def get(self, request):
    #     user = request.user
    #     data = Payment.objects.get(user=user)
    #     serializers = PaymentSerializer(data=data, many=True)
    #     response = {
    #         "message": serializers.data
    #     }
    #     return Response(response, status=status.HTTP_200_OK)
    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for payment",
        operation_description="""
        This endpoint allows you to make payment.

        To make payment, make a POST request to this endpoint with the necessary information included in the request body.

        The request body should contain the following fields:

        `- amount (required): The amount to be paid.`
        `- payee_wallet_address (required): The wallet address of the payee.`
        `- description (required): The description of the payment transaction.`
        ---
        request_body:
          required: true
          serializer: PaymentSerializer
        responses:
          201:
            description: Payment successful
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Success message confirming the payment
          400:
            description: Invalid request or data
        """,
        request_body=PaymentSerializer,
    )
    def post(self, request):
        serializer = TransactionSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )
        if serializer.is_valid():
            transaction = serializer.save()
            response = {
                "message": "Payment successful",
                # "data": TransactionSerializer(transaction).data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepositFundAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for depositing funds into a logged in user's wallet",
        operation_description="""
        This endpoint allows you to deposit funds into the wallet of a logged-in user.

        To deposit funds, make a POST request to this endpoint with the necessary information included in the request body.

        The request body should contain the following fields:

        `- amount (required): The amount to be deposited.`

        ---
        request_body:
          required: true
          serializer: DepositSerializer
        responses:
          201:
            description: Funds deposited successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Success message confirming the deposit
          400:
            description: Invalid request or data
        """,
        request_body=Depositserializer,
    )
    def post(self, request):
        data = request.data
        serializer = Depositserializer(data=data, context={'request': request})

        if serializer.is_valid():
            deposit = serializer.save(
                wallet=request.user.wallet,
                status="Completed",
                transaction_type="Deposit",
            )
            response = {
                "message": "You have successfully deposited ₦{0} into your wallet".format(
                    data["amount"]
                )
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
