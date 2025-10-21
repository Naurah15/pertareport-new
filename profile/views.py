from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

@login_required
def profile_view(request):
    """View untuk menampilkan profil user"""
    user = request.user
    profile = user.user_profile  # PERBAIKI: gunakan user_profile sesuai related_name

    context = {
        'user': user,
        'username': user.username,
        'email': user.email,
        'phone_number': profile.phone_number,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }
    return render(request, 'profile.html', context)

@csrf_exempt
@login_required
def update_profile(request):
    """View untuk update profil user via AJAX"""
    if request.method == 'POST':
        user = request.user
        profile = user.user_profile  # PERBAIKI

        email = request.POST.get('email', '').strip()
        if email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email already used by another user.'
                }, status=400)
            user.email = email
        else:
            user.email = ''

        phone_number = request.POST.get('phone_number', '').strip()
        profile.phone_number = phone_number

        try:
            user.save()
            profile.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    }, status=405)

@login_required
@csrf_exempt
def profile_flutter(request):
    """View untuk Flutter - mendapatkan data profil user"""
    if request.method == 'GET':
        user = request.user
        profile = user.user_profile  # PERBAIKI

        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': profile.phone_number,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
        }

        return JsonResponse({
            'success': True,
            'profile': profile_data
        }, status=200)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    }, status=405)

@csrf_exempt
@login_required
def update_profile_flutter(request):
    """View untuk Flutter - update profil user"""
    if request.method == 'POST':
        user = request.user
        profile = user.user_profile  # PERBAIKI

        # Parse JSON body untuk Flutter
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            phone_number = data.get('phone_number', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data.'
            }, status=400)

        if email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email already used by another user.'
                }, status=400)
            user.email = email

        profile.phone_number = phone_number

        try:
            user.save()
            profile.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!' 
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    }, status=405)