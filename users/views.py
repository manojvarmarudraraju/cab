from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import date
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib.sessions.backends.db import SessionStore
from selfdrive.models import *
from hiring.models import *
from  supervisor.models import *

def UserRegister(request):
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
            phone=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            firstname=request.POST['firstname']
            lastname=request.POST['lastname']
            dob=request.POST['dob']
            pincode=request.POST['pin']
            gender=request.POST['optradio']
            mobileno=request.POST['mobileno']
            email=request.POST['email']
            user=authenticate(username=phone,password=password)
            q = userdb(firstname=firstname, lastname=lastname, mobileno=mobileno,
                       birthdate=dob, email=email, pincode=pincode,gender=gender,
                        user_id=user.id)
            q.save()
            #subject = 'Thank You for Registration'
            #message = 'Welcome CivilRegistry of AMRITA_UNIVERSITY\t\t' + 'Username:' + phone + '\t\tPassword:' + password
            #from_mail = 'CivilRegistry of AMRITA_UNIVERSITY'
            #to_list = [email]
            #send_mail(subject, message, from_mail, to_list, fail_silently=True)
            login(request, user)
            return redirect('Userhome',foo='bar')
    else:
        form=UserForm()
    return render(request,'registerUser1.html',{'form':form})


def UserLogin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
            if admindb.objects.filter(mobileno=username).exists():
                return redirect('AdminLogin')
            elif userdb.objects.filter(mobileno=username).exists():
                login(request, user)
                return redirect('Userhome')
            elif Driverdb.objects.filter(mobileno=username).exists():
                return redirect('DriverLogin')

        else:
            return redirect('UserLogin')
    else:
        return render(request,'loginUser.html')


@login_required
def Userlogout(request):
    logout(request)
    return redirect(UserLogin)


@login_required
def UserDetailsView(request):

    phone = request.user.username
    n = userdb.objects.get(mobileno=phone)
    return render(request,'UserDetailsUpdation.html',{'n':n},{})

@login_required
def UpdateDetails(request):
    if request.method=='POST':
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        n.firstname = request.POST['firstname']
        n.lastname = request.POST['lastname']
        n.pincode = request.POST['pin']
        n.email = request.POST['email']
        n.save()
        return redirect('UserDetailsView')
    else:
        return HttpResponse('Details Updated')


@login_required
def Cartype(request):
    if request.method=='POST':
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        type=request.POST['type']
        if type=='selfdrive':
            return redirect('sviewcars')
        else:
            return redirect('hviewcars')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        return render(request,'test.html',{'n':n})


@login_required
def sviewcars(request):
    phone = request.user.username
    n = userdb.objects.get(mobileno=phone)
    q=SelfDriveCar.objects.filter(Cartype="sedan")
    w=SelfDriveCar.objects.filter(Cartype="micro")
    e=SelfDriveCar.objects.filter(Cartype="hatchback")
    r=SelfDriveCar.objects.filter(Cartype="suv")
    return render(request,'selfdrives.html',{'q':q,'w':w,'e':e,'r':r,'n':n})


@login_required
def hviewcars(request):
    phone = request.user.username
    n = userdb.objects.get(mobileno=phone)
    q = HiredCar.objects.filter(Cartype="sedan").filter(availability="yes")
    w = HiredCar.objects.filter(Cartype="micro").filter(availability="yes")
    e = HiredCar.objects.filter(Cartype="hatchback").filter(availability="yes")
    r = HiredCar.objects.filter(Cartype="suv").filter(availability="yes")
    return render(request, 'hiredrives.html',{'q':q,'w':w,'e':e,'r':r,'n':n} )


@login_required
def sbookcar(request,carid):
    if request.method=='POST':
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q=SelfDriveCar.objects.get(CarRegistration=carid)
        q.Status=1
        pickup=request.POST['address']
        date=request.POST['date']
        time=request.POST['time']
        days=request.POST['days']
        w=SelfBooking(Carid=carid,Userid=n.mobileno,pickup=pickup,bookingdate=timezone.now(),Days=days,time=date,ti=time)
        w.save()
        return redirect('Userhome')
    else:
        q = SelfDriveCar.objects.filter(CarRegistration=carid)
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
    return render(request,'selfbook.html',{'q':q,'n':n})


@login_required
def Userhome(request):
    phone = request.user.username
    n = userdb.objects.get(mobileno=phone)
    return render(request,'userhome.html',{'n':n})


