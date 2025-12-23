from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': '아이디',
            'email': '이메일',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user