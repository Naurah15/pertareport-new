import json
from django.shortcuts import render, redirect, get_object_or_404
from chat.forms import MessageForm
from chat.models import Chat, Message
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

def create_chat(request):
    if(request.user.profile.role == "user"):
        user_valid = User.objects.filter(profile__role='seller')
    else:
        existing_chats = Chat.objects.all()
        users_selected = set()

        for chat in existing_chats:
            chat_users_set = set(chat.users.all())
            if request.user in chat_users_set:
                chat_users_set.remove(request.user)
                users_selected.update(user.id for user in chat_users_set)
        user_valid = User.objects.filter(id__in=users_selected)
    return render(request, 'create_chat.html', {'users': user_valid, 'user_loggedin':request.user, 'existing_messages':Message.objects.all().order_by('-timestamp')})


def handle_room(request, selected_user_id):
    selected_user = get_object_or_404(User, id=selected_user_id)
    all_users = [selected_user, request.user]

    existing_chats = Chat.objects.filter(users__in=all_users).distinct()
    for chat in existing_chats:
        chat_users_set = set(chat.users.all())
        if chat_users_set == set(all_users):
            return redirect('chat:send_message', chat_id=chat.id)

    chat = Chat.objects.create()
    chat.users.set(all_users) 
    chat.save()

    return redirect('chat:send_message', chat_id=chat.id)

def send_message(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat 
            message.sender = request.user
            message.save()
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = MessageForm()

    return render(request, 'chat_detail.html', {'form': form, 'chat': chat})

def delete_message(request, message_id):
    message = Message.objects.get(pk=message_id)
    message.delete()
    return redirect('chat:send_message', message.chat.id)

def show_json_chat(request):
    data = Chat.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_json_message(request):
    data = Message.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def create_chat_flutter(request):
    if(request.user.profile.role == "user"):
        user_valid = User.objects.filter(profile__role='seller')
    else:
        existing_chats = Chat.objects.all()
        users_selected = set()

        for chat in existing_chats:
            chat_users_set = set(chat.users.all())
            if request.user in chat_users_set:
                chat_users_set.remove(request.user)
                users_selected.update(user.id for user in chat_users_set)
        user_valid = User.objects.filter(id__in=users_selected)

    user_valid_data = serializers.serialize('json', user_valid)
    user_loggedin_data = serializers.serialize('json', [request.user])

    response_data = {
        'users': user_valid_data,
        'user_loggedin': user_loggedin_data,
    }

    return JsonResponse(response_data)

@csrf_exempt
def handle_room_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('id')
        
        selected_user = get_object_or_404(User, id=user_id)
        all_users = [selected_user, request.user]

        existing_chats = Chat.objects.filter(users__in=all_users).distinct()
        for chat in existing_chats:
            chat_users_set = set(chat.users.all())
            if chat_users_set == set(all_users):
                return JsonResponse({"status": "success", "chat_id": chat.id}, status=200)

        chat = Chat.objects.create()
        chat.users.set(all_users) 
        chat.save()

        return JsonResponse({"status": "success", "chat_id": chat.id}, status=200)
    
    else:
        return JsonResponse({"status": "error", "chat_id": "gagal"}, status=401)

@csrf_exempt
def send_message_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            content = data.get('messages')
            
            chat = get_object_or_404(Chat, pk=chat_id)
            
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content
            )

            return JsonResponse({
                'status': 'success',
                'message': {
                    'pk': str(message.id),
                    'fields': {
                        'chat': str(message.chat.id), 
                        'sender': message.sender.username,  
                        'content': message.content,
                        'timestamp': message.timestamp.isoformat()
                    }
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_messages_flutter(request, chat_id):
    try:
        chat = Chat.objects.get(pk=chat_id)
        messages = chat.messages.all()

        messages_data = [{
            'pk': str(message.id), 
            'fields': {
                'chat': str(message.chat.id), 
                'sender': message.sender.username,  
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            }
        } for message in messages]

        response_data = {
            'messages': messages_data,
            'user_loggedin': request.user.username
        }
        return JsonResponse(response_data, safe=False)

    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)

@csrf_exempt
def delete_message_flutter(request, message_id):
    if request.method == 'DELETE':
        try:
            message = Message.objects.get(id=message_id)
            message.delete()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
