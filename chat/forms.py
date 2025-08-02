from django.forms import ModelForm
from chat.models import Chat, Message
from django import forms
from main.models import Profile
from django.contrib.auth.models import User

class ChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = ['users']
        widgets = {
            'users': forms.SelectMultiple(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-[#AB886D]focus:border-[#AB886D] block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-[#AB886D] dark:focus:border-[#AB886D]'
            })
        }
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)  # Get the current user from kwargs
        super(ChatForm, self).__init__(*args, **kwargs)
        
        # Exclude the current user from the users queryset
        self.fields['users'].queryset = User.objects.exclude(id=current_user.id)
        
        if(current_user.profile.role == "user"):
            self.fields['users'].queryset = User.objects.filter(profile__role='seller')
        else:
            # If the current user is a seller, show users they have previously chatted with
            existing_chats = Chat.objects.all()
            users_selected = set()

            # Collect user IDs from chats the seller has participated in
            for chat in existing_chats:
                chat_users_set = set(chat.users.all())
                if current_user in chat_users_set:
                    chat_users_set.remove(current_user)
                    users_selected.update(user.id for user in chat_users_set)
            self.fields['users'].queryset = User.objects.filter(id__in=users_selected)
            

class MessageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
            'placeholder': 'Type your message...',
            'class': 'block mx-4 p-2 w-full h-10 text-sm text-gray-900 bg-white rounded-lg border border-gray-300 focus:ring-[#AB886D] focus:border-[#AB886D] dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-[#AB886D] dark:focus:border-[#AB886D]'
        }))

    class Meta:
        model = Message
        fields = ['content']