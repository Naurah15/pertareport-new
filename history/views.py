import urllib.parse
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
from openpyxl.utils import get_column_letter
from reportlab.lib.units import inch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_date
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors


@login_required
def history_list(request):
    user = request.user
    
    # Get base queryset based on user permissions
    if user.username == 'admin' and user.check_password('Mimin1234%'):
        laporan_queryset = Laporan.objects.all()
    else:
        laporan_queryset = Laporan.objects.filter(
            nama_team_support__iexact=user.username
        )
    
    # Apply date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date_parsed = parse_date(start_date)
            if start_date_parsed:
                laporan_queryset = laporan_queryset.filter(
                    tanggal_proses__date__gte=start_date_parsed
                )
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_parsed = parse_date(end_date)
            if end_date_parsed:
                laporan_queryset = laporan_queryset.filter(
                    tanggal_proses__date__lte=end_date_parsed
                )
        except ValueError:
            pass
    
    # Order by name first, then by date
    laporan_list = laporan_queryset.order_by('nama_team_support', '-tanggal_proses')

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

    # ==== Styling dasar ====
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="003876", end_color="003876", fill_type="solid")
    title_font = Font(bold=True, size=14, color="003876")

    # ==== Judul ====
    ws.merge_cells('A1:C1')
    cell = ws['A1']
    cell.value = f"LAPORAN {laporan.no_document}"
    cell.font = title_font
    cell.alignment = Alignment(horizontal="center")

    ws.append([])
    ws.append(["No Document", laporan.no_document])
    coord = (laporan.lokasi or "").strip()
    ws.append(["Lokasi", coord])
    # ambil koordinat lalu jadikan hyperlink langsung ke Google Maps
    ws["B4"].hyperlink = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(coord)}"
    ws["B4"].style = "Hyperlink"


    ws.append(["Nama Team Support", laporan.nama_team_support])
    ws.append(["Tanggal Proses", laporan.tanggal_proses.strftime("%d-%m-%Y %H:%M")])
    ws.append([])

    # ==== Header tabel ====
    header_row = ws.max_row + 1
    headers = ["Jenis Kegiatan", "Remark", "Foto"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # ==== Data & gambar ====
    row_num = ws.max_row + 1
    for kegiatan in kegiatan_list:
        ws.append([kegiatan.get_kegiatan_display_name(), kegiatan.remark, ""])
        foto_col = 3  # mulai dari kolom C

        # Foto utama
        if kegiatan.foto:
            img_path = os.path.join(settings.MEDIA_ROOT, str(kegiatan.foto))
            if os.path.exists(img_path):
                img = XLImage(img_path)
                img.width = 300
                img.height = 200
                ws.add_image(img, f"{get_column_letter(foto_col)}{row_num}")
                ws.column_dimensions[get_column_letter(foto_col)].width = 50  # ✅ lebar kolom foto
                ws.row_dimensions[row_num].height = 160                      # ✅ tinggi baris
                foto_col += 1

        # Foto tambahan
        for foto in kegiatan.foto_list.all():
            img_path = os.path.join(settings.MEDIA_ROOT, str(foto.foto))
            if os.path.exists(img_path):
                img = XLImage(img_path)
                img.width = 300
                img.height = 200
                col_letter = get_column_letter(foto_col)
                ws.add_image(img, f"{col_letter}{row_num}")
                ws.column_dimensions[col_letter].width = 50                  # ✅ lebar kolom tiap foto
                ws.row_dimensions[row_num].height = 160
                foto_col += 1

        # Pusatkan teks baris tersebut
        for c in range(1, foto_col):
            ws.cell(row=row_num, column=c).alignment = Alignment(
                vertical="center", horizontal="center", wrap_text=True
            )

        row_num += 1

    # ==== Kolom teks utama ====
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
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

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor('#003876'))
    p.drawString(100, y, f"LAPORAN: {laporan.no_document}")
    y -= 30

    p.setFont("Helvetica", 12)
    p.setFillColor(HexColor('#000000'))
    p.drawString(100, y, "Lokasi: ")
    p.linkURL(f"https://www.google.com/maps?q={laporan.lokasi}", (150, y-2, 400, y+10))
    p.drawString(150, y, laporan.lokasi)
    y -= 20

    p.drawString(100, y, f"Nama Team Support: {laporan.nama_team_support}")
    y -= 20
    p.drawString(100, y, f"Tanggal Proses: {laporan.tanggal_proses.strftime('%d-%m-%Y %H:%M')}")
    y -= 40

    for kegiatan in kegiatan_list:
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(HexColor('#003876'))
        p.drawString(100, y, kegiatan.get_kegiatan_display_name())
        y -= 15
        p.setFont("Helvetica", 11)
        p.setFillColor(HexColor('#000000'))
        p.drawString(100, y, kegiatan.remark)
        y -= 20

        # Foto utama dari KegiatanLaporan
        if kegiatan.foto:
            img_path = os.path.join(settings.MEDIA_ROOT, str(kegiatan.foto))
            if os.path.exists(img_path):
                p.drawImage(img_path, 100, y-200, width=300, height=200)
                y -= 220

        # Foto tambahan dari KegiatanFoto
        for foto in kegiatan.foto_list.all():
            img_path = os.path.join(settings.MEDIA_ROOT, str(foto.foto))
            if os.path.exists(img_path):
                p.drawImage(img_path, 100, y-200, width=300, height=200)
                y -= 220

        y -= 20

        if y < 100:  # page break
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response


