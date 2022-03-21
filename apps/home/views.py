# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
from datetime import date, timedelta

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

from decaptcha.models import CaptchaUsage, CaptchaLog


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def summary_day(request):
    context = {}
    table_data = []

    try:
        try:
            query_set = CaptchaUsage.objects.filter(created_at__gte=date.today() - timedelta(days=90)).order_by('partner_id').order_by('-using_date').all()
        except CaptchaUsage.DoesNotExist:
            html_template = loader.get_template('home/page-404.html')
            return HttpResponse(html_template.render(context, request))

        for x in query_set:
            table_data.append({
                "using_date": x.using_date,
                "partner_id": x.partner_id,
                "using_count": x.using_count,
                "fail_count": x.fail_count,
                "total": x.using_count + x.fail_count,
                "updated_at": x.updated_at,
            })

        html_template = loader.get_template('home/summary_day.html')
        return HttpResponse(html_template.render({'table_data': table_data}, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render({'error_msg': ''}, request))


@login_required(login_url="/login/")
def summary_month(request):
    context = {}
    table_data = []

    try:
        try:
            last3month = (date.today() - timedelta(90)).replace(day=1)
            cursor = connection.cursor()
            cursor.execute("SELECT DATE_FORMAT(using_date,'%Y-%m') as using_date, partner_id,SUM(using_count) as using_count,SUM(fail_count) as fail_count FROM decaptcha_captchausage WHERE DATE_FORMAT(using_date,'%Y-%m') >= '" + last3month.strftime("%Y-%m") + "' GROUP BY DATE_FORMAT(using_date,'%Y-%m'),partner_id ORDER BY DATE_FORMAT(using_date,'%Y-%m') desc,partner_id")
            raw_set = cursor.fetchall()
        except CaptchaUsage.DoesNotExist:
            html_template = loader.get_template('home/page-404.html')
            return HttpResponse(html_template.render(context, request))

        for x in raw_set:
            table_data.append({
                "using_date": x[0],
                "partner_id": x[1],
                "using_count": x[2],
                "fail_count": x[3],
                "total": x[2] + x[3],
            })

        html_template = loader.get_template('home/summary_month.html')
        return HttpResponse(html_template.render({'table_data': table_data}, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render({'error_msg': ''}, request))


@csrf_exempt
def trainer1(request):
    filled_count = 0
    if request.method == "POST":
        image_id = request.POST.get('image_id', '')
        captcha_value = request.POST.get('captcha_value', '')
        if image_id and captcha_value:
            try:
                image_id = int(image_id)
                CaptchaLog.objects.filter(id=image_id).update(train1=captcha_value)
            except:
                print("Waring: image {} not found, or update error".format(image_id))

    try:
        log = CaptchaLog.objects.filter(status=3, train1=None).order_by('id').first()
        try:
            filled_count = CaptchaLog.objects.filter(status=3, train1__isnull=False).count()
        except:
            pass
        if not log:
            return HttpResponse("Not Found")

        html_template = loader.get_template('home/trainer.html')
        return HttpResponse(html_template.render({'trainer_number': 1, 'img_value': log.image, 'old_value': log.decode_value, 'img_id': log.id, "filled_count": filled_count}, request))
    except Exception as e:
        return HttpResponse("Not Found:"+str(e))


@csrf_exempt
def trainer2(request):
    filled_count = 0
    if request.method == "POST":
        image_id = request.POST.get('image_id', '')
        captcha_value = request.POST.get('captcha_value', '')
        if image_id and captcha_value:
            try:
                image_id = int(image_id)
                CaptchaLog.objects.filter(id=image_id).update(train2=captcha_value)
            except:
                print("Waring: image {} not found, or update error".format(image_id))

    try:
        log = CaptchaLog.objects.filter(status=3, train2=None).order_by('id').first()
        try:
            filled_count = CaptchaLog.objects.filter(status=3, train2__isnull=False).count()
        except:
            pass
        if not log:
            return HttpResponse("Not Found")

        html_template = loader.get_template('home/trainer.html')
        return HttpResponse(html_template.render({'trainer_number': 2, 'img_value': log.image, 'old_value': log.decode_value, 'img_id': log.id, "filled_count": filled_count}, request))
    except Exception as e:
        return HttpResponse("Not Found:"+str(e))


@csrf_exempt
def trainer3(request):
    filled_count = 0
    if request.method == "POST":
        image_id = request.POST.get('image_id', '')
        captcha_value = request.POST.get('captcha_value', '')
        if image_id and captcha_value:
            try:
                image_id = int(image_id)
                CaptchaLog.objects.filter(id=image_id).update(train1=captcha_value)
            except:
                print("Waring: image {} not found, or update error".format(image_id))

    try:
        log = CaptchaLog.objects.filter(status=3, train1=None).order_by('id')[20:].first()
        try:
            filled_count = CaptchaLog.objects.filter(status=3, train1__isnull=False).count()
        except:
            pass
        if not log:
            return HttpResponse("Not Found")

        html_template = loader.get_template('home/trainer.html')
        return HttpResponse(html_template.render({'trainer_number': 1, 'img_value': log.image, 'old_value': log.decode_value, 'img_id': log.id, "filled_count": filled_count}, request))
    except Exception as e:
        return HttpResponse("Not Found:"+str(e))


@csrf_exempt
def trainer4(request):
    filled_count = 0
    if request.method == "POST":
        image_id = request.POST.get('image_id', '')
        captcha_value = request.POST.get('captcha_value', '')
        if image_id and captcha_value:
            try:
                image_id = int(image_id)
                CaptchaLog.objects.filter(id=image_id).update(train2=captcha_value)
            except:
                print("Waring: image {} not found, or update error".format(image_id))

    try:
        log = CaptchaLog.objects.filter(status=3, train2=None).order_by('id')[20:].first()
        try:
            filled_count = CaptchaLog.objects.filter(status=3, train2__isnull=False).count()
        except:
            pass
        if not log:
            return HttpResponse("Not Found")

        html_template = loader.get_template('home/trainer.html')
        return HttpResponse(html_template.render({'trainer_number': 2, 'img_value': log.image, 'old_value': log.decode_value, 'img_id': log.id, "filled_count": filled_count}, request))
    except Exception as e:
        return HttpResponse("Not Found:"+str(e))
