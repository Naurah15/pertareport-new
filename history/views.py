import os
import openpyxl
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from report.models import Laporan
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from report.models import Laporan
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl.drawing.image import Image as XLImage
from django.conf import settings


@login_required
def history_list(request):
    user = request.user

    # Admin bisa lihat semua laporan
    if user.username == 'admin' and user.check_password('Mimin1234%'):
        laporan_list = Laporan.objects.all().order_by('-tanggal_proses')
    else:
        laporan_list = Laporan.objects.filter(
        nama_team_support__iexact=user.username
        ).order_by('-tanggal_proses')

    return render(request, 'history_list.html', {
        'laporan_list': laporan_list
    })


@login_required
def download_laporan_excel(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    kegiatan_list = laporan.kegiatan_list.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Laporan"

    ws.append(["No Document", laporan.no_document])
    ws.append(["Lokasi", laporan.lokasi])
    ws.append(["Nama Team Support", laporan.nama_team_support])
    ws.append(["Tanggal Proses", laporan.tanggal_proses.strftime("%d-%m-%Y %H:%M")])
    ws.append([])
    ws.append(["Jenis Kegiatan", "Remark"])

    for kegiatan in kegiatan_list:
        ws.append([kegiatan.get_kegiatan_display_name(), kegiatan.remark])

    # Tambah gambar kalau ada
    if kegiatan.foto:
        img_path = os.path.join(settings.MEDIA_ROOT, str(kegiatan.foto))
        if os.path.exists(img_path):
            img = XLImage(img_path)
            img.width = 300  # resize kalau mau
            img.height = 200
            ws.add_image(img, "E1")  # posisikan di cell E1

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="Laporan_{laporan.no_document}.xlsx"'
    wb.save(response)
    return response


@login_required
def download_laporan_pdf(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    kegiatan_list = laporan.kegiatan_list.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Laporan_{laporan.no_document}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    y = 800

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, f"Laporan: {laporan.no_document}")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(100, y, f"Lokasi: {laporan.lokasi}")
    y -= 20
    p.drawString(100, y, f"Nama Team Support: {laporan.nama_team_support}")
    y -= 20
    p.drawString(100, y, f"Tanggal Proses: {laporan.tanggal_proses.strftime('%d-%m-%Y %H:%M')}")
    y -= 40

    for kegiatan in kegiatan_list:
        p.drawString(100, y, f"{kegiatan.get_kegiatan_display_name()} - {kegiatan.remark}")
        y -= 20

    # Tambah gambar kalau ada
    if kegiatan.foto:
        img_path = os.path.join(settings.MEDIA_ROOT, str(kegiatan.foto))
        if os.path.exists(img_path):
            p.drawImage(img_path, 100, y-200, width=300, height=200)  # atur posisi dan ukuran
            y -= 220

    p.showPage()
    p.save()
    return response


