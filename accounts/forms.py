from django import forms
<<<<<<< HEAD
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    # 이메일을 필수 항목으로 지정하고 싶을 때 추가 (선택사항)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        # username(ID), email 두 가지만 지정 (비밀번호 2개는 기본 포함됨)
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        # 닉네임을 입력받지 않으므로, 기본값을 아이디(username)로 설정해둡니다.
        if not user.nickname:
            user.nickname = user.username
=======
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
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
        if commit:
            user.save()
        return user