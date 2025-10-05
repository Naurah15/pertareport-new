import json
import os
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .forms import LaporanForm, KegiatanFormSet
from .models import SPBU, Laporan
from django.contrib.auth.decorators import login_required
from .forms import JenisKegiatanForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .models import Laporan, KegiatanLaporan, JenisKegiatan, KegiatanFoto
from django.core.files.storage import default_storage
from django.conf import settings

@csrf_exempt
@require_http_methods(["GET"])
def get_jenis_kegiatan(request):
    """API untuk mendapatkan daftar jenis kegiatan"""
    try:
        jenis_kegiatan = JenisKegiatan.objects.all().order_by('nama')
        data = []
        for jenis in jenis_kegiatan:
            data.append({
                'id': jenis.id,
                'nama': jenis.nama
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_laporan(request):
    """API untuk membuat laporan baru"""
    try:
        data = json.loads(request.body)
        
        # Validasi data yang diperlukan
        required_fields = ['lokasi', 'nama_team_support', 'remark', 'kegiatan_id']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Field {field} is required'
                }, status=400)
        
        spbu_id = data.get('spbu_id')
        spbu_obj = None
        if spbu_id:
            try:
                spbu_obj = SPBU.objects.get(id=spbu_id)
            except SPBU.DoesNotExist:
                pass

        # Buat laporan baru
        laporan = Laporan.objects.create(
            lokasi=data['lokasi'].strip(),
            nama_team_support=data['nama_team_support'].strip(),
            spbu=spbu_obj 
        )
        
        # Buat kegiatan laporan
        try:
            jenis_kegiatan = JenisKegiatan.objects.get(id=data['kegiatan_id'])
        except JenisKegiatan.DoesNotExist:
            laporan.delete()  # Rollback
            return JsonResponse({
                'status': 'error',
                'message': 'Jenis kegiatan tidak ditemukan'
            }, status=400)
        
        # Handle kegiatan_other
        kegiatan_other = data.get('kegiatan_other', '').strip() if data.get('kegiatan_other') else ''
        
        kegiatan_laporan = KegiatanLaporan.objects.create(
            laporan=laporan,
            kegiatan=jenis_kegiatan,
            kegiatan_other=kegiatan_other,
            remark=data['remark'].strip()
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Laporan berhasil dibuat',
            'laporan_id': laporan.id,
            'no_document': laporan.no_document,
            'kegiatan_laporan_id': kegiatan_laporan.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_laporan_images(request):
    """API untuk upload foto laporan"""
    try:
        laporan_id = request.POST.get('laporan_id')
        if not laporan_id:
            return JsonResponse({
                'status': 'error',
                'message': 'laporan_id is required'
            }, status=400)
        
        try:
            laporan = Laporan.objects.get(id=laporan_id)
            # Ambil kegiatan laporan terbaru untuk laporan ini
            kegiatan_laporan = KegiatanLaporan.objects.filter(laporan=laporan).last()
            if not kegiatan_laporan:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Kegiatan laporan tidak ditemukan'
                }, status=404)
        except Laporan.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Laporan tidak ditemukan'
            }, status=404)
        
        images = request.FILES.getlist('images')
        if not images:
            return JsonResponse({
                'status': 'error',
                'message': 'No images provided'
            }, status=400)
        
        uploaded_files = []
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        max_size = 5 * 1024 * 1024  # 5MB
        
        for image in images:
            # Validasi file
            if not image.content_type in allowed_types:
                continue
            
            if image.size > max_size:
                continue
                
            # Simpan file
            try:
                foto = KegiatanFoto.objects.create(
                    kegiatan=kegiatan_laporan,
                    foto=image
                )
                uploaded_files.append({
                    'id': foto.id,
                    'url': request.build_absolute_uri(foto.foto.url) if foto.foto else None
                })
            except Exception as e:
                continue
        
        return JsonResponse({
            'status': 'success',
            'message': f'{len(uploaded_files)} foto berhasil diupload',
            'files': uploaded_files
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_laporan_list(request):
    """API untuk mendapatkan daftar laporan"""
    try:
        laporan_list = Laporan.objects.all().order_by('-tanggal_proses')
        data = []
        
        for laporan in laporan_list:
            kegiatan_list = []
            for kegiatan in laporan.kegiatan_list.all():
                foto_list = []
                for foto in kegiatan.foto_list.all():
                    foto_list.append({
                        'id': foto.id,
                        'url': request.build_absolute_uri(foto.foto.url) if foto.foto else None
                    })
                
                kegiatan_list.append({
                    'id': kegiatan.id,
                    'kegiatan': kegiatan.get_kegiatan_display_name(),
                    'kegiatan_other': kegiatan.kegiatan_other,
                    'remark': kegiatan.remark,
                    'foto': kegiatan.foto.url if kegiatan.foto else None,
                    'foto_list': foto_list
                })
            
            data.append({
                'id': laporan.id,
                'lokasi': laporan.lokasi,
                'nama_team_support': laporan.nama_team_support,
                'tanggal_proses': laporan.tanggal_proses.isoformat(),
                'no_document': laporan.no_document,
                'kegiatan_list': kegiatan_list
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def laporan_form_view(request):
    if request.method == 'POST':
        form = LaporanForm(request.POST)
        lokasi = request.POST.get('lokasi')  # dari input hidden (geo)
        
        if form.is_valid():
            laporan = form.save(commit=False)
            laporan.lokasi = lokasi
            laporan.tanggal_proses = timezone.now()
            laporan.user = request.user  # Tambah ini
            laporan.save()
            
            # Process kegiatan formset
            kegiatan_formset = KegiatanFormSet(request.POST, request.FILES, instance=laporan)
            
            if kegiatan_formset.is_valid():
                kegiatan_formset.save()
                messages.success(request, f'Laporan berhasil disimpan dengan nomor dokumen: {laporan.no_document}')
                return redirect('report:laporan_success')
            else:
                # Jika formset tidak valid, hapus laporan yang sudah dibuat
                laporan.delete()
                messages.error(request, 'Terjadi kesalahan dalam menyimpan kegiatan.')
        else:
            kegiatan_formset = KegiatanFormSet(request.POST, request.FILES)
    else:
        form = LaporanForm()
        kegiatan_formset = KegiatanFormSet()
    
    # Generate preview nomor dokumen untuk ditampilkan
    now = timezone.now()
    prefix = f"PTPR{now.strftime('%y%m')}"
    last_laporan = Laporan.objects.filter(
        no_document__startswith=prefix
    ).order_by('-no_document').first()
    
    if last_laporan:
        last_number = int(last_laporan.no_document.split('-')[1])
        preview_number = f"{last_number + 1:04d}"
    else:
        preview_number = "0001"
    
    preview_no_document = f"{prefix}-{preview_number}"
    
    return render(request, 'laporan_form.html', {
        'form': form,
        'kegiatan_formset': kegiatan_formset,
        'preview_no_document': preview_no_document,
        'username': request.user.username if request.user.is_authenticated else ''
    })

def laporan_success_view(request):
    return render(request, 'laporan_success.html')

@login_required
def manage_jenis_kegiatan(request):
    if request.user.username != "admin":
        messages.error(request, "Anda tidak punya akses.")
        return redirect('report:laporan_form')

    if request.method == "POST":
        if 'delete_id' in request.POST:
            JenisKegiatan.objects.filter(id=request.POST['delete_id']).delete()
            messages.success(request, "Jenis kegiatan berhasil dihapus.")
            return redirect('report:manage_jenis_kegiatan')
        else:
            form = JenisKegiatanForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Jenis kegiatan berhasil ditambahkan.")
                return redirect('report:manage_jenis_kegiatan')
    else:
        form = JenisKegiatanForm()

    kegiatan_list = JenisKegiatan.objects.all()
    return render(request, "manage_jenis_kegiatan.html", {
        "form": form,
        "kegiatan_list": kegiatan_list
    })

# Tambahkan ke views.py Anda

@csrf_exempt
@require_http_methods(["POST"])
def add_kegiatan_to_laporan(request):
    """API untuk menambah kegiatan ke laporan yang sudah ada"""
    try:
        data = json.loads(request.body)
        
        # Validasi data yang diperlukan
        required_fields = ['laporan_id', 'remark', 'kegiatan_id']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Field {field} is required'
                }, status=400)
        
        # Cari laporan
        try:
            laporan = Laporan.objects.get(id=data['laporan_id'])
        except Laporan.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Laporan tidak ditemukan'
            }, status=404)
        
        # Cari jenis kegiatan
        try:
            jenis_kegiatan = JenisKegiatan.objects.get(id=data['kegiatan_id'])
        except JenisKegiatan.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Jenis kegiatan tidak ditemukan'
            }, status=400)
        
        # Handle kegiatan_other
        kegiatan_other = data.get('kegiatan_other', '').strip() if data.get('kegiatan_other') else ''
        
        # Tambah kegiatan baru ke laporan yang sudah ada
        kegiatan_laporan = KegiatanLaporan.objects.create(
            laporan=laporan,
            kegiatan=jenis_kegiatan,
            kegiatan_other=kegiatan_other,
            remark=data['remark'].strip()
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Kegiatan berhasil ditambahkan ke laporan',
            'laporan_id': laporan.id,
            'no_document': laporan.no_document,
            'kegiatan_laporan_id': kegiatan_laporan.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_kegiatan_images(request):
    """API untuk upload foto ke kegiatan laporan tertentu"""
    try:
        kegiatan_laporan_id = request.POST.get('kegiatan_laporan_id')
        if not kegiatan_laporan_id:
            return JsonResponse({
                'status': 'error',
                'message': 'kegiatan_laporan_id is required'
            }, status=400)
        
        try:
            kegiatan_laporan = KegiatanLaporan.objects.get(id=kegiatan_laporan_id)
        except KegiatanLaporan.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Kegiatan laporan tidak ditemukan'
            }, status=404)
        
        images = request.FILES.getlist('images')
        if not images:
            return JsonResponse({
                'status': 'error',
                'message': 'No images provided'
            }, status=400)
        
        uploaded_files = []
        skipped_files = []
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        max_size = 5 * 1024 * 1024  # 5MB
        
        for i, image in enumerate(images):
            if image.content_type not in allowed_types:
                skipped_files.append({'name': image.name, 'reason': f'Invalid type: {image.content_type}'})
                continue
            
            if image.size > max_size:
                skipped_files.append({'name': image.name, 'reason': f'Too large: {image.size}'})
                continue

            try:
                if not kegiatan_laporan.foto:  
                    # simpan ke field utama (biar web tetap bisa baca)
                    kegiatan_laporan.foto = image
                    kegiatan_laporan.save()
                    uploaded_files.append({
                        'id': kegiatan_laporan.id,
                        'url': request.build_absolute_uri(kegiatan_laporan.foto.url),
                        'name': image.name,
                        'is_primary': True
                    })
                else:
                    # simpan ke tabel KegiatanFoto (tambahan)
                    foto = KegiatanFoto.objects.create(
                        kegiatan=kegiatan_laporan,
                        foto=image
                    )
                    uploaded_files.append({
                        'id': foto.id,
                        'url': request.build_absolute_uri(foto.foto.url),
                        'name': image.name,
                        'is_primary': False
                    })
            except Exception as e:
                skipped_files.append({'name': image.name, 'reason': f'Upload error: {str(e)}'})
                continue
        
        if not uploaded_files:
            return JsonResponse({
                'status': 'error',
                'message': 'No files were successfully uploaded',
                'skipped_files': skipped_files
            }, status=400)
        
        response_data = {
            'status': 'success',
            'message': f'{len(uploaded_files)} foto berhasil diupload',
            'files': uploaded_files
        }
        if skipped_files:
            response_data['skipped_files'] = skipped_files
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def manage_spbu(request):
    if request.user.username != "admin":
        messages.error(request, "Anda tidak punya akses.")
        return redirect('report:laporan_form')

    if request.method == "POST":
        if 'delete_id' in request.POST:
            SPBU.objects.filter(id=request.POST['delete_id']).delete()
            messages.success(request, "SPBU berhasil dihapus.")
            return redirect('report:manage_spbu')
        else:
            # Tambah SPBU baru
            nama = request.POST.get('nama')
            kode = request.POST.get('kode')
            alamat = request.POST.get('alamat', '')
            
            if nama and kode:
                SPBU.objects.create(nama=nama, kode=kode, alamat=alamat)
                messages.success(request, "SPBU berhasil ditambahkan.")
                return redirect('report:manage_spbu')

    spbu_list = SPBU.objects.all()
    return render(request, "manage_spbu.html", {
        "spbu_list": spbu_list
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_spbu_list(request):
    """API untuk mendapatkan daftar SPBU"""
    try:
        spbu_list = SPBU.objects.all().order_by('kode')
        data = []
        for spbu in spbu_list:
            data.append({
                'id': spbu.id,
                'nama': spbu.nama,
                'kode': spbu.kode,
                'alamat': spbu.alamat
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)