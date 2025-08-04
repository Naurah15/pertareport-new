from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product
from .models import Bookmarks
from report.models import Product
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Product, Bookmarks
from datetime import datetime

@csrf_exempt
@login_required
def remove_bookmark(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        user = request.user

        # Mencari atau membuat bookmark baru
        bookmark, created = Bookmarks.objects.get_or_create(user=user, product=product)

        if not created:
            # Jika bookmark sudah ada, hapus
            bookmark.delete()
            # is_bookmarked = False
            return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
@csrf_exempt
@login_required
def add_bookmark(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    bookmark, created = Bookmarks.objects.get_or_create(user=user, product=product)

    if not created:
        bookmark.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@csrf_exempt
@login_required
def bookmarked_products(request):
    bookmarks = Bookmarks.objects.filter(user=request.user)
    bookmarked_products = [bookmark.product for bookmark in bookmarks]

    return render(request, 'show_bookmarks.html', {'bookmarked_products': bookmarked_products})

@csrf_exempt
def add_bookmark_flutter(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Hardcoded user for development
        user_id = request.user.id # Default to user ID 1 if not provided
        
        # Menambahkan bookmark
        bookmark, created = Bookmarks.objects.get_or_create(user_id=user_id, product=product)

        if created:
            return JsonResponse({'success': True, 'message': 'Bookmark added.'}, status=201)
        else:
            return JsonResponse({'success': False, 'message': 'Bookmark already exists.'}, status=200)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def remove_bookmark_flutter(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Hardcoded user for development
        user_id = request.user.id # Default to user ID 1 if not provided

        # Menghapus bookmark jika ada
        bookmark = Bookmarks.objects.filter(user_id=user_id, product=product).first()
        if bookmark:
            bookmark.delete()
            return JsonResponse({'success': True, 'message': 'Bookmark removed.'}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'Bookmark not found.'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def bookmarked_products_flutter(request):
    if request.method == 'GET':
        # Hardcoded user for development
        user_id = request.user.id
        # Mendapatkan semua bookmark untuk user saat ini
        bookmarks = Bookmarks.objects.filter(user_id=user_id)
        
        # Membentuk data produk yang di-bookmark
        bookmarked_products = [
            {
                'id': bookmark.product.pk,
                'nama': bookmark.product.nama,
                'kategori': bookmark.product.kategori,
                'harga': str(bookmark.product.harga),  # Konversi Decimal ke string untuk JSON
                'nama_restoran': bookmark.product.nama_restoran,
                'lokasi': bookmark.product.lokasi,
                'url_gambar': bookmark.product.url_gambar,
                'created_at': bookmark.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': bookmark.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for bookmark in bookmarks
        ]

        # Mengembalikan data dalam format JSON
        return JsonResponse({'success': True, 'bookmarked_products': bookmarked_products}, status=200)

    # Menangani jika request method tidak valid
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


    