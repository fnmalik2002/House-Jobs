from datetime import datetime
import time
from django.http import HttpResponseRedirect, HttpResponse
# from django.http.request import HttpRequest
from django.template import loader
from django.shortcuts import render, get_object_or_404
# from django.urls import reverse
# from django.views import generic
from .models import JobPost, Payments
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models import Avg, Count, Min, Sum
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
from .forms import NewChildUserForm, NewJob
from django.shortcuts import redirect
import random

from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages


my_money_under_review_this_month = None
my_total_this_mont = None
unclaimed = None

def get_this_family_jobs(request):
    family_admin = None
    date_today = timezone.datetime.now()
    user_group = Group.objects.get(user = request.user)
    users_in_a_group = User.objects.filter(groups=user_group)
    for u in users_in_a_group:
        if u.is_staff:
            family_admin = u
    this_family_jobs = JobPost.objects.filter(job_creator=family_admin)
    return this_family_jobs


# Create your views here.
@login_required
def index(request):
    print("index - user is : ",request.user)
    user = User.objects.get(username = request.user)
    grps = request.user.groups.all()
    if len(grps) == 0:
        print("index - this user has no group")
        new_group = Group(name = request.user)
        new_group.save()
        user.groups.add(new_group)
    else:
        print("index - this user belongs to group", grps)
    user_group = Group.objects.get(user = request.user)
    print('user_group \n', user_group)
    
    users_in_a_group = User.objects.filter(groups=user_group)
    print('users in group \n',users_in_a_group )
    def job_creators(users_in_a_group):
        poster = None
        for u in users_in_a_group:
            job_list_1 = JobPost.objects.filter(job_creator = u).order_by('-id') 
            print (u, job_list_1, len(job_list_1))
            if len(job_list_1) > 0:
                print("job creator is", u.id)
                poster = u
                print(u)
                
            else:
                print('None')

        return poster
    date_today = timezone.datetime.now()            
    # print('current month :' , timezone.datetime.now().month)
    # print("Jobs on a specific date : ", JobPost.objects.filter(publish_date__month=date_today.month))
    this_family_jobs = JobPost.objects.filter(publish_date__month=date_today.month).filter(job_creator=job_creators(users_in_a_group))
    this_family_jobs_today = JobPost.objects.filter(publish_date__day=date_today.day).filter(job_creator=job_creators(users_in_a_group))
    
    print('this_family_jobs : ', this_family_jobs)
    
    if request.user.is_staff:
        print("I am a staff")
        my_jobs_under_review = this_family_jobs.filter(job_taker=user).filter(job_taken= True).filter(job_under_review= True).order_by('-id') 
        my_jobs_acceptably_done = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).order_by('-id')
        
        jobs_under_review = this_family_jobs.filter(job_taken= True).filter(job_under_review= True).order_by('-id') 
        jobs_acceptably_done = this_family_jobs.filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).filter(job_paid=False).order_by('-id')
        jobs_review_rejected_by_admin = this_family_jobs.filter(job_taken=True).filter(job_done=True).filter(job_rejected_by_admin = True).order_by('-id')
        my_jobs_review_rejected_by_admin = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=True).filter(job_rejected_by_admin = True).order_by('-id')
        jobs_paid = this_family_jobs.filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).filter(job_paid=True).order_by('-id')
        

        job_list = this_family_jobs.filter(job_taken= False).order_by('-id')
        job_gone = this_family_jobs.filter(job_taken= True).order_by('-id')
        my_unfinished_jobs = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=False).order_by('-id')
        all_unfinished_jobs = this_family_jobs.filter(job_taken=True).filter(job_done=False).order_by('-id')

        my_done_jobs = this_family_jobs.filter(job_taker=user).filter(job_done=True).order_by('-id')
        all_done_jobs = this_family_jobs.filter(job_taken=True).filter(job_done=True).order_by('-id')
        my_money_under_review_this_month = this_family_jobs.filter(job_taken=True).filter(job_under_review= True).filter(job_done=True).aggregate(Sum('job_price'))
        my_total_this_mont = this_family_jobs.filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).aggregate(Sum('job_price'))
        unclaimed = this_family_jobs.filter(job_taken= False).aggregate(Sum('job_price'))

    else:
        print("I am not a staff")
        my_jobs_under_review = this_family_jobs.filter(job_taker=user).filter(job_taken= True).filter(job_under_review= True).order_by('-id')
        my_jobs_acceptably_done = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).filter(job_paid=False).order_by('-id')
        jobs_under_review = this_family_jobs.filter(job_taken= True).filter(job_under_review= True).order_by('-id') 
        jobs_acceptably_done = this_family_jobs.filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).order_by('-id')
        jobs_paid = this_family_jobs.filter(job_taken=True).filter(job_taker=user).filter(job_done=True).filter(job_passed_review= True).filter(job_paid=True).order_by('-id')
        
        job_list = this_family_jobs_today.filter(job_taken= False).order_by('-id')         
        job_gone = this_family_jobs.filter(job_taken= True).order_by('-id')
        my_unfinished_jobs = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=False).order_by('-id')
        all_unfinished_jobs = this_family_jobs_today.filter(job_taken=True).filter(job_done=False).order_by('-id')
        my_done_jobs = this_family_jobs.filter(job_taker=user).filter(job_done=True).order_by('-id')
        all_done_jobs = this_family_jobs.filter(job_taken=True).filter(job_done=True).order_by('-id')
        
        my_money_under_review_this_month = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_under_review= True).filter(job_done=True).aggregate(Sum('job_price'))
        my_total_this_mont = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).aggregate(Sum('job_price'))
        unclaimed = this_family_jobs_today.filter(job_taken= False).aggregate(Sum('job_price'))
        my_jobs_review_rejected_by_admin = this_family_jobs.filter(job_taker=user).filter(job_taken=True).filter(job_done=True).filter(job_rejected_by_admin = True).order_by('-id')
        jobs_review_rejected_by_admin = this_family_jobs.filter(job_taken=True).filter(job_done=True).filter(job_rejected_by_admin = True).order_by('-id')

    
    template = loader.get_template('jobs/index.html')
    print("Money", my_money_under_review_this_month)
    
    if request.user == 'AnonymousUser':
        usr = "None"
    else:
        usr = request.user
    context = {
     'job_list': job_list,
     'job_gone' : job_gone,
     'my_unfinished_jobs' : my_unfinished_jobs,
     'my_done_jobs' : my_done_jobs,
     'user': usr,
     'my_money_under_review_this_month':my_money_under_review_this_month,
     'my_total_this_mont': my_total_this_mont,
     'unclaimed': unclaimed,
     'all_unfinished_jobs' : all_unfinished_jobs,
     'all_done_jobs' : all_done_jobs,
     'jobs_acceptably_done' : jobs_acceptably_done,
     'jobs_under_review' : jobs_under_review,
     'my_jobs_acceptably_done' : my_jobs_acceptably_done,
     'my_jobs_under_review' : my_jobs_under_review,
     'date_today' : timezone.datetime.now(),
     'jobs_review_rejected_by_admin' : jobs_review_rejected_by_admin,
     'my_jobs_review_rejected_by_admin' : my_jobs_review_rejected_by_admin,
     'jobs_paid' : jobs_paid,
     

     }
    return HttpResponse(template.render(context, request))


