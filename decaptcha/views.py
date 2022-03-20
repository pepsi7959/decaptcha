import datetime
import json
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Partner, CaptchaUsage, CaptchaLog
from decaptcha.captcha_master import data
from datetime import date, datetime


@csrf_exempt
def decaptcha(request):
    response = {
        "status": "fail",
        "message": "ERROR",
        "data": None,
    }

    try:
        if request.method != "POST":
            response['message'] = 'ERROR_METHOD'
            return HttpResponse(json.dumps(response))

        if not request.body:
            response['message'] = 'ERROR_BODY'
            return HttpResponse(json.dumps(response))

        try:
            request_data = json.loads(request.body)
        except:
            response['message'] = 'ERROR_JSON'
            return HttpResponse(json.dumps(response))

        if 'name' not in request_data or not request_data['name']:
            response['message'] = 'ERROR_NAME'
            return HttpResponse(json.dumps(response))
        partner_name = request_data['name']

        if 'token' not in request_data or not request_data['token']:
            response['message'] = 'ERROR_TOKEN'
            return HttpResponse(json.dumps(response))
        partner_token = request_data['token']

        if 'image' not in request_data or not request_data['image']:
            response['message'] = 'ERROR_IMAGE'
            return HttpResponse(json.dumps(response))
        partner_image = request_data['image']

        try:
            partner = Partner.objects.filter(name=partner_name).filter(token=partner_token).get()
        except Partner.DoesNotExist:
            response['message'] = 'ERROR_CREDENTIAL'
            return HttpResponse(json.dumps(response))

        try:
            captcha_stat = CaptchaUsage.objects.filter(partner_id=partner.id).filter(using_date=date.today()).get()
        except CaptchaUsage.DoesNotExist:
            captcha_stat = CaptchaUsage(
                partner_id=partner.id,
                using_date=date.today(),
            )
            captcha_stat.save()

        try:
            image = data.decode_image(partner_image, settings.IMAGE_H, settings.IMAGE_W, settings.LABEL_LENGTH)
            x_data = data.split_image(image, settings.IMAGE_H, settings.IMAGE_W, settings.LABEL_LENGTH)
            y_preds = settings.TF_MODEL.predict(x_data)
            label = ''
            for y_pred in y_preds:
                label = label + data.onehot2number(y_pred, settings.LABELS)
        except:
            response['message'] = 'ERROR_CAPTCHA_DETECT'
            return HttpResponse(json.dumps(response))

        log = CaptchaLog(
            partner_id=partner.id,
            decode_value=label,
            image=str(partner_image),
        )
        log.save()

        CaptchaUsage.objects.filter(id=captcha_stat.id).update(using_count=F('using_count') + 1)
        CaptchaUsage.objects.filter(id=captcha_stat.id).update(updated_at=datetime.now())

        response['status'] = 'success'
        response['message'] = 'OK'
        response['data'] = {
            "id": log.id,
            "label": label,
        }
        return HttpResponse(json.dumps(response))
    except:
        response['message'] = 'UNKNOWN_ERROR'
        return HttpResponse(json.dumps(response))


@csrf_exempt
def feedback(request):
    response = {
        "status": "fail",
        "message": "ERROR",
        "data": None,
    }

    try:
        if request.method != "POST":
            response['message'] = 'ERROR_METHOD'
            return HttpResponse(json.dumps(response))

        if not request.body:
            response['message'] = 'ERROR_BODY'
            return HttpResponse(json.dumps(response))

        try:
            request_data = json.loads(request.body)
        except:
            response['message'] = 'ERROR_JSON'
            return HttpResponse(json.dumps(response))

        if 'name' not in request_data or not request_data['name']:
            response['message'] = 'ERROR_NAME'
            return HttpResponse(json.dumps(response))
        partner_name = request_data['name']

        if 'token' not in request_data or not request_data['token']:
            response['message'] = 'ERROR_TOKEN'
            return HttpResponse(json.dumps(response))
        partner_token = request_data['token']

        if 'id' not in request_data or not request_data['id']:
            response['message'] = 'ERROR_ID'
            return HttpResponse(json.dumps(response))
        image_id = int(request_data['id'])

        if 'status' not in request_data or not request_data['status']:
            response['message'] = 'ERROR_STATUS'
            return HttpResponse(json.dumps(response))
        status = int(request_data['status'])

        if status != 1 and status != 2:
            response['message'] = 'ERROR_STATUS_CODE'
            return HttpResponse(json.dumps(response))

        try:
            partner = Partner.objects.filter(name=partner_name).filter(token=partner_token).get()
        except Partner.DoesNotExist:
            response['message'] = 'ERROR_CREDENTIAL'
            return HttpResponse(json.dumps(response))

        try:
            log = CaptchaLog.objects.filter(partner_id=partner.id).filter(id=image_id).get()
        except CaptchaLog.DoesNotExist:
            response['message'] = 'ERROR_LOG_ID'
            return HttpResponse(json.dumps(response))

        if log.status != 0:
            response['message'] = 'ERROR_ALREADY_FEEDBACK_SET'
            return HttpResponse(json.dumps(response))

        log_id = log.id
        if status == 2:
            try:
                captcha_stat = CaptchaUsage.objects.filter(partner_id=partner.id).filter(using_date=date.today()).get()
                try:
                    CaptchaUsage.objects.filter(id=captcha_stat.id).update(using_count=F('using_count') - 1)
                    CaptchaUsage.objects.filter(id=captcha_stat.id).update(fail_count=F('fail_count') + 1)
                    CaptchaUsage.objects.filter(id=captcha_stat.id).update(updated_at=datetime.now())
                except:
                    # do nothing
                    captcha_stat.save()

            except CaptchaUsage.DoesNotExist:
                captcha_stat = CaptchaUsage(
                    partner_id=partner.id,
                    using_date=date.today(),
                )
                captcha_stat.save()
            log.status = status
            log.save()
        else:
            log.delete()
            # log.status = status
            # log.save()

        response['status'] = 'success'
        response['message'] = 'OK'
        response['data'] = {
            "id": log_id,
        }
        return HttpResponse(json.dumps(response))

    except:
        response['message'] = 'UNKNOWN_ERROR'
        return HttpResponse(json.dumps(response))
