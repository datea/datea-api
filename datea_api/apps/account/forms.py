from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.models import get_current_site
from django.template import loader

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)
        #del self.fields['short_name']

    class Meta:
        model = User

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        #del self.fields['short_name']

    class Meta:
        model = User


class CustomPasswordResetForm(PasswordResetForm):

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, base_url = '', sitename_override=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """

        from django.core.mail import send_mail
        email = self.cleaned_data["email"]
        active_users = User.objects.filter(
            email__iexact=email, is_active=True)
        
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            f = open('/tmp/datea_errors.txt', 'w')
            f.write('hey')
            f.close()
            current_site = get_current_site(request)
            #if not user.has_usable_password():
            #    continue
            
            # don't send pass for superuser
            if user.is_superuser:
                continue
            if not sitename_override:
                site_name = current_site.name
            else:
                site_name = sitename_override

            if not domain_override:
                domain = current_site.domain
            else:
                domain = domain_override

            c = {
                'email': user.email,
                'base_url': base_url,
                'sitename': site_name,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])



