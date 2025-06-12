from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/applications/', views.admin_applications, name='admin_applications'),
    path('dashboard/admin/applications/<int:pk>/', views.admin_application_detail, name='admin_application_detail'),
    path('dashboard/admin/tenants/', views.admin_tenants, name='admin_tenants'),
    path('dashboard/admin/payments/', views.admin_payments, name='admin_payments'),
    path('dashboard/admin/leave-requests/', views.admin_leave_requests, name='admin_leave_requests'),
    path('api/unit-availability/', views.unit_availability_api, name='unit_availability_api'),
    path('dashboard/admin/payments/<int:pk>/', views.admin_payment_detail, name='admin_payment_detail'),
    path('dashboard/admin/announcements/', views.admin_announcements, name='admin_announcements'),
    path('dashboard/admin/messages/', views.admin_messages, name='admin_messages'),
    path('dashboard/admin/messages/<int:pk>/', views.admin_message_detail, name='admin_message_detail'),

    # Admin Unit Management
    path('dashboard/admin/units/', views.admin_units_list, name='admin_units_list'),
    path('dashboard/admin/units/add/', views.admin_unit_create, name='admin_unit_create'),
    path('dashboard/admin/units/<int:pk>/edit/', views.admin_unit_update, name='admin_unit_update'),
    path('dashboard/admin/units/<int:pk>/delete/', views.admin_unit_delete, name='admin_unit_delete'),
    
    # Client URLs
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('client/units/', views.client_units, name='client_units'),
    path('client/units/<int:pk>/', views.client_unit_detail, name='client_unit_detail'),
    path('client/application-status/', views.client_application_status, name='client_application_status'),
    
    # Tenant URLs
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/payment-history/', views.tenant_payment_history, name='tenant_payment_history'),
    path('tenant/submit-payment/', views.tenant_submit_payment, name='tenant_submit_payment'),
    path('tenant/messages/', views.tenant_messages, name='tenant_messages'),
    path('tenant/messages/<int:pk>/', views.tenant_message_detail, name='tenant_message_detail'),
    path('tenant/announcements/', views.tenant_announcements, name='tenant_announcements'),
    path('tenant/announcements/<int:pk>/', views.tenant_announcement_detail, name='tenant_announcement_detail'),
    path('tenant/leave-request/', views.tenant_leave_request, name='tenant_leave_request'),
    
    # Profile
    path('profile/', views.profile, name='profile'),

    # Conversation-based messaging
    path('messages/', views.conversation_list, name='conversation_list'),
    path('messages/new/', views.conversation_create, name='conversation_create'),
    path('messages/conversation/<int:conversation_id>/', views.conversation_thread, name='conversation_thread'),
]