import json
from datetime import date
import os
from os import path
import base64

from django.conf import settings
from django.db import connection
from django.db.models import F
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from decaptcha.captcha_master import data
from .models import Partner, CaptchaUsage, CaptchaLog


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
        except Exception as e:
            response['message'] = 'ERROR_JSON:' + str(e)
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
            partner = Partner.objects.filter(name=partner_name).filter(token=partner_token).first()
        except Partner.DoesNotExist:
            response['message'] = 'ERROR_CREDENTIAL'
            return HttpResponse(json.dumps(response))
        except Exception as e:
            response['message'] = 'ERROR_CREDENTIAL:' + str(e)
            return HttpResponse(json.dumps(response))
        if not partner:
            response['message'] = 'ERROR_CREDENTIAL:NOT_FOUND'
            return HttpResponse(json.dumps(response))

        try:
            captcha_stat = CaptchaUsage.objects.filter(partner_id=partner.id).filter(using_date=date.today()).first()
        except CaptchaUsage.DoesNotExist:
            captcha_stat = CaptchaUsage(
                partner_id=partner.id,
                using_date=date.today(),
            )
            captcha_stat.save()
        except Exception as e:
            response['message'] = 'ERROR_USAGE:' + str(e)
            return HttpResponse(json.dumps(response))
        if not captcha_stat:
            captcha_stat = CaptchaUsage(
                partner_id=partner.id,
                using_date=date.today(),
            )
            captcha_stat.save()

        try:
            x_data = data.decode_image(partner_image, settings.IMAGE_H, settings.IMAGE_W, settings.LABEL_LENGTH)
            y_preds = settings.TF_MODEL.predict(x_data)
            label = ''
            for y_pred in y_preds:
                label = label + data.onehot2number(y_pred, settings.LABELS)
            if len(label) > settings.LABEL_LENGTH or len(label) < settings.LABEL_LENGTH - 1:
                response['message'] = 'ERROR_CAPTCHA_DETECT:DETECT_LENGTH_' + str(len(label))
                return HttpResponse(json.dumps(response))
        except Exception as e:
            response['message'] = 'ERROR_CAPTCHA_DETECT:' + str(e)
            return HttpResponse(json.dumps(response))

        log = CaptchaLog(
            partner_id=partner.id,
            decode_value=label,
            image=str(partner_image),
        )
        log.save()

        CaptchaUsage.objects.filter(id=captcha_stat.id).update(using_count=F('using_count') + 1, updated_at=timezone.now())

        response['status'] = 'success'
        response['message'] = 'OK'
        response['data'] = {
            "id": log.id,
            "label": label,
        }
        return HttpResponse(json.dumps(response))
    except Exception as e:
        response['message'] = 'UNKNOWN_ERROR:' + str(e)
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
        except Exception as e:
            response['message'] = 'ERROR_JSON:' + str(e)
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
            partner = Partner.objects.filter(name=partner_name).filter(token=partner_token).first()
        except Partner.DoesNotExist:
            response['message'] = 'ERROR_CREDENTIAL'
            return HttpResponse(json.dumps(response))
        except Exception as e:
            response['message'] = 'ERROR_CREDENTIAL:' + str(e)
            return HttpResponse(json.dumps(response))
        if not partner:
            response['message'] = 'ERROR_CREDENTIAL:NOT_FOUND'
            return HttpResponse(json.dumps(response))

        try:
            log = CaptchaLog.objects.filter(partner_id=partner.id).filter(id=image_id).first()
        except Exception as e:
            response['message'] = 'ERROR_LOG_ID:' + str(e)
            return HttpResponse(json.dumps(response))
        if not log:
            response['message'] = 'ERROR_LOG_ID:NOT_FOUND'
            return HttpResponse(json.dumps(response))

        if log.status != 0:
            response['message'] = 'ERROR_ALREADY_FEEDBACK_SET'
            return HttpResponse(json.dumps(response))

        log_id = log.id
        if status == 2:
            try:
                captcha_stat = CaptchaUsage.objects.filter(partner_id=partner.id).filter(using_date=date.today()).first()
                if not captcha_stat:
                    captcha_stat = CaptchaUsage(
                        partner_id=partner.id,
                        using_date=date.today(),
                    )
                    captcha_stat.save()
                else:
                    try:
                        CaptchaUsage.objects.filter(id=captcha_stat.id).update(using_count=F('using_count') - 1, fail_count=F('fail_count') + 1, updated_at=timezone.now())
                        cursor = connection.cursor()
                        cursor.execute("DELETE FROM decaptcha_captchalog WHERE status=0 AND created_at < DATE_ADD(NOW(), INTERVAL 6 HOUR)")
                    except:
                        # do nothing
                        pass
            except Exception as e:
                response['message'] = 'ERROR_USAGE:' + str(e)
                return HttpResponse(json.dumps(response))
            if not captcha_stat:
                captcha_stat = CaptchaUsage(
                    partner_id=partner.id,
                    using_date=date.today(),
                )
                captcha_stat.save()
            log.status = status
            log.save()
        else:
            log.delete()
            pass

        response['status'] = 'success'
        response['message'] = 'OK'
        response['data'] = {
            "id": log_id,
        }
        return HttpResponse(json.dumps(response))

    except Exception as e:
        response['message'] = 'UNKNOWN_ERROR:' + str(e)
        return HttpResponse(json.dumps(response))


@csrf_exempt
def get_train_image(request):
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
        except Exception as e:
            response['message'] = 'ERROR_JSON:' + str(e)
            return HttpResponse(json.dumps(response))

        if 'limit' not in request_data or not request_data['limit']:
            image_limit = 1000
        else:
            image_limit = int(request_data['limit'])

        try:
            images = CaptchaLog.objects.filter(status=3, train1__isnull=False, train2__isnull=False, train1=F('train2')).all().order_by('id')[:image_limit]
        except Exception as e:
            response['message'] = 'ERROR_GET_DB:' + str(e)
            return HttpResponse(json.dumps(response))

        img_dir = 'images'
        if not path.exists(img_dir):
            os.mkdir(img_dir)

        success_count = 0

        for image in images:
            if str(image.train1).find("l") >= 0:
                image.train1 = str(image.train1).replace("l", "I")
            img_path = img_dir + '/' + image.train1 + '.png'
            if not path.exists(img_path):
                try:
                    img_data = base64.b64decode(str(image.image))
                    fd = open(img_path, 'wb')
                    fd.write(img_data)
                    fd.close()

                    image.delete()
                    success_count += 1
                except Exception as e:
                    print("write file {} failed:{}".format(image.train1, str(e)))
            else:
                image.delete()

        response['status'] = 'success'
        response['message'] = 'OK'
        response['data'] = {
            "success": success_count,
        }
        return HttpResponse(json.dumps(response))

    except Exception as e:
        response['message'] = 'UNKNOWN_ERROR:' + str(e)
        return HttpResponse(json.dumps(response))
