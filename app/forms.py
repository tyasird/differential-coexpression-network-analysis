from django import forms
from .models import DiffCoExpression


class analyzeForm(forms.Form):
    status_hash = forms.CharField(label='Hash', required=True)
    healthy_sample = forms.IntegerField(label='Healthy Sample', required=True)
    input_excel = forms.FileField(label='Input', required=True)

    class Meta:
        model = DiffCoExpression
        exclude = ['disease_sample', 'pcritic_min', 'pcritic_max', 'healthy_normality_pvalue',
                   'disease_normality_pvalue', 'healthy_co_expression', 'disease_co_expression',
                   'healthy_diff_co_expression', 'disease_diff_co_expression', 'timestamp']
