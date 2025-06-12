from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from io import BytesIO
from .models import *
from .forms import *
from django.core.paginator import Paginator



def home(request):
    units = Unit.objects.filter(status=Unit.AVAILABLE)[:3]
    return render(request, 'home.html', {'units': units})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.role == User.ADMIN:
        return redirect('admin_dashboard')
    elif request.user.role == User.TENANT:
        return redirect('tenant_dashboard')
    else:
        return redirect('client_dashboard')



def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role == User.ADMIN):
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_units_list(request):
    units = Unit.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/units_list.html', {'units': units})

@login_required
@admin_required
def admin_unit_create(request):
    if request.method == 'POST':
        form = UnitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit created successfully!')
            return redirect('admin_units_list')
    else:
        form = UnitForm()
    return render(request, 'admin_panel/unit_form.html', {'form': form, 'action': 'Create'})

@login_required
@admin_required
def admin_unit_update(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        form = UnitForm(request.POST, request.FILES, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit updated successfully!')
            return redirect('admin_units_list')
    else:
        form = UnitForm(instance=unit)
    return render(request, 'admin_panel/unit_form.html', {'form': form, 'action': 'Update', 'unit': unit})

@login_required
@admin_required
def admin_unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        unit.delete()
        messages.success(request, 'Unit deleted successfully!')
        return redirect('admin_units_list')
    return render(request, 'admin_panel/unit_confirm_delete.html', {'unit': unit})

@login_required
@admin_required
def admin_dashboard(request):
    pending_applications = Application.objects.filter(status=Application.PENDING).count()
    active_tenants = Lease.objects.filter(is_active=True).count()
    pending_payments = Payment.objects.filter(status=Payment.PENDING).count()
    context = {
        'pending_applications': pending_applications,
        'active_tenants': active_tenants,
        'pending_payments': pending_payments,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@admin_required
def admin_applications(request):
    applications = Application.objects.all().order_by('-applied_date')
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_panel/applications.html', {'page_obj': page_obj})

@login_required
@admin_required
def admin_application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        application.status = int(status)
        application.notes = notes
        application.processed_date = timezone.now()
        application.save()
        if status == str(Application.APPROVED):
            # Create tenant user
            application.client.role = User.TENANT
            application.client.save()
            # Create lease
            lease = Lease.objects.create(
                tenant=application.client,
                unit=application.unit,
                start_date=timezone.now().date(),
                monthly_rent=application.unit.monthly_price,
                is_active=True
            )
            unit = application.unit
            unit.status = Unit.OCCUPIED
            unit.save()
            messages.success(request, 'Application approved and tenant created!')
        else:
            messages.success(request, 'Application status updated!')
        return redirect('admin_applications')
    return render(request, 'admin_panel/application_detail.html', {'application': application})

@login_required
@admin_required
def admin_tenants(request):
    tenants = User.objects.filter(role=User.TENANT)
    leases = Lease.objects.filter(is_active=True)
    return render(request, 'admin_panel/tenants.html', {'tenants': tenants, 'leases': leases})

@login_required
@admin_required
def admin_payments(request):
    payments = Payment.objects.all().order_by('-created_at')
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_panel/payments.html', {'page_obj': page_obj})

@login_required
@admin_required
def admin_payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        payment.status = int(status)
        payment.notes = notes
        payment.save()
        messages.success(request, 'Payment status updated!')
        return redirect('admin_payments')
    return render(request, 'admin_panel/payment_detail.html', {'payment': payment})

@login_required
@admin_required
def admin_announcements(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            form.save_m2m() 
            messages.success(request, 'Announcement created successfully!')
            return redirect('admin_announcements')
    else:
        form = AnnouncementForm()
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/announcements.html', {
        'form': form,
        'announcements': announcements
    })

@login_required
@admin_required
def admin_messages(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    return render(request, 'messages/conversation_list.html', {'conversations': conversations})

@login_required
@admin_required
def admin_message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = message.sender 
            reply.save()
            messages.success(request, 'Reply sent successfully!')
            return redirect('admin_message_detail', pk=pk)
    else:
        form = MessageForm(initial={'recipient': message.sender, 'subject': f"Re: {message.subject}"})
    return render(request, 'admin_panel/message_detail.html', {'message': message, 'form': form})


from django.http import JsonResponse
import calendar

# Client Views
@login_required
def client_dashboard(request):
    if request.user.role != User.CLIENT:
        return redirect('dashboard')
    
    has_pending_application = Application.objects.filter(client=request.user, status=Application.PENDING).exists()
    
    context = {
        'has_pending_application': has_pending_application
    }
    return render(request, 'client/dashboard.html', context)

def client_units(request):
    units = Unit.objects.all().annotate(
        is_occupied=models.Exists(
            Lease.objects.filter(
                unit=models.OuterRef('pk'),
                is_active=True
            )
        )
    )
    return render(request, 'client/units.html', {'units': units})

@login_required
def client_unit_detail(request, pk):
    if request.user.role != User.CLIENT:
        return redirect('dashboard')
    
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.client = request.user
            application.unit = unit
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('client_dashboard')
    else:
        # Pre-fill with user data
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}",
            'address': request.user.address,
            'contact_number': request.user.phone_number,
            'email': request.user.email,
            'facebook_account': request.user.facebook_account,
            'occupation': request.user.occupation,
        }
        form = ApplicationForm(initial=initial_data)
    
    return render(request, 'client/unit_detail.html', {'unit': unit, 'form': form})

@login_required
def client_application_status(request):
    if request.user.role != User.CLIENT:
        return redirect('dashboard')
    
    applications = Application.objects.filter(client=request.user).order_by('-applied_date')
    return render(request, 'client/application_status.html', {'applications': applications})

def unit_availability_api(request):
    """
    Returns a JSON response with unit availability for the current month.
    For each day, returns the number of available units.
    """
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    _, last_day = calendar.monthrange(year, month)
    days = [today.replace(year=year, month=month, day=day) for day in range(1, last_day+1)]

    leased_units = Lease.objects.filter(is_active=True)
    leased_unit_ids = set(leased_units.values_list('unit_id', flat=True))
    all_units = Unit.objects.filter(status=Unit.AVAILABLE)
    total_units = all_units.count()

    availability = []
    for day in days:
        leased_on_day = Lease.objects.filter(
            is_active=True,
            start_date__lte=day,
            end_date__gte=day if Lease._meta.get_field('end_date').null else day
        ).values_list('unit_id', flat=True)
        available_count = all_units.exclude(id__in=leased_on_day).count()
        availability.append({
            'date': day.strftime('%Y-%m-%d'),
            'available_units': available_count,
            'total_units': total_units
        })
    return JsonResponse({'availability': availability})

# Tenant Views
@login_required
def tenant_dashboard(request):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    lease = Lease.objects.filter(tenant=request.user, is_active=True).first()
    
    today = timezone.now().date()
    next_payment_due = today.replace(day=1) + timedelta(days=32)
    next_payment_due = next_payment_due.replace(day=1)
    
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    new_announcements = Announcement.objects.filter(
        Q(is_global=True) | Q(recipients=request.user),
        created_at__gte=timezone.now() - timedelta(days=7)
    )

    context = {
        'lease': lease,
        'next_payment_due': next_payment_due,
        'unread_messages': unread_messages,
        'new_announcements': new_announcements.count(),
    }
    return render(request, 'tenant/dashboard.html', context)

@login_required
def tenant_payment_history(request):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    lease = Lease.objects.filter(tenant=request.user, is_active=True).first()
    if not lease:
        messages.warning(request, 'You do not have an active lease.')
        return redirect('tenant_dashboard')
    
    payments = Payment.objects.filter(lease=lease).order_by('-payment_date')
    
    # Export functionality
    export_format = request.GET.get('export')
    if export_format:
        if export_format == 'pdf':
            return generate_payment_pdf(lease, payments)
        elif export_format == 'excel':
            return generate_payment_excel(lease, payments)
    
    return render(request, 'tenant/payment_history.html', {'payments': payments, 'lease': lease})

def generate_payment_pdf(lease, payments):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_history_{lease.id}.pdf"'
    
    p = canvas.Canvas(response)
    
    # PDF content
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Payment History for {lease.tenant.get_full_name()}")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Unit: {lease.unit.name}")
    p.drawString(100, 760, f"Monthly Rent: ${lease.monthly_rent}")
    
    y = 730
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Date")
    p.drawString(200, y, "Amount")
    p.drawString(300, y, "Status")
    p.drawString(400, y, "Notes")
    
    p.setFont("Helvetica", 10)
    y -= 20
    
    for payment in payments:
        p.drawString(100, y, payment.payment_date.strftime('%Y-%m-%d'))
        p.drawString(200, y, f"${payment.amount}")
        p.drawString(300, y, payment.get_status_display())
        p.drawString(400, y, payment.notes[:20] + "..." if payment.notes else "")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    
    p.save()
    return response