@login_required
def detail(request, pk):
    print(pk)
    detail = get_object_or_404(JobPost, pk=pk) 
    template = loader.get_template('jobs/detail.html')
    if request.user == 'AnonymousUser':
        usr = "None"
    else:
        usr = request.user
    context = {
    'detail': detail,
    'user': usr,
    # 'my_money_under_review_this_month': my_money_under_review_this_month,
    # 'unclaimed': unclaimed,
    # 'my_total_this_mont': my_total_this_mont,
     }
    return HttpResponse(template.render(context, request))

def payments(request):
    
    user = User.objects.get(username = request.user)
    
    print(request.user, user.id)
    # if request.user.is_superuser:       
    #     job_list = JobPost.objects.filter(job_taken= False).order_by('-id') 
    #     job_gone = JobPost.objects.filter(job_taken= True).order_by('-id')
    # else:
    #     job_list = JobPost.objects.filter(job_taker = user_id).order_by('-id') 
    #     job_gone = JobPost.objects.filter(job_taken= True).order_by('-id')
    try:
        pk=request.POST['Choice']
        print("choice id : ", pk)
        upd_rec = JobPost.objects.get(pk=pk)
        upd_rec.job_taken = True
        upd_rec.job_taken_date = timezone.now()
        upd_rec.job_taker = user
        upd_rec.save()
    except Exception as e:
        print(e)
        
    payment_list = JobPost.objects.filter(job_taken= True).filter(job_done= False).order_by('-id') 
    template = loader.get_template('jobs/payments.html')
    if request.user == 'AnonymousUser':
        usr = "None"
    else:
        usr = request.user
    context = {
    'payment_list': payment_list,
    'user': usr,
     }
    # return HttpResponse(template.render(context, request))
    return index(request)

def reset_password(request): 
    template = loader.get_template('registration/reset.html')
    context = { 
    'user': request.user,
     }
    return HttpResponse(template.render(context, request))

