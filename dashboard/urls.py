from django.urls import path
from . import views

urlpatterns = [
   path("transactions/", views.AllTransactionsAPIView.as_view(), name="transactions"),
   path("users/", views.AllUsersApiView.as_view(), name="users"),
   # path("user_details/<int:pk>/", views.UserDetailsAPIView.as_view(), name="user_details"),
   path("transaction_details/<str:transaction_ref>/", views.TransactionDetailAPIView.as_view(),name="transaction_details"),
   path("wallets/", views.AllWalletAPIView.as_view(),name="wallets"),
   path("wallet_details/<str:wallet_identifier>/", views.WalletDetailAPIView.as_view(),name="wallet_details"),

   # contact us
   path("contact_us/", views.ContactUsListView.as_view(),name="contact-us"),
   path("contact_details/<str:id>/", views.ContactUsDetailView.as_view(),name="contact-us-details"),
]
