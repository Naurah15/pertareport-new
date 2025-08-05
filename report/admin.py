from django.contrib import admin
from .models import Laporan, KegiatanLaporan

class KegiatanLaporanInline(admin.TabularInline):
    model = KegiatanLaporan
    extra = 1
    fields = ['kegiatan', 'kegiatan_other', 'remark', 'foto']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('laporan')

@admin.register(Laporan)
class LaporanAdmin(admin.ModelAdmin):
    list_display = ['no_document', 'nama_team_support', 'lokasi', 'tanggal_proses']
    list_filter = ['tanggal_proses']
    search_fields = ['no_document', 'nama_team_support', 'lokasi']
    readonly_fields = ['no_document', 'tanggal_proses']
    ordering = ['-tanggal_proses']
    
    inlines = [KegiatanLaporanInline]
    
    fieldsets = (
        ('Informasi Dokumen', {
            'fields': ('no_document', 'tanggal_proses')
        }),
        ('Detail Laporan', {
            'fields': ('nama_team_support', 'lokasi')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Bisa diatur sesuai kebutuhan permission
        return request.user.is_superuser

@admin.register(KegiatanLaporan)
class KegiatanLaporanAdmin(admin.ModelAdmin):
    list_display = ['laporan', 'get_kegiatan_display_name', 'remark_preview']
    list_filter = ['kegiatan', 'laporan__tanggal_proses']
    search_fields = ['laporan__no_document', 'remark', 'kegiatan_other']
    
    def remark_preview(self, obj):
        return obj.remark[:50] + '...' if len(obj.remark) > 50 else obj.remark
    remark_preview.short_description = 'Remark'
    
    def get_kegiatan_display_name(self, obj):
        return obj.get_kegiatan_display_name()
    get_kegiatan_display_name.short_description = 'Kegiatan'