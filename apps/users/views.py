from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views.generic import View

from apps.users.models import User
from apps.roles.models import Role, UserRole
from .forms import UserCreateForm, UserEditForm, AdminPasswordChangeForm


def system_only(view):
    """Only system users can access"""
    @login_required(login_url='/admin/login/')
    def wrapped(request, *args, **kwargs):
        if request.user.user_type != 'system':
            return redirect('core:dashboard')
        return view(request, *args, **kwargs)
    return wrapped


@method_decorator(system_only, name='dispatch')
class UserListView(View):
    def get(self, request):
        search = request.GET.get('search', '')
        user_type = request.GET.get('user_type', '')

        users = User.objects.all().order_by('-date_joined')

        if search:
            users = users.filter(email__icontains=search) | \
                    users.filter(username__icontains=search)
        if user_type:
            users = users.filter(user_type=user_type)

        return render(request, 'users/index.html', {
            'users': users,
            'search': search,
            'user_type_filter': user_type,
            'total': User.objects.count(),
            'platform_count': User.objects.filter(user_type='platform').count(),
            'system_count': User.objects.filter(user_type='system').count(),
        })


@method_decorator(system_only, name='dispatch')
class UserCreateView(View):
    template_name = 'users/create.html'

    def get(self, request):
        return render(request, self.template_name, {'form': UserCreateForm()})

    def post(self, request):
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            if user.user_type == 'system':
                user.is_staff = True

            user.save()

            selected_roles = form.cleaned_data.get('roles', [])
            for role in selected_roles:
                UserRole.objects.get_or_create(user=user, role=role)

            messages.success(request, f"User '{user.username}' created successfully.")
            return redirect('users:index')

        return render(request, self.template_name, {'form': form})


@method_decorator(system_only, name='dispatch')
class UserEditView(View):
    template_name = 'users/edit.html'

    def get_user(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user = self.get_user(pk)
        # Current roles pre-select
        current_roles = Role.objects.filter(user_roles__user=user)
        form = UserEditForm(instance=user, initial={'roles': current_roles})
        return render(request, self.template_name, {'form': form, 'target_user': user})

    def post(self, request, pk):
        user = self.get_user(pk)
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if user.user_type == 'system':
                user.is_staff = True
            user.save()

            # Roles update - pehle sab hata do, phir naye lagao
            UserRole.objects.filter(user=user).delete()
            selected_roles = form.cleaned_data.get('roles', [])
            for role in selected_roles:
                UserRole.objects.create(user=user, role=role)

            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('users:index')

        return render(request, self.template_name, {'form': form, 'target_user': user})


@method_decorator(system_only, name='dispatch')
class UserDeleteView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        # Apne aap ko delete nahi kar sakta
        if user == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect('users:index')
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted.")
        return redirect('users:index')


@method_decorator(system_only, name='dispatch')
class UserToggleActiveView(View):
    """Quick toggle active/inactive"""
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, "You cannot deactivate yourself.")
            return redirect('users:index')
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User '{user.username}' {status}.")
        return redirect('users:index')


# @method_decorator(login_required(login_url='/admin/login/'), name='dispatch')
# class ChangePasswordView(View):
#     """Logged-in system user apna password change kare"""
#     template_name = 'users/change_password.html'

#     def get(self, request):
#         form = AdminPasswordChangeForm(user=request.user)
#         return render(request, self.template_name, {'form': form})

#     def post(self, request):
#         form = AdminPasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             request.user.set_password(form.cleaned_data['new_password'])
#             request.user.save()
#             # Session update - logout nahi hoga
#             update_session_auth_hash(request, request.user)
#             messages.success(request, "Password changed successfully.")
#             return redirect('core:admin_dashboard')
#         return render(request, self.template_name, {'form': form})