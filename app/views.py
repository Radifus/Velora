from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.views.generic import CreateView
from app.form import RegisterForm, EmailLoginForm
from django.contrib.auth.views import LoginView

from app.models import User
from app.utils import generate_code, send_register_email


class IndexView(TemplateView):
    template_name = 'index.html'


class UserLoginView(LoginView):
    authentication_form = EmailLoginForm
    template_name = "login.html"
    redirect_authenticated_user = True


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        super().form_valid(form)

        user = self.object
        code = generate_code()

        # Kodni va Userni sessionda saqlaymiz
        self.request.session["verify_user_id"] = user.id
        self.request.session["verify_code"] = str(code)
        send_register_email(to_email=user.email, code=code)

        return redirect("confirm_password")



class VerifyEmailView(TemplateView):
    template_name = "confirm_password.html"

    def post(self, request, *args, **kwargs):
        if request.POST.get("code") != request.session.get("verify_code"):
            return redirect("verify-email")

        user = User.objects.get(id=request.session["verify_user_id"])
        user.is_active = True
        user.save()

        request.session.pop("verify_code", None)
        request.session.pop("verify_user_id", None)
        return redirect("login")


class ForgotPasswordView(TemplateView):
    template_name = 'parolni_tiklash.html'

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()
        if not user:
            return render(request, self.template_name,
                          {'error': 'Bunday foydalanuvchi topilmadi'})
        code = generate_code()
        request.session['reset_code'] = code
        request.session['reset_user_id'] = user.id
        send_register_email(user.email, code)
        return redirect('reset_password')


class ResetPasswordView(TemplateView):
    template_name = 'reset_password.html'

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if code != str(request.session.get('reset_code')):
            return render(request, self.template_name, {'error': 'Kod noto‘g‘ri'})
        if password != confirm_password:
            return render(request, self.template_name, {'error': 'Parollar bir xil emas'})
        user = User.objects.filter(id=request.session.get('reset_user_id')).first()
        if not user:
            return redirect('forgot-password')
        user.set_password(password)
        user.save()
        request.session.pop('reset_code', None)
        request.session.pop('reset_user_id', None)
        return redirect('login')