def review_done(request):
    pk=request.POST['Choice']
    print("choice id : ", pk)
    print(type(pk))
    if int(pk) > 0:
        upd_rec = JobPost.objects.get(pk=pk)
        upd_rec.job_under_review = False
        upd_rec.job_passed_review = True
        
        upd_rec.save()
    elif int(pk) < 0:
        pkid = str(-1*int(pk))
        print(type(pkid), pkid, "else statement in review jobs")
        
        try:
            upd_rec = JobPost.objects.get(pk=pkid)
            upd_rec.job_rejected_by_admin = True
            upd_rec.job_under_review = False
            upd_rec.save()
        except Exception as e:
            print(e)
            print('exception happened')
        

    return index(request) 

def mark_done(request):
    pk=request.POST['Choice']
    print("choice id : ", pk)
    print(type(pk))
    if int(pk) > 0:
        upd_rec = JobPost.objects.get(pk=pk)
        upd_rec.job_done = True
        upd_rec.job_under_review = True
        upd_rec.job_done_date = timezone.now()
        upd_rec.save()  
    elif int(pk) < 0:
        pkid = str(-1*int(pk))
        print(type(pkid), pkid, "else statement")
        
        try:
            upd_rec = JobPost.objects.get(pk=pkid)
            upd_rec.job_taken = False
            
            upd_rec.job_taker = User.objects.get(username = 'nouser')
            upd_rec.save()
        except Exception as e:
            print(e)
            print('exception happened')
    elif int(pk)==0:
        try:
            jobss = JobPost.objects.all()
            print(jobss)
            for job in jobss:
                print(job)
                job.job_taken = False
                job.job_done = False
                job.job_done_date = None
                job.job_taken_date = None
                job.job_under_review = False
                job.job_passed_review = False
                job.job_paid = False
                job.job_rejected_by_admin = False
                job.job_expired = False
                job.job_taker = User.objects.get(username = 'nouser')
                job.save()
        except Exception as e:
            print(e)
            print('exception happened')
    return index(request)

def mark_not_done(request):
    print("Not done selected")
    return index(request)

@login_required
def dashboard(request):
    date_today = timezone.datetime.now()
    job_list = get_this_family_jobs(request)
    
    unclaimed_this_day = get_this_family_jobs(request).filter(publish_date__day=date_today.day).filter(job_taken= False).aggregate(Sum('job_price'))  
    unclaimed_this_month = get_this_family_jobs(request).filter(publish_date__month=date_today.month).filter(job_taken= False).aggregate(Sum('job_price'))  
    unclaimed_this_year = get_this_family_jobs(request).filter(publish_date__year=date_today.year).filter(job_taken= False).aggregate(Sum('job_price'))  
      
    my_total_this_day = get_this_family_jobs(request).filter(publish_date__day=date_today.day).filter(job_taker=request.user).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).aggregate(Sum('job_price'))
    my_total_this_month = get_this_family_jobs(request).filter(publish_date__month=date_today.month).filter(job_taker=request.user).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).aggregate(Sum('job_price'))
    my_total_this_year = get_this_family_jobs(request).filter(publish_date__year=date_today.year).filter(job_taker=request.user).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).aggregate(Sum('job_price'))

    print("job = ", job_list)
    
    # def get_jobs_ready_for_payment_this_month(request):
    jobs = {}
    payments = {}
        
    user_group = Group.objects.get(user = request.user)
    users_in_a_group = User.objects.filter(groups=user_group)
    for u in users_in_a_group:
        payment_history = {}
        if u.is_staff:
            pass
        else:
            jobs[u] = get_this_family_jobs(request).filter(publish_date__month=date_today.month).filter(job_taker=u).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).filter(job_paid= False).aggregate(Sum('job_price'))
            payms = get_this_family_jobs(request).filter(job_taker=u).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).filter(job_paid= True)             
            for p in payms:
                p.job_payment_id.id
                    
                payment_history[p]= Payments.objects.get(id=p.job_payment_id.id)
            payments[u] = payment_history

        

    # print("Family jobs this month and year long payments  : ", jobs, payments)
    # for key, value in jobs.items():
    #     print("JOBS for this family children : ", key, value)
        
    for key, value in payments.items():
        
        print("PAYMENTS for this family children : ", value)
    # return jobs, payments



    template = loader.get_template('jobs/dashboard.html')
    context = { 
    'user': request.user,
    'date_today' : date_today,
    'unclaimed_this_day' : unclaimed_this_day,
    'unclaimed_this_month' : unclaimed_this_month,
    'unclaimed_this_year' : unclaimed_this_year,
    'my_total_this_day' : my_total_this_day,
    'my_total_this_month' : my_total_this_month,
    'my_total_this_year' : my_total_this_year,
    'job_list' : job_list,
    # 'jobs_ready_for_payment_this_month' : get_jobs_ready_for_payment_this_month(request).jobs,
    'jobs_ready_for_payment_this_month' : jobs,
    'payment_history' : payments,

     }
    return HttpResponse(template.render(context, request))
    
