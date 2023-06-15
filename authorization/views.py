from django.views.decorators.csrf import csrf_protect, csrf_exempt
from gitdb.utils.encoding import force_text
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from main.tokens import generate_token
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from kyostudy import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from main.models import UsersInfo, Subjects, SubjectLists

# Create your views here.
username = ""
fn = ""
ln = ""
email = ""
passwd = ""


def signin(request):
    return render(request, 'authorization/signin.html')


def signup(request):
    return render(request, 'authorization/signup.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()

        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")

        return redirect('login')
    else:
        return render(request, 'activation_failed.html')


@csrf_protect
def signupaction(request):
    if request.method == "POST":
        username = request.POST['full_name']
        fname = request.POST['first_name']
        lname = request.POST['last_name']
        email = request.POST['your_email']
        pass1 = request.POST['password']
        pass2 = request.POST['confirm_password']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('registeraction')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('registeraction')

        if len(username) > 20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('registeraction')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('registeraction')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('registeraction')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        new_instance = UsersInfo(
            id=myuser,
            phone_number='+7 777 777 7777',
            birth_date='2023-06-02',
            avatar_img='https://cdn.vectorstock.com/i/preview-1x/28/35/male-person-avatar-businessman-portrait-flat-icon-vector-46692835.webp',

        )
        new_instance.save()
        messages.success(request,
                         "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")

        # Welcome Email
        subject = "Welcome to KyoStudy !!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to KyoStudy!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nKyoStudy developers team"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ KyoStudy - Django Login!!"
        message2 = render_to_string('authorization/email_confirmation.html', {

            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('login')

    return render(request, "authorization/signup.html")


@csrf_exempt
def signinaction(request):
    if request.method == 'POST':
        username = request.POST['full_name_1']
        pass1 = request.POST['password_1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            email = user.email
            username_for_instance = user.username
            pass1_for_instance = pass1
            UserObject = User.objects.get(email=email)
            id = UserObject.id
            request.session['fname'] = fname
            request.session['email'] = email
            request.session['user_id'] = id
            request.session['username_for_instance'] = username_for_instance
            request.session['pass1_for_instance'] = pass1_for_instance

            return redirect("/home", {
                'email': email,
                'fname': fname,
                'user_id': id,

            })

        else:
            messages.error(request, "Bad Credentials!!")
            return render(request, "authorization/signin.html")

    return render(request, "authorization/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('login')