def generate_payment_excel(lease, payments):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="payment_history_{lease.id}.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Payment History"
    
    # Header
    ws.append(["Date", "Amount", "Status", "Notes"])
    
    # Data
    for payment in payments:
        ws.append([
            payment.payment_date.strftime('%Y-%m-%d'),
            payment.amount,
            payment.get_status_display(),
            payment.notes
        ])
    
    wb.save(response)
    return response

@login_required
def tenant_submit_payment(request):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    lease = Lease.objects.filter(tenant=request.user, is_active=True).first()
    if not lease:
        messages.warning(request, 'You do not have an active lease.')
        return redirect('tenant_dashboard')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.lease = lease
            payment.save()
            messages.success(request, 'Payment submitted successfully! It will be reviewed by the admin.')
            return redirect('tenant_payment_history')
    else:
        initial_data = {
            'amount': lease.monthly_rent,
            'payment_date': timezone.now().date(),
        }
        form = PaymentForm(initial=initial_data)
    
    return render(request, 'tenant/submit_payment.html', {'form': form, 'lease': lease})

@login_required
def tenant_messages(request):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    conversation_users = User.objects.filter(models.Q(role=User.ADMIN) | models.Q(is_superuser=True))
    unread_counts = {u.id: Message.objects.filter(sender=u, recipient=request.user, is_read=False).count() for u in conversation_users}
    return render(request, 'messages/conversation_list.html', {
        'conversation_users': conversation_users,
        'unread_counts': unread_counts
    })

