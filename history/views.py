import json
from django.shortcuts import render, redirect, get_object_or_404, reverse
from history.forms import ForumEntryForm, CommentForm
from history.models import ForumEntry, Comment
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers

# Create your views here.
@login_required(login_url='/login')
def show_main(request):
    forum_entries = ForumEntry.objects.all()
    context = {
        'name': request.user.username,
        'forum_entries': forum_entries
    }
    return render(request, "forum.html", context)


def create_forum_entry(request):
    form = ForumEntryForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        forum_entry = form.save(commit=False)
        forum_entry.user = request.user
        forum_entry.save()
        return redirect('forum:show_main')

    context = {'form': form}
    return render(request, "create_forum_entry.html", context)

@login_required
def add_comment(request, forum_entry_id):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        forum_entry = get_object_or_404(ForumEntry, id=forum_entry_id)
        comment = Comment.objects.create(
            forum_entry=forum_entry,
            user=request.user,  # Use 'user' to match your model field
            content=content,
            created_at=timezone.now()
        )
        data = {
            'success': True,
            'comment': {
                'author': comment.user.username,
                'created_at': comment.created_at.strftime('%B %d, %Y, %I:%M %p'),
                'content': comment.content,
            },
            'answers_count': forum_entry.comments.count(),
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def delete_forum(request, id):
    forum = ForumEntry.objects.get(pk = id)
    forum.delete()
    return HttpResponseRedirect(reverse('forum:show_main'))

# def show_json_forum(request):
#     forum_entries = ForumEntry.objects.all()
#      # Serialize the comments into JSON format
#     data = serializers.serialize("json", forum_entries)
#     return HttpResponse(data, content_type="application/json")

def show_json_forum(request):
    forum_entries = ForumEntry.objects.all()
    data = []

    # Iterate through each forum entry to add the comment count
    for forum in forum_entries:
        data.append({
            "pk": forum.pk,
            "fields": {
                "user": forum.user.id,  # Assuming there's a foreign key to User
                "title": forum.title,
                "description": forum.description,
                "comments_count": forum.comments.count(),  # Count related comments
                'is_author' : request.user == forum.user,
            }
        })

    return JsonResponse(data, safe=False)


def show_json_comment_forum(request, forum_id):
    comments = Comment.objects.filter(forum_entry__id=forum_id)
    comments_data = []
    for comment in comments:
        comments_data.append({
            'user': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at,
            'forum_entry': comment.forum_entry.id,
        })

    return JsonResponse({'comment': comments_data})

@csrf_exempt
def delete_forum_flutter(request, forum_id):
    if request.method == 'POST':
        try:
            # Retrieve the article by ID
            forum = ForumEntry.objects.get(id=forum_id)
            if forum.user != request.user:
                return JsonResponse({'error': 'You are not allowed to delete this article'}, status=403)
            # Perform the delete operation
            forum.delete()
            # Return success response
            return JsonResponse({'success': True, 'message': 'Article deleted successfully'})
        except ForumEntry.DoesNotExist:
            # If the article does not exist
            return JsonResponse({'success': False, 'message': 'Article not found'}, status=404)
        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        # If the request is not POST
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt  
def create_forum_flutter(request):
    if request.method == 'POST':
        # Parse the JSON body
        data = json.loads(request.body)
        new_forum = ForumEntry.objects.create(
            title = data['title'],
            description = data['description'],
            user = request.user,
        )
        new_forum.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)

@csrf_exempt  # Only for development. Remove in production.
def add_comment_flutter(request, forum_id):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            content = data.get('content')

            # Validate the received data
            if content is None:
                return JsonResponse(
                    {"status": "error", "message": "Rating and review are required."},
                    status=400
                )
            if not isinstance(content, str) or not content.strip():
                return JsonResponse(
                    {"status": "error", "message": "Review text cannot be empty."},
                    status=400
                )

            # Retrieve the Food object
            Forum = get_object_or_404(ForumEntry, pk=forum_id)

            # Create and save the new review
            new_comment = Comment.objects.create(
                forum_entry = Forum, 
                user=request.user,  # Correct field name
                content=content,
                created_at=timezone.now(),
            )
            new_comment.save()
            return JsonResponse({"status": "success"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data."},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=500
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Only POST method is allowed."},
            status=405
        )