@login_required
def bulk_download_excel(request):
    user = request.user
    
    # Get filtered queryset
    if user.username == 'admin' and user.check_password('Mimin1234%'):
        laporan_queryset = Laporan.objects.all()
    else:
        laporan_queryset = Laporan.objects.filter(
            nama_team_support__iexact=user.username
        )
    
    # Apply date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date_parsed = parse_date(start_date)
            if start_date_parsed:
                laporan_queryset = laporan_queryset.filter(
                    tanggal_proses__date__gte=start_date_parsed
                )
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_parsed = parse_date(end_date)
            if end_date_parsed:
                laporan_queryset = laporan_queryset.filter(
                    tanggal_proses__date__lte=end_date_parsed
                )
        except ValueError:
            pass
    
    laporan_list = laporan_queryset.order_by('nama_team_support', '-tanggal_proses')
    
    if not laporan_list:
        response = HttpResponse("Tidak ada laporan untuk diunduh")
        return response

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Laporan Bulk"

    # Styling
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="003876", end_color="003876", fill_type="solid")
    title_font = Font(bold=True, size=16, color="E31E24")
    section_font = Font(bold=True, size=14, color="003876")
    
    # Main title
    ws.merge_cells('A1:G1')
    cell = ws['A1']
    cell.value = "LAPORAN KEGIATAN PERTAMINA"
    cell.font = title_font
    cell.alignment = Alignment(horizontal="center")
    
    # Date range info
    if start_date and end_date:
        ws.merge_cells('A2:G2')
        cell = ws['A2']
        cell.value = f"Periode: {start_date} s/d {end_date}"
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal="center")
        current_row = 4
    elif start_date:
        ws.merge_cells('A2:G2')
        cell = ws['A2']
        cell.value = f"Dari Tanggal: {start_date}"
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal="center")
        current_row = 4
    elif end_date:
        ws.merge_cells('A2:G2')
        cell = ws['A2']
        cell.value = f"Sampai Tanggal: {end_date}"
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal="center")
        current_row = 4
    else:
        current_row = 3

    # Group by team support
    grouped_laporan = {}
    for laporan in laporan_list:
        if laporan.nama_team_support not in grouped_laporan:
            grouped_laporan[laporan.nama_team_support] = []
        grouped_laporan[laporan.nama_team_support].append(laporan)

    for team_name, team_laporan in grouped_laporan.items():
        # Team section header
        ws.merge_cells(f'A{current_row}:G{current_row}')
        cell = ws[f'A{current_row}']
        cell.value = f"TEAM: {team_name.upper()}"
        cell.font = section_font
        cell.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
        current_row += 2

        # Headers
        headers = ["No Document", "Lokasi", "Tanggal", "Jenis Kegiatan", "Remark", "Foto", "Foto Tambahan"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", wrap_text=True)

        current_row += 1

        for laporan in team_laporan:
            kegiatan_list = laporan.kegiatan_list.all()
            laporan_start_row = current_row
            
            if kegiatan_list:
                for idx, kegiatan in enumerate(kegiatan_list):
                    ws.cell(row=current_row, column=1, value=laporan.no_document)
                    loc_cell = ws.cell(row=current_row, column=2, value=laporan.lokasi)
                    loc_cell.hyperlink = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(laporan.lokasi)}"
                    loc_cell.style = "Hyperlink"

                    ws.cell(row=current_row, column=3, value=laporan.tanggal_proses.strftime("%d-%m-%Y %H:%M"))
                    
                    # Kegiatan info
                    ws.cell(row=current_row, column=4, value=kegiatan.get_kegiatan_display_name())
                    ws.cell(row=current_row, column=5, value=kegiatan.remark)
                    
                    # Foto utama
                    if kegiatan.foto:
                        img_path = os.path.join(settings.MEDIA_ROOT, str(kegiatan.foto))
                        if os.path.exists(img_path):
                            img = XLImage(img_path)
                            img.width = 200
                            img.height = 150
                            ws.add_image(img, f"F{current_row}")
                            ws.row_dimensions[current_row].height = 120      # ✅ tinggi baris
                            for c_idx in range(1, 8):                        # ✅ teks tengah vertikal
                                ws.cell(row=current_row, column=c_idx).alignment = Alignment(
                                    vertical="center", horizontal="center", wrap_text=True
                                )

                    # Foto tambahan
                    for foto in kegiatan.foto_list.all():
                        img_path = os.path.join(settings.MEDIA_ROOT, str(foto.foto))
                        if os.path.exists(img_path):
                            img = XLImage(img_path)
                            img.width = 200
                            img.height = 150
                            ws.add_image(img, f"{get_column_letter(foto_col)}{current_row}")
                            ws.row_dimensions[current_row].height = 120      # ✅ set tinggi sama
                            foto_col += 1

                    current_row += 1
            else:
                # Laporan without kegiatan
                ws.cell(row=current_row, column=1, value=laporan.no_document)
                loc_cell = ws.cell(row=current_row, column=2, value=laporan.lokasi)
                loc_cell.hyperlink = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(laporan.lokasi)}"
                loc_cell.style = "Hyperlink"

                ws.cell(row=current_row, column=3, value=laporan.tanggal_proses.strftime("%d-%m-%Y %H:%M"))
                ws.cell(row=current_row, column=4, value="Tidak ada kegiatan")
                current_row += 1
            
            current_row += 1  # Space between laporan

        current_row += 2  # Space between teams

    # Adjust column widths
    column_widths = {'A': 20, 'B': 30, 'C': 18, 'D': 25, 'E': 40, 'F': 25, 'G': 25}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Generate filename
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"laporan_pertareport_{today_str}.xlsx"

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


@login_required
def bulk_download_pdf(request):
    from django.utils import timezone
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from django.http import HttpResponse
    from django.conf import settings
    import os
    from django.utils.dateparse import parse_date

    user = request.user

    # Ambil queryset sesuai user
    if user.username == 'admin' and user.check_password('Mimin1234%'):
        laporan_queryset = Laporan.objects.all()
    else:
        laporan_queryset = Laporan.objects.filter(
            nama_team_support__iexact=user.username
        )

    # Filter tanggal
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        try:
            sd = parse_date(start_date)
            if sd:
                laporan_queryset = laporan_queryset.filter(tanggal_proses__date__gte=sd)
        except ValueError:
            pass
    if end_date:
        try:
            ed = parse_date(end_date)
            if ed:
                laporan_queryset = laporan_queryset.filter(tanggal_proses__date__lte=ed)
        except ValueError:
            pass

    laporan_list = laporan_queryset.order_by('nama_team_support', '-tanggal_proses')
    if not laporan_list:
        return HttpResponse("Tidak ada laporan untuk diunduh")

    # === Nama file otomatis: laporan_pertareport_<tanggal_download>.pdf ===
    today_str = timezone.now().strftime('%Y-%m-%d')
    filename = f"laporan_pertareport_{today_str}.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=A4)

    # ====== Halaman Judul ======
    page_width, page_height = A4

    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(HexColor('#E31E24'))
    title1 = "LAPORAN KEGIATAN"
    title2 = "PERTAMINA"
    p.drawCentredString(page_width/2, 750, title1)
    p.drawCentredString(page_width/2, 720, title2)

    # Tambahkan periode bila ada filter
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor('#003876'))
    if start_date and end_date:
        p.drawCentredString(page_width/2, 670, f"Periode: {start_date} s/d {end_date}")
    elif start_date:
        p.drawCentredString(page_width/2, 670, f"Dari Tanggal: {start_date}")
    elif end_date:
        p.drawCentredString(page_width/2, 670, f"Sampai Tanggal: {end_date}")

    # Generated on
    p.setFont("Helvetica", 12)
    p.setFillColor(HexColor('#000000'))
    generated_text = f"Generated on: {timezone.now().strftime('%d-%m-%Y %H:%M')}"
    p.drawCentredString(page_width/2, 100, generated_text)

    # ====== Logo di tengah2 antara judul dan generated_on ======
    logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        # ukuran logo lebih besar
        logo_width = 220      # sebelumnya 120
        logo_height = 150     # sebelumnya 80

        # titik vertikal di tengah antara teks periode (~670) dan generated on (100)
        mid_y = (670 + 100) / 2
        p.drawImage(
            logo_path,
            (page_width - logo_width) / 2,      # center horizontal
            mid_y - (logo_height / 2),          # center vertical
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True,
            mask='auto'
        )

    p.showPage()


    # ====== Isi Laporan per Team ======
    grouped_laporan = {}
    for lap in laporan_list:
        grouped_laporan.setdefault(lap.nama_team_support, []).append(lap)

    for team_name, team_laporan in grouped_laporan.items():
        y = 800
        p.setFont("Helvetica-Bold", 18)
        p.setFillColor(HexColor('#003876'))
        p.drawString(50, y, f"TEAM: {team_name.upper()}")
        y -= 40

        for lap in team_laporan:
            if y < 200:
                p.showPage()
                y = 800
            p.setFont("Helvetica-Bold", 14)
            p.setFillColor(HexColor('#E31E24'))
            p.drawString(50, y, f"Laporan: {lap.no_document}")
            y -= 20

            p.setFont("Helvetica", 12)
            p.setFillColor(HexColor('#000000'))
            p.drawString(50, y, f"Lokasi: {lap.lokasi}")
            y -= 15
            p.drawString(50, y, f"Tanggal: {lap.tanggal_proses.strftime('%d-%m-%Y %H:%M')}")
            y -= 25

            kegiatan_list = lap.kegiatan_list.all()
            if kegiatan_list:
                for keg in kegiatan_list:
                    if y < 250:
                        p.showPage()
                        y = 800
                    p.setFont("Helvetica-Bold", 12)
                    p.setFillColor(HexColor('#003876'))
                    p.drawString(70, y, f"• {keg.get_kegiatan_display_name()}")
                    y -= 15
                    p.setFont("Helvetica", 11)
                    p.setFillColor(HexColor('#000000'))
                    p.drawString(70, y, f"Remark: {keg.remark}")
                    y -= 20

                    # Foto utama
                    if keg.foto:
                        img_path = os.path.join(settings.MEDIA_ROOT, str(keg.foto))
                        if os.path.exists(img_path):
                            if y < 220:
                                p.showPage()
                                y = 800
                            p.drawImage(img_path, 70, y-200, width=250, height=180)
                            y -= 220

                    # Foto tambahan
                    for foto in keg.foto_list.all():
                        img_path = os.path.join(settings.MEDIA_ROOT, str(foto.foto))
                        if os.path.exists(img_path):
                            if y < 220:
                                p.showPage()
                                y = 800
                            p.drawImage(img_path, 70, y-200, width=250, height=180)
                            y -= 220
                    y -= 10
            else:
                p.setFont("Helvetica-Oblique", 11)
                p.setFillColor(HexColor('#666666'))
                p.drawString(70, y, "Tidak ada kegiatan yang tercatat")
                y -= 20
            y -= 30

    p.save()
    return response


@csrf_exempt
def history_list_api(request):
    user = request.user if request.user.is_authenticated else None
    
    if user and user.username == 'admin' and user.check_password('Mimin1234%'):
        laporan_list = Laporan.objects.all().order_by('-tanggal_proses')
    elif user:
        laporan_list = Laporan.objects.filter(
            nama_team_support__iexact=user.username
        ).order_by('-tanggal_proses')
    else:
        laporan_list = Laporan.objects.all().order_by('-tanggal_proses')

    data = {
        "status": "success",
        "laporan_list": [
            {
                "id": laporan.id,
                "no_document": laporan.no_document,
                "lokasi": laporan.lokasi,
                "nama_team_support": laporan.nama_team_support,
                "tanggal_proses": laporan.tanggal_proses.strftime("%Y-%m-%d %H:%M:%S"),
                "kegiatan_list": [
                    {
                        "display_name": k.get_kegiatan_display_name(),
                        "remark": k.remark,
                        "foto": k.foto.url if k.foto else None,
                    }
                    for k in laporan.kegiatan_list.all()
                ],
            }
            for laporan in laporan_list
        ]
    }
    return JsonResponse(data, safe=False)