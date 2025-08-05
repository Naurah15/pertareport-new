from django.db import models
from django.utils import timezone

class Laporan(models.Model):
    lokasi = models.CharField(max_length=200)  # Tag lokasi dari geo
    nama_team_support = models.CharField(max_length=200)
    tanggal_proses = models.DateTimeField(default=timezone.now)
    no_document = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        # Generate no_document otomatis
        if not self.no_document:
            now = timezone.now()
            prefix = f"PTPR{now.strftime('%y%m')}"
            last_laporan = Laporan.objects.filter(
                no_document__startswith=prefix
            ).order_by('-no_document').first()

            if last_laporan:
                last_number = int(last_laporan.no_document.split('-')[1])
                new_number = f"{last_number + 1:04d}"
            else:
                new_number = "0001"

            self.no_document = f"{prefix}-{new_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.no_document

class KegiatanLaporan(models.Model):
    KEGIATAN_CHOICES = [
        ('melayani_pengisian_bbm', 'Melayani pengisian BBM'),
        ('mengelola_transaksi', 'Mengelola transaksi'),
        ('menjaga_kebersihan_area_spbu', 'Menjaga kebersihan area SPBU'),
        ('memantau_stok', 'Memantau stok'),
        ('memperbaiki_kerusakan', 'Memperbaiki kerusakan'),
        ('other', 'Other'),
    ]
    
    laporan = models.ForeignKey(Laporan, on_delete=models.CASCADE, related_name='kegiatan_list')
    kegiatan = models.CharField(max_length=50, choices=KEGIATAN_CHOICES)
    kegiatan_other = models.CharField(max_length=200, blank=True, null=True)  # untuk custom kegiatan
    remark = models.TextField()
    foto = models.ImageField(upload_to='laporan_foto/', blank=True, null=True)
    
    def get_kegiatan_display_name(self):
        if self.kegiatan == 'other' and self.kegiatan_other:
            return self.kegiatan_other
        return self.get_kegiatan_display()

    def __str__(self):
        return f"{self.laporan.no_document} - {self.get_kegiatan_display_name()}"