from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '이메일'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': '사용자명'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': '비밀번호'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': '비밀번호 확인'
        })


class ManualNumberForm(forms.Form):
    number_1 = forms.IntegerField(min_value=1, max_value=45, widget=forms.NumberInput(
        attrs={'class': 'form-control number-input', 'placeholder': '1~45', 'min': 1, 'max': 45}
    ))
    number_2 = forms.IntegerField(min_value=1, max_value=45, widget=forms.NumberInput(
        attrs={'class': 'form-control number-input', 'placeholder': '1~45', 'min': 1, 'max': 45}
    ))
    number_3 = forms.IntegerField(min_value=1, max_value=45, widget=forms.NumberInput(
        attrs={'class': 'form-control number-input', 'placeholder': '1~45', 'min': 1, 'max': 45}
    ))
    number_4 = forms.IntegerField(min_value=1, max_value=45, widget=forms.NumberInput(
        attrs={'class': 'form-control number-input', 'placeholder': '1~45', 'min': 1, 'max': 45}
    ))
    number_5 = forms.IntegerField(min_value=1, max_value=45, widget=forms.NumberInput(
        attrs={'class': 'form-control number-input', 'placeholder': '1~45', 'min': 1, 'max': 45}
    ))
    number_6 = forms.IntegerField(min_value=1, max_value=45, widget=forms.NumberInput(
        attrs={'class': 'form-control number-input', 'placeholder': '1~45', 'min': 1, 'max': 45}
    ))

    def clean(self):
        cleaned_data = super().clean()
        numbers = []
        for i in range(1, 7):
            num = cleaned_data.get(f'number_{i}')
            if num is not None:
                numbers.append(num)

        if len(numbers) == 6:
            # 중복 번호 체크
            if len(set(numbers)) != 6:
                raise ValidationError('중복된 번호가 있습니다. 서로 다른 6개의 번호를 선택해주세요.')

        return cleaned_data