@login_required
def hbookcar(request,registration):
    if request.method=="POST":
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        pickup=request.POST['pickup']
        date=request.POST['date']
        time=request.POST['time']
        q = HiredCar.objects.get(HcarRegistration=registration)
        q.status = 1
        q.save()
        e=drivercar.objects.get(car_id=registration)
        driverid=e.driver_id
        w=HiringCar(Driverid=driverid,Userid=n.mobileno,Date=date,Time=time,Pickup=pickup)
        w.save()
        return redirect('Userhome')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q = HiredCar.objects.filter(HcarRegistration=registration)
    return render(request,'hirebook.html',{'q':q,'n':n})


@login_required
def Selfviewbookings(request):
    phone = request.user.username
    n = userdb.objects.get(mobileno=phone)
    q=SelfBooking.objects.filter(Userid=phone).filter(status="upcoming")
    w=SelfBooking.objects.filter(Userid=phone).filter(status="completed").filter(rated=0)
    e = SelfBooking.objects.filter(Userid=phone).filter(status="completed").filter(rated=1)
    return render(request,'selfviewbookings.html',{'n':n,'q':q,'w':w,'e':e})


@login_required
def Hireviewbookings(request):
    phone = request.user.username
    n = userdb.objects.get(mobileno=phone)
    q=HiringCar.objects.filter(Userid=phone).filter(status="upcoming")
    w=HiringCar.objects.filter(Userid=phone).filter(status="completed").filter(rated=0)
    e = HiringCar.objects.filter(Userid=phone).filter(status="completed").filter(rated=1)
    return render(request,'hiringviewbookings.html',{'n':n,'q':q,'w':w,'e':e})


@login_required
def editselfbooking(request,bookid):
    if request.method=="POST":
        q = SelfBooking.objects.get(id=bookid)
        q.pickup = request.POST['address']
        q.time = request.POST['date']
        q.ti = request.POST['time']
        q.Days = request.POST['days']
        q.save()
        return redirect('Selfviewbookings')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q = SelfBooking.objects.get(id=bookid)
        return render(request,'editselfbooking.html',{'n':n,'q':q})


@login_required
def edithirebooking(request,bookid):
    if request.method=="POST":
        q=HiringCar.objects.get(id=bookid)
        q.Pickup=request.POST['address']
        q.time=request.POST['time']
        q.save()
        return redirect('Hireviewbookings')
    else:
        q = HiringCar.objects.get(id=bookid)
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        return render(request, 'edithirebooking.html', {'n': n,'q':q})


@login_required
def selfcancelbooking(request,bookid):
    if request.method=="POST":
        q=SelfBooking.objects.get(id=bookid)
        w=SelfCancelrepo(bookid=bookid,reason=request.POST['reason'],Carid=q.Carid,Userid=q.Userid,bookingdate=q.bookingdate)
        w.save()
        q.delete()
        return redirect('Selfviewbookings')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q = SelfBooking.objects.filter(id=bookid)
        return render(request, 'selfcancelbooking.html', {'n': n,'q':q})


@login_required
def hirecancelbooking(request,bookid):
    if request.method=="POST":
        q=HiringCar.objects.get(id=bookid)
        w=HireCancelrepo(bookid=bookid,reason=request.POST['reason'],Driverid=q.Driverid,Userid=q.Userid)
        w.save()
        q.delete()
        return redirect('Hireviewbookings')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q = HiringCar.objects.filter(id=bookid)
        return render(request, 'hirecancelbooking.html', {'n': n,'q':q})

@login_required
def selfcarrating(request,bookid):
    if request.method=="POST":
        q = SelfBooking.objects.get(id=bookid)
        q.ServiceRating=request.POST['servicerat']
        q.ServiceDesc=request.POST['servicedesc']
        q.CarRating=request.POST['carrating']
        q.CarDesc=request.POST['cardesc']
        q.rated=1
        q.save()
        return redirect('Selfviewbookings')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q = SelfBooking.objects.filter(id=bookid)
        return render(request, 'selfcarrating.html', {'n': n, 'q': q})


@login_required
def hirecarrating(request,bookid):
    if request.method=="POST":
        q = HiringCar.objects.get(id=bookid)
        q.DriverRating=request.POST['driverrating']
        q.DriverDesc=request.POST['driverdesc']
        q.ServiceRating = request.POST['servicerat']
        q.ServiceDesc = request.POST['servicedesc']
        q.rated=1
        q.save()
        return redirect('Hireviewbookings')
    else:
        phone = request.user.username
        n = userdb.objects.get(mobileno=phone)
        q = HiringCar.objects.filter(id=bookid)
        return render(request, 'hirecarrating.html', {'n': n, 'q': q})


@login_required
def contactus(request):
    return render(request,'contact.html')