def new_job(request):
    if request.method == "POST":
        form = NewJob(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.job_creator = request.user
            post.save()
            return detail(request, pk=post.pk)
    else:
        form = NewJob()

    # print(form)
    
    date_today = timezone.datetime.now()
    print("New Job creation page loaded")
    template = loader.get_template('jobs/new_job.html')
    context = {
        'form': form,
        'date_today' : date_today,
     }
    return HttpResponse(template.render(context, request))

def repost_job(request, pk):
    date_today = timezone.datetime.now()
    print("JOB IS : ")
    this_job = JobPost.objects.get(id=pk)
    print("JOB IS : ", this_job.job_title, this_job.job_detail,this_job.job_price )

    reposted_job = JobPost(job_title = this_job.job_title, job_detail=this_job.job_detail, job_price=this_job.job_price, job_creator=request.user )
    reposted_job.save()

    
    date_today = timezone.datetime.now()
    print("New Job repost page loaded")
    template = loader.get_template('jobs/dashboard.html')
    context = {
        
        'date_today' : date_today,
     }
    # return HttpResponse(template.render(context, request))
    return dashboard(request)

def job_payments(request):
    print("job_payment is done")
    date_today = timezone.datetime.now()

    pk=request.POST['Choice']
    print("Payment choice id : ", pk)
    print(type(pk))

    this_kid = User.objects.get(id = pk)
    print("This Kid = ", this_kid)
    this_kid_jobs_to_be_paid_this_month = get_this_family_jobs(request).filter(publish_date__month=date_today.month).filter(job_taker=this_kid).filter(job_taken=True).filter(job_done=True).filter(job_passed_review= True).filter(job_paid= False)
    this_kid_total_payment_this_month = this_kid_jobs_to_be_paid_this_month.aggregate(Sum('job_price'))['job_price__sum']
    # print("this_kid_total_payment_this_month = ", this_kid_total_payment_this_month)
    
    n = random.randint(1000,1000000)
    uid = this_kid.first_name+"-"+str(date_today.month)+"-"+str(this_kid_total_payment_this_month)+"-"+str(n)
    print(uid)



    paid = Payments(payment_uid = uid, payment_amount = this_kid_total_payment_this_month, payment_note = "This is payment for all jobs this month for this kid")
    paid.save()
    
    time.sleep(1)
    pymnt = Payments.objects.get(payment_uid=uid)



    print(pymnt)
    print("This Kid Jobs This Month For Payment = ", this_kid_jobs_to_be_paid_this_month)
    for job in this_kid_jobs_to_be_paid_this_month:
        print(job)
        job.job_paid = True
        job.job_payment_id = pymnt
        job.save()
    

    template = loader.get_template('jobs/dashboard.html')
    context = {
        
        'date_today' : date_today,
        
     }
    # return HttpResponse(template.render(context, request))
    return dashboard(request)


def register(request):
    print("register clicked")
    print(request.user)
    if request.user.is_authenticated:
        print('user is not anonymous')
        user_groups = Group.objects.get(user = request.user)
        print("user group is : ", user_groups)
        if request.method == "POST":
            print("POST received")
            form = NewChildUserForm(request.POST)
            if form.is_valid():
                print("form is validated")
                user = form.save(user_groups)
                
                messages.success(request, "Registration successful." )
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Unsuccessful registration. Invalid information.")
        print("get form request received from admin dashboard")
        form = NewChildUserForm()
        return render (request=request, template_name="registration/register.html", context={"register_form":form})


    else:
        print('user is anonymous')
 
        if request.method == "POST":
            print("POST received")
            form = NewUserForm(request.POST)
            if form.is_valid():
                print("form is validated")
                user = form.save()
                messages.success(request, "Registration successful." )
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Unsuccessful registration. Invalid information.")
        print("get form request received from anonymous user")
        form = NewUserForm()
        return render (request=request, template_name="registration/register.html", context={"register_form":form})

def delete_job(request, pk):
    date_today = timezone.datetime.now()
    
    this_job = JobPost.objects.get(id=pk)
    print(this_job)
    print("JOB IS : ",this_job.id, this_job.job_title, this_job.job_detail, this_job.job_price )
    this_job.delete()
    return index(request)