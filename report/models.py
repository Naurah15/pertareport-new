from django.db import models
from django.utils import timezone

class JenisKegiatan(models.Model):
    nama = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nama


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
    
    laporan = models.ForeignKey(Laporan, on_delete=models.CASCADE, related_name='kegiatan_list')
    kegiatan = models.ForeignKey(JenisKegiatan, on_delete=models.CASCADE)
    kegiatan_other = models.CharField(max_length=200, blank=True, null=True)  # untuk custom kegiatan
    remark = models.TextField()
    foto = models.ImageField(upload_to='laporan_foto/')
    
    def get_kegiatan_display_name(self):
        # Kalau user isi manual, pakai itu
        if self.kegiatan_other:
            return self.kegiatan_other
        # Kalau tidak, pakai nama dari dropdown
        return self.kegiatan.nama if self.kegiatan else ''
    
    def save(self, *args, **kwargs):
        if self.kegiatan_other and (not self.kegiatan or self.kegiatan.nama.lower() != 'other'):
            other_obj, _ = JenisKegiatan.objects.get_or_create(nama='Other')
            self.kegiatan = other_obj
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.laporan.no_document} - {self.get_kegiatan_display_name()}"
    

class KegiatanFoto(models.Model):
    kegiatan = models.ForeignKey(
        KegiatanLaporan,
        on_delete=models.CASCADE,
        related_name='foto_list'
    )
    foto = models.ImageField(upload_to='laporan_foto/')

    def __str__(self):
        return f"Foto untuk {self.kegiatan.get_kegiatan_display_name()}"

