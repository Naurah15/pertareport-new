from django import forms
from .models import Laporan, KegiatanLaporan

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