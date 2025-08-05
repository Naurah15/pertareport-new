import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from review.models import ReviewEntry
from review.forms import ReviewEntryForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponseForbidden

# Show Review View
@csrf_exempt
@login_required
def show_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order = request.GET.get('order', 'newest')  # Ambil parameter 'order' dari query string

    # Urutkan review berdasarkan parameter 'order'
    if order == 'oldest':
        reviews = ReviewEntry.objects.filter(product=product).select_related('user').order_by('time')
    else:  # default ke 'newest'
        reviews = ReviewEntry.objects.filter(product=product).select_related('user').order_by('-time')

    context = {
        'reviews': reviews,
        'product': product,
        'order': order  # Kirim parameter order ke template
    }
    return render(request, "page.html", context)

# Add Review View
@csrf_exempt
@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ReviewEntryForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.review_text = review.review_text.replace("\r", "\n")  # Ganti \r dengan \n untuk line breaks
            review.save()

            # Mengembalikan respons JSON
            return JsonResponse({
                'username': review.user.username,
                'time': review.time.strftime("%B %d, %Y, %I:%M %p"),
                'review_text': review.review_text,
            })
        else:
            return HttpResponse("Form tidak valid", status=400)  # Mengembalikan HTTP 400 Bad Request

    # Jika bukan POST, render halaman add_review.html
    context = {
        'form': form,
        'product': product
    }
    return render(request, "add_review.html", context)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(ReviewEntry, pk=pk)

    if request.method == 'POST':
        review.delete()
        return redirect('review:show_review', pk=review.product.pk)
    return redirect('review:show_review', pk=review.product.pk)


@csrf_exempt
def get_product_reviews_json(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        order = request.GET.get('order', 'newest')

        if order == 'oldest':
            reviews = ReviewEntry.objects.filter(product=product).order_by('time')
        else:
            reviews = ReviewEntry.objects.filter(product=product).order_by('-time')

        reviews_data = [{
            'id': review.id,
            'username': review.user.username,
            'review_text': review.review_text,
            'time': review.time.strftime("%Y-%m-%d %H:%M:%S"),
        } for review in reviews]

        return JsonResponse({
            'status': 'success',
            'product_id': pk,
            'reviews': reviews_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
def add_review_json(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = get_object_or_404(Product, pk=pk)

            review = ReviewEntry.objects.create(
                user=request.user,  # Pastikan user terautentikasi
                product=product,
                review_text=data.get('review_text', '').replace('\r', '\n'),
            )

            return JsonResponse({
                'status': 'success',
                'review': {
                    'id': review.id,
                    'username': review.user.username,
                    'review_text': review.review_text,
                    'time': review.time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


@csrf_exempt
def delete_review_json(request, pk):
    try:
        if request.method == 'DELETE':
            review = get_object_or_404(ReviewEntry, pk=pk)
            review.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil dihapus.'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request method.'
            }, status=405)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)