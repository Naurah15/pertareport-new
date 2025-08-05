from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .forms import LaporanForm, KegiatanFormSet
from .models import Laporan

def laporan_form_view(request):
    if request.method == 'POST':
        form = LaporanForm(request.POST)
        lokasi = request.POST.get('lokasi')  # dari input hidden (geo)
        
        if form.is_valid():
            laporan = form.save(commit=False)
            laporan.lokasi = lokasi
            laporan.tanggal_proses = timezone.now()
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
        'preview_no_document': preview_no_document
    })

def laporan_success_view(request):
    return render(request, 'laporan_success.html')