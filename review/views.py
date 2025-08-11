from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from report.models import Laporan

@login_required
def review_list(request):
    user = request.user

    # Admin bisa lihat semua laporan
    if user.username == 'admin' and user.check_password('Admin1234'):
        laporan_list = Laporan.objects.all().order_by('-tanggal_proses')
    else:
        laporan_list = Laporan.objects.filter(
            nama_team_support=user.username
        ).order_by('-tanggal_proses')

    return render(request, 'review_list.html', {
        'laporan_list': laporan_list
    })
