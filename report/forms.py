from django import forms
from .models import Laporan, KegiatanLaporan, JenisKegiatan

class LaporanForm(forms.ModelForm):
    class Meta:
        model = Laporan
        fields = ['nama_team_support']
        widgets = {
            'nama_team_support': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama team support'
            })
        }

class KegiatanForm(forms.ModelForm):
    class Meta:
        model = KegiatanLaporan
        fields = ['kegiatan', 'kegiatan_other', 'remark', 'foto']
        widgets = {
            'kegiatan': forms.Select(attrs={
                'class': 'form-control kegiatan-select',
                'onchange': 'toggleOtherInput(this)'
            }),
            'kegiatan_other': forms.TextInput(attrs={
                'class': 'form-control other-input',
                'placeholder': 'Masukkan kegiatan lainnya',
                'style': 'display: none;'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Masukkan remark kegiatan'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pastikan ada opsi "Other" di database
        other_obj, created = JenisKegiatan.objects.get_or_create(
            nama='Other',
            defaults={'nama': 'Other'}
        )
        
        # Set queryset untuk kegiatan field agar include opsi "Other"
        self.fields['kegiatan'].queryset = JenisKegiatan.objects.all().order_by('nama')
        self.fields['kegiatan'].empty_label = "Pilih Jenis Kegiatan..."
    
    def clean(self):
        cleaned_data = super().clean()
        kegiatan = cleaned_data.get('kegiatan')
        kegiatan_other = cleaned_data.get('kegiatan_other')
        
        # Jika pilih "Other", maka kegiatan_other harus diisi
        if kegiatan and kegiatan.nama.lower() == 'other' and not kegiatan_other:
            raise forms.ValidationError('Mohon isi jenis kegiatan lainnya.')
        
        # Jika tidak pilih "Other", kosongkan kegiatan_other
        if kegiatan and kegiatan.nama.lower() != 'other':
            cleaned_data['kegiatan_other'] = ''
        
        return cleaned_data

# Formset untuk multiple kegiatan
KegiatanFormSet = forms.inlineformset_factory(
    Laporan,
    KegiatanLaporan,
    form=KegiatanForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class JenisKegiatanForm(forms.ModelForm):
    class Meta:
        model = JenisKegiatan
        fields = ['nama']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama kegiatan'
            })
        }