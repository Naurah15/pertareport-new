from django.forms import ModelForm
from review.models import ReviewEntry

class ReviewEntryForm(ModelForm):
    class Meta:
        model = ReviewEntry
        fields = ["review_text"]