from django import forms
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
        if commit:
            user.save()
        return user