from django.shortcuts import get_object_or_404, render
from accounts.models import CustomUser
from dashboard.serializers import ContactUsSerializers
from .models import ContactUs
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from accounts.serializers import RegisterUserSerializer
from payments.models import Transaction, Wallet
from payments.serializers import TransactionSerializer, WalletSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from accounts.permissions import (
    IsAdmin,
    is_support_level1,
    is_support_level2,
    isAccountant1,
    isAccountant2,
)
from rest_framework import status


class CustomPaginator(PageNumberPagination):
    page_size = 20
    page_query_param = "page"
    page_size_query_param = "page_size"


# Get all registered users
class AllUsersApiView(APIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPaginator

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ["phone_number", "first_name", "last_name", "email_address"]
    search_fields = ["phone_number", "first_name", "last_name", "email_address"]
    permission_classes = [
        IsAuthenticated & IsAdmin
        | IsAuthenticated & is_support_level1
        | IsAuthenticated & is_support_level2
    ]

    # get all users
    @swagger_auto_schema(
        operation_summary="This is responsible for listing all registered user for admin purposes",
        operation_description="""
        This endpoint allows administrators to retrieve a list of all registered users in the database.
        
        To access this endpoint, you must be an admin, a superuser, authenticated, and have a valid token.

        Filtering Options
        The following filtering options are supported:

        - phone_number: Filter all users by phone_number.
        - first_name: Filter all users by first_name.
        - last_name: Filter all users by last_name.
        - email_address: Filter all users by email_address.

        Usage
        To apply filtering, include the desired filter parameters as query parameters in the request URL. Examples:

        - Filter by phone_number: `GET /users?phone_number=
        =2347038320362`
        - Filter by first_name: `GET /users?first_name=Dennis`
        - Filter by last_name: `GET /users?last_name=Akagha`
        - Filter by email_address: `GET /users?email_address=denscholar20@gmail.com`

        You can also combine multiple filters by including multiple query parameters in the request.

        If no filters are provided, the API will return all users by default.

        ---
        `parameters for pagination:`
          - name: page
            in: query
            type: integer
            description: The page number for pagination (default: 1)
          - name: page_size
            in: query
            type: integer
            description: The number of items per page (default: 20)
        ---
        `responses:`
          200:
            description: List of registered users
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Information message
                data:
                  type: array
                  description: List of registered users
                  items:
                    $ref: '#/definitions/RegisterUserSerializer'
          404:
            description: No registered users found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
        """,
    )
    def get(self, request):
        registered_users = CustomUser.objects.all()
        if not registered_users:
            return Response(
                data={"message": "No registered users found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RegisterUserSerializer(registered_users, many=True)
        response = {"message": "All users", "data": serializer.data}
        return Response(data=response, status=status.HTTP_200_OK)


# class UserDetailsAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated & IsAdmin | IsAuthenticated & is_support_level1 | IsAuthenticated & is_support_level2]
#     # get all users
#     @swagger_auto_schema(
#         operation_summary="This is responsible for accessing a user details",
#         operation_description="This endpoint returns a user detail and accessible to only and authenticated user with an admin, a superuser, is_support_level1, is_support_level2 status"
#     )
#     def  get(self, request, pk):
#         user = get_object_or_404(CustomUser, pk=pk)
#         serializer = RegisterUserSerializer(user)
#         response = {
#             "message": serializer.data
#         }
#         return Response(response, status=status.HTTP_200_OK)


# Get all transactions
class AllTransactionsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPaginator
    permission_classes = [
        IsAuthenticated & IsAdmin
        | IsAuthenticated & isAccountant1
        | IsAuthenticated & isAccountant2
    ]
    pagination_class = CustomPaginator
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = ["payee_wallet_address", "transaction_ref", "timestamp"]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible getting all transactions",
        operation_description="""
        This endpoint allows administrators and accountants to retrieve all transactions.

        To access this endpoint, you must be an authenticated user who is either an admin, isAccountant1, or isAccountant2.

        Filtering Options
        The following filtering options are supported:

        - payee_wallet_address: Filter all transactions by payee_wallet_address.
        - transaction_ref: Filter all transactions by transaction_ref.
        - timestamp: Filter all transactions by timestamp.

        Usage
        To apply filtering, include the desired filter parameters as query parameters in the request URL. Examples:

        - Filter by payee_wallet_address: `GET /transactions?payee_wallet_address=
        =7038320362`
        - Filter by transaction_ref: `GET /transactions?transaction_ref=werd33-234er-eyhage-rtask`
        - Filter by timestamp: `GET /transactions?transaction_ref=`

        You can also combine multiple filters by including multiple query parameters in the request.

        If no filters are provided, the API will return all users by default.

        ---
        `parameters for pagination:`
          - name: page
            in: query
            type: integer
            description: The page number for pagination (default: 1)
          - name: page_size
            in: query
            type: integer
            description: The number of items per page (default: 20)
        ---
        responses:
          200:
            description: List of transactions
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Information message
                data:
                  type: array
                  description: List of transactions
                  items:
                    $ref: '#/definitions/TransactionSerializer'
        """,
    )
    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        response = {
            "message": "All transactions",
            "data": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


class TransactionDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated & IsAdmin
        | IsAuthenticated & isAccountant1
        | IsAuthenticated & isAccountant2
    ]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for getting a transaction by the transaction reference",
        operation_description="""
        This endpoint allows administrators and accountants to retrieve a transaction by its transaction reference.

        To access this endpoint, you must be an authenticated user who is either an admin, isAccountant1, or isAccountant2.

        ---
        parameters:
          - name: transaction_ref
            in: path
            type: string
            required: true
            description: Transaction reference

        responses:
          200:
            description: Transaction details
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Information message
                data:
                  $ref: '#/definitions/TransactionSerializer'
          404:
            description: Transaction not found
        """,
    )
    def get(self, request, transaction_ref):
        transanction = get_object_or_404(Transaction, pk=transaction_ref)
        serializer = TransactionSerializer(transanction)

        response = {
            "message": "transaction details",
            "data": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


class AllWalletAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPaginator
    permission_classes = [
        IsAuthenticated & IsAdmin
        | IsAuthenticated & is_support_level1
        | IsAuthenticated & is_support_level2
    ]
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = ["wallet_identifier"]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for getting all wallets",
        operation_description="""
        This endpoint allows administrators and support level users to retrieve all wallets.

        To access this endpoint, you must be an authenticated user who is either an admin, support_level1, or support_level2.

        Filtering Options
        The following filtering options are supported:

        - wallet_identifier: Filter all wallets by wallet_identifier.

        Usage
        To apply filtering, include the desired filter parameters as query parameters in the request URL. Examples:

        - Filter by wallet_identifier: `GET /wallets?wallet_identifier=7031501124


        If no filters are provided, the API will return all users by default.

        ---
        `parameters for pagination:`
          - name: page
            in: query
            type: integer
            description: The page number for pagination (default: 1)
          - name: page_size
            in: query
            type: integer
            description: The number of items per page (default: 20)

        ---
        responses:
          200:
            description: List of wallets
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/definitions/WalletSerializer'
        """,
    )
    def get(self, request):
        wallets = Wallet.objects.all()
        serializer = WalletSerializer(wallets, many=True)
        response = {"data": serializer.data}
        return Response(data=response, status=status.HTTP_200_OK)


class WalletDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated & IsAdmin
        | IsAuthenticated & is_support_level1
        | IsAuthenticated & is_support_level2
    ]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for getting a wallet associated with a wallet identifiier",
        operation_description="""
        This endpoint allows administrators and support level users to retrieve a wallet by its identifier (phone number).

        To access this endpoint, you must be an authenticated user who is either an admin, support_level1, or support_level2.

        ---
        parameters:
          - name: wallet_identifier
            in: path
            type: string
            required: true
            description: Wallet identifier (phone number)

        responses:
          200:
            description: Wallet details
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Information message
                data:
                  $ref: '#/definitions/WalletSerializer'
          404:
            description: Wallet not found
        """,
    )
    def get(self, request, wallet_identifier):
        wallet = get_object_or_404(Wallet, pk=wallet_identifier)
        serializer = WalletSerializer(wallet)

        response = {
            "message": "Wallet detail for a user",
            "data": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


# contact us
class ContactUsListView(APIView):
    # contact us message List view
    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for listing all contactus messages",
        operation_description="This endpoint is responsible for listing all contactus messages",
    )
    def get(self, request):
        messages = ContactUs.objects.all()
        serializer = ContactUsSerializers(messages, many=True)
        response = {"message": serializer.data}

        return Response(response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="This endpoint creates contactus message",
        operation_description="This endpoint creates contactus message",
        request_body=ContactUsSerializers,
    )
    def post(self, request):
        # create a message
        data = request.data
        serializer = ContactUsSerializers(data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": "Message created",
                "message": serializer.data,
            }
        return Response(response, status=status.HTTP_201_CREATED)


class ContactUsDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="This endpoint provides the details of a contactus message",
        operation_description="This endpoint provides the details of a contactus message",
    )
    def get(self, request, id):
        message = get_object_or_404(ContactUs, id=id)
        serializer = ContactUsSerializers(message)
        response = {"message details": serializer.data}
        return Response(response, status=status.HTTP_200_OK)