@login_required
def tenant_message_detail(request, pk):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    message = get_object_or_404(Message, pk=pk)
    
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'tenant/message_detail.html', {'message': message})

@login_required
def tenant_announcements(request):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    announcements = Announcement.objects.filter(
        Q(is_global=True) | Q(recipients=request.user)
    ).order_by('-created_at')
    
    return render(request, 'tenant/announcements.html', {'announcements': announcements})

@login_required
def tenant_announcement_detail(request, pk):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if not announcement.is_global and request.user not in announcement.recipients.all():
        messages.error(request, 'You are not authorized to view this announcement.')
        return redirect('tenant_announcements')
    
    return render(request, 'tenant/announcement_detail.html', {'announcement': announcement})

@login_required
def tenant_leave_request(request):
    if request.user.role != User.TENANT:
        return redirect('dashboard')
    
    lease = Lease.objects.filter(tenant=request.user, is_active=True).first()
    if not lease:
        messages.warning(request, 'You do not have an active lease.')
        return redirect('tenant_dashboard')
    
    existing_request = LeaveRequest.objects.filter(lease=lease, status=LeaveRequest.PENDING).first()
    if existing_request:
        messages.info(request, 'You already have a pending leave request.')
        return redirect('tenant_dashboard')
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.tenant = request.user
            leave_request.lease = lease
            leave_request.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('tenant_dashboard')
    else:
        initial_data = {
            'requested_end_date': timezone.now().date() + timedelta(days=30),
        }
        form = LeaveRequestForm(initial=initial_data)
    
    return render(request, 'tenant/leave_request.html', {'form': form, 'lease': lease})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@admin_required
def admin_leave_requests(request):
    leave_requests = LeaveRequest.objects.select_related('tenant', 'lease', 'lease__unit').order_by('-created_at')
    if request.method == 'POST':
        action = request.POST.get('action')
        leave_id = request.POST.get('leave_id')
        leave = get_object_or_404(LeaveRequest, id=leave_id)
        if action == 'accept' and leave.status == LeaveRequest.PENDING:
            leave.status = LeaveRequest.APPROVED
            leave.processed_at = timezone.now()
            leave.save()
            lease = leave.lease
            lease.is_active = False
            lease.end_date = leave.requested_end_date
            lease.save()
            tenant = leave.tenant
            tenant.role = User.CLIENT
            tenant.save()
            unit = lease.unit
            unit.status = Unit.AVAILABLE
            unit.save()
            messages.success(request, f"Leave request for {tenant.get_full_name()} accepted. Tenant demoted to client and unit marked available.")
        elif action == 'deny' and leave.status == LeaveRequest.PENDING:
            leave.status = LeaveRequest.REJECTED
            leave.processed_at = timezone.now()
            leave.save()
            messages.info(request, f"Leave request for {leave.tenant.get_full_name()} denied.")
        return redirect('admin_leave_requests')
    return render(request, 'admin_panel/leave_requests.html', {'leave_requests': leave_requests})

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    return render(request, 'messages/conversation_list.html', {'conversations': conversations})

@login_required
def conversation_create(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST, user=request.user)
        if form.is_valid():
            conversation = form.save()
            conversation.participants.add(request.user)
            for participant in form.cleaned_data['participants']:
                conversation.participants.add(participant)
            initial_message = request.POST.get('initial_message')
            if initial_message:
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=form.cleaned_data['participants'].first(),
                    subject=form.cleaned_data['subject'],
                    content=initial_message
                )
            return redirect('conversation_thread', conversation_id=conversation.id)
    else:
        form = ConversationForm(user=request.user)
    return render(request, 'messages/conversation_create.html', {'form': form})

@login_required
def conversation_thread(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages_qs = conversation.messages.order_by('created_at')
    messages_qs.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.method == 'POST':
        form = MessageForm(request.POST, initial={'conversation': conversation.id})
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.conversation = conversation
            other_participants = conversation.participants.exclude(id=request.user.id)
            if other_participants.exists():
                msg.recipient = other_participants.first()
            else:
                msg.recipient = request.user
            msg.subject = conversation.subject
            msg.save()
            return redirect('conversation_thread', conversation_id=conversation.id)
    else:
        form = MessageForm(initial={'conversation': conversation.id})
    return render(request, 'messages/thread.html', {
        'conversation': conversation,
        'messages_qs': messages_qs,
        'form': form
    })