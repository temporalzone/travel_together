from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import TravelGroup, GroupMember, Chat
from .forms import GroupForm, ChatForm
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp = send_verification_email(user)  # Send email
            request.session['otp'] = otp  # Save code temporarily
            request.session['email'] = user.email
            messages.success(request, 'Check your email for verification code!')
            return redirect('verify_email')  # Go to verify page
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
 
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    groups = TravelGroup.objects.filter(is_public=True)
    query = request.GET.get('q', '')
    group_type = request.GET.get('type', '')
    if query:
        groups = groups.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if group_type:
        groups = groups.filter(group_type=group_type)
    owned_groups = TravelGroup.objects.filter(owner=request.user)
    context = {
        'groups': groups,
        'owned_groups': owned_groups,
        'query': query,
        'group_type': group_type,
    }
    return render(request, 'dashboard.html', context)

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            messages.success(request, 'Group created—invite your travel tribe!')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'create_group.html', {'form': form})

@login_required
def group_detail(request, pk):
    group = get_object_or_404(TravelGroup, pk=pk)
    is_member = GroupMember.objects.filter(user=request.user, group=group, status='approved').exists()
    is_owner = group.owner == request.user
    members = GroupMember.objects.filter(group=group, status='approved').select_related('user')
    pending_requests = GroupMember.objects.filter(group=group, status='pending') if is_owner else []
    context = {
        'group': group,
        'is_member': is_member,
        'is_owner': is_owner,
        'members': members,
        'pending_requests': pending_requests,
    }
    return render(request, 'group_detail.html', context)

@login_required
def request_join(request, group_id):
    group = get_object_or_404(TravelGroup, group_id=group_id)
    if not GroupMember.objects.filter(user=request.user, group=group).exists():
        GroupMember.objects.create(user=request.user, group=group)
        messages.success(request, 'Join request sent—await the owner\'s nod!')
    return redirect('group_detail', pk=group_id)

@login_required
def group_chat(request, pk):
    group = get_object_or_404(TravelGroup, pk=pk)
    is_member = GroupMember.objects.filter(user=request.user, group=group, status='approved').exists() or group.is_public
    if not is_member and not group.is_public:
        messages.error(request, "You need to join this private group first!")
        return redirect('group_detail', pk=pk)
    chats = Chat.objects.filter(group=group).order_by('-timestamp')[:50]
    form = ChatForm()
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid() and is_member:
            chat = form.save(commit=False)
            chat.group = group
            chat.user = request.user
            chat.save()
            return redirect('group_chat', pk=pk)
    context = {'group': group, 'chats': chats, 'form': form}
    return render(request, 'group_chat.html', context)

@login_required
def manage_requests(request, pk):
    group = get_object_or_404(TravelGroup, pk=pk)
    if group.owner != request.user:
        messages.error(request, "Only the group owner can manage requests!")
        return redirect('group_detail', pk=pk)
    requests = GroupMember.objects.filter(group=group).exclude(status='approved')
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        action = request.POST.get('action')
        member = get_object_or_404(GroupMember, id=member_id, group=group)
        if action == 'approve':
            member.status = 'approved'
        elif action == 'reject':
            member.status = 'rejected'
        elif action == 'block':
            member.status = 'blocked'
        member.save()
        messages.success(request, f"Request {action}d successfully!")
        return redirect('manage_requests', pk=pk)
    context = {'group': group, 'requests': requests}
    return render(request, 'manage_requests.html', context)

def send_verification_email(user):
    otp_code = random.randint(100000, 999999)  # Makes the code
    subject = 'Welcome to Travel Together!'
    message = f'Hi {user.username}, your verification code is {otp_code}. Use it to confirm your account.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    return otp_code  # Gives the code back for checking

#def send_verification_sms(phone_number):
#    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#    otp_code = random.randint(100000, 999999)
#    message = client.messages.create(
 #       body=f'Your Travel Together verification code is {otp_code}.',
 #       from_=settings.TWILIO_PHONE_NUMBER,
 #       to=phone_number
 #   )
  #  return otp_code

def verify_otp(request):
    if request.method == 'POST':
        entered_code = request.POST.get('otp')
        saved_code = request.session.get('otp')
        if entered_code == str(saved_code):
            # Verified—log in
            phone = request.session.get('phone')
            # Get user from phone (you can query UserProfile)
            user = User.objects.get(profile__phone_number=phone)
            login(request, user)
            del request.session['otp']  # Clear session
            messages.success(request, 'Verified! Welcome to dashboard.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Wrong code. Try again.')
    return render(request, 'verify_otp.html')

def verify_email(request):
    if request.method == 'POST':
        entered_code = request.POST.get('otp')
        saved_code = request.session.get('otp')
        if entered_code == str(saved_code):
            # Verified—log in
            email = request.session.get('email')
            user = User.objects.get(email=email)
            login(request, user)
            del request.session['otp']  # Clear
            messages.success(request, 'Email verified! Welcome to dashboard.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Wrong code. Try again.')
    return render(request, 'verify_email.html')