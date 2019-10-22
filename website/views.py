from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from itertools import chain
from . import models
from PIL import Image, ImageColor
from .module import device_module, upload_module

import json
import logging
import numpy
import os
logger = logging.getLogger(__name__)
# logger.error()

from django.views.decorators.csrf import csrf_exempt

width = settings.IMG_WIDTH
height = settings.IMG_HEIGHT
ext = settings.BINARY_EXT
bit = settings.IMG_BIT


# Create your views here.
@login_required(login_url='/login/')
def index(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']
    org = models.Organization.objects.get(name=organization)
    
    if request.method == 'POST' and request.session['permission'] == 'user':
        if request.POST['func'] == 'deleteTag':
            try:
                tag = models.Tag.objects.get(mac=request.POST['modify_mac'])
                tag.name = ''
                tag.level = 0
                tag.owner = ''
                tag.json = None
                tag.save()
                
            except models.TagOrg.DoesNotExist:
                messages.add_message(request, messages.INFO, '請選擇正確的裝置')
            except models.Tag.DoesNotExist:
                messages.add_message(request, messages.INFO, '請選擇正確的裝置')
        
        if request.POST['func'] == 'modifyDevice':
            ifile = ''
            if request.POST.get('jsonfile', '') == '':
                if 'jsonfile' in request.FILES:
                    upload = request.FILES['jsonfile']
                    if upload.name.upper().endswith('.JSON'):
                        try:
                            json = models.Json.objects.get(archive='%s/%s' % (org, upload), organization=org)
                            messages.add_message(request, messages.INFO, '%s 已經存在' % (upload.name))
                        except models.Json.DoesNotExist:
                            json = models.Json(archive=upload, organization=org)
                            json.save()
                            ifile = upload.name
                    else:
                        messages.add_message(request, messages.INFO, '%s 檔案類型錯誤' % (upload))
            else:
                ifile = request.POST['jsonfile']
            
            
            try:
                tag = models.Tag.objects.get(mac=request.POST['modify_mac'])
                tag_orgs = models.TagOrg.objects.get(tag=tag, organization=org)
                tag.name = request.POST['dev_name']
                tag.level = request.POST['level']
                tag.owner = request.POST['keeper']
                if ifile == '':
                    tag.json = None
                else:
                    json = models.Json.objects.get(archive='%s/%s' % (org, ifile), organization=org)
                    tag.json = json
                tag.save()
                
            except models.TagOrg.DoesNotExist:
                messages.add_message(request, messages.INFO, '請選擇正確的裝置')
            except models.Tag.DoesNotExist:
                messages.add_message(request, messages.INFO, '請選擇正確的裝置')
            
    
        if request.POST['func'] == 'addFile':
            for upload in request.FILES.getlist('file'):
                err_files = []
                if upload.name.upper().endswith('.JSON'):
                    try:
                        json = models.Json.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        err_files.append(upload.name)
                    except models.Json.DoesNotExist:
                        json = models.Json(archive=upload, organization=org)
                        json.save()
                elif upload.name.upper().endswith('.BMP') or upload.name.upper().endswith('.JPG') or upload.name.upper().endswith('.JPEG') or upload.name.upper().endswith('.PNG'):
                    width = 1200
                    height = 825
                    # upload image file
                    try:
                        img = models.Image.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        err_files.append(upload.name)
                    except models.Image.DoesNotExist:
                        im = Image.open(upload)
                        if im.size[0] != width or im.size[1] != height:
                            x = width / im.size[0]
                            y = height / im.size[1]
                            if x > y:
                                nim = im.resize((width, int(im.size[1] * x)))
                            else:
                                nim = im.resize((int(im.size[0] * y), height))
                                
                            im = nim.crop((0, 0, width, height))
                            
                        im.save('%s%s/%s' % (settings.MEDIA_ROOT, org, upload))
                        
                        img = models.Image(archive='%s/%s' % (org, upload), organization=org)
                        img.save()
                    """
                    # add ImageBin
                    try:
                        img = models.Image.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img_bin, created = models.ImageBin.objects.get_or_create(
                            image = img
                        )
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Add ImageBin fail')
                    """
                    # add Bin
                    try:
                        bin = models.Bin.objects.get(archive='%s/%s.bin' % (org, upload), organization=org)
                        err_files.append('%s.bin' % (upload))
                    except models.Bin.DoesNotExist:
                        bi = Image.open(upload)
                        pix = bi.load()
                        raw = bytearray(width * height)
                        for h in range(height):
                            for w in range(width):
                                r, g, b = pix[w, h]
                                if r > 0x80 and g < 0x80 and b < 0x80:
                                    raw[w+h*width] = 0x80
                                else:
                                    black = 0.3*r + 0.587*g + 0.114*b
                                    if black < 0x90:
                                        raw[w+h*width] = 0
                                    else:
                                        raw[w+h*width] = 0xFF
                                        
                        output = open('%s%s/%s.bin' % (settings.MEDIA_ROOT, org, upload), "wb")
                        output.write(raw)
                        output.close()
                        
                        bin = models.Bin(archive='%s/%s.bin' % (org, upload), organization=org)
                        bin.save()
                        
                        img = models.Image.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img_bin, created = models.ImageBin.objects.get_or_create(
                            image = img,
                            bin = bin
                        )
                    """
                    # map Image and Bin
                    try:
                        img = models.Image.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        bin = models.Bin.objects.get(archive='%s/%s.bin' % (org, upload), organization=org)
                        img_bin = models.ImageBin.objects.get(image=img)
                        img_bin.bin = bin
                        img_bin.save()
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Map Image and Bin fail')
                    """
                        
                elif upload.name.endswith('.bin'):
                    width = 1200
                    height = 825
                    raw = bytearray(upload.read())
                    # upload bin file
                    try:
                        bin = models.Bin.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        err_files.append(upload.name)
                    except models.Bin.DoesNotExist:
                        if len(raw) == width * height:
                            bin = models.Bin(archive=upload, organization=org)
                            bin.save()
                    """
                    # add ImageBin
                    try:
                        bin = models.Bin.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img_bin, created = models.ImageBin.objects.get_or_create(
                            bin = bin
                        )
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Add ImageBin fail')
                    """
                    # add Image
                    try:
                        img = models.Image.objects.get(archive='%s/%s.png' % (org, upload), organization=org)
                        err_files.append('%s.png' % (upload))
                    except models.Image.DoesNotExist:
                        raw = numpy.array(raw)
                        
                        newImage = Image.new('RGB', (width,height), 'White')

                        for h in range(height):
                            for w in range(width):
                                if(raw[w+width*h] == 0):
                                    newImage.putpixel((w,h), ImageColor.getcolor("black","RGB"))
                                if(raw[w+width*h] == 128):
                                    newImage.putpixel((w,h), ImageColor.getcolor("red","RGB"))
                        newImage.save('%s%s/%s.png' % (settings.MEDIA_ROOT, org, upload))
                        
                        img = models.Image(archive='%s/%s.png' % (org, upload), organization=org)
                        img.save()
                        
                        bin = models.Bin.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img_bin, created = models.ImageBin.objects.get_or_create(
                            bin = bin,
                            image = img
                        )
                    """
                    # map Image and Bin
                    try:
                        bin = models.Bin.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img = models.Image.objects.get(archive='%s/%s.png' % (org, upload), organization=org)
                        img_bin = models.ImageBin.objects.get(bin=bin)
                        img_bin.image = img
                        img_bin.save()
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Map Image and Bin fail')
                    """
                else:
                    messages.add_message(request, messages.INFO, '%s 檔案類型錯誤' % (upload))
                
                for err in err_files:
                    messages.add_message(request, messages.INFO, '%s 已經存在' % (err))
    

        if request.POST['func'] == 'deleteFile':
            if request.POST['file'].upper().endswith('.JSON'):
                try:
                    json = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    json.delete()
                    messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '刪除檔案失敗')
            elif request.POST['file'].upper().endswith('.BMP') or request.POST['file'].upper().endswith('.JPG') or request.POST['file'].upper().endswith('.JPEG') or request.POST['file'].upper().endswith('.PNG'):
                try:
                    img = models.Image.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    img_bin = models.ImageBin.objects.get(image=img)
                    img_bin.bin.delete()
                    img.delete()
                    messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
                except models.ImageBin.DoesNotExist:
                    img = models.Image.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    img.delete()
                    messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '刪除檔案失敗')
            elif request.POST['file'].upper().endswith('.BIN'):
                try:
                    bin = models.Bin.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    img_bin = models.ImageBin.objects.get(bin=bin)
                    img_bin.image.delete()
                    bin.delete()
                    messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
                except models.ImageBin.DoesNotExist:
                    bin = models.Bin.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    bin.delete()
                    messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '刪除檔案失敗')


        if request.POST['func'] == 'modifyFile':
            if request.POST['file'].upper().endswith('.JSON'):
                try:
                    json = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    json.archive.name = '%s/%s.json' % (org, request.POST['file_name'])
                    json.save()
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename(request.POST['file'], '%s/%s.json' % (org, request.POST['file_name']))
                    messages.add_message(request, messages.SUCCESS, '修改檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '修改檔案失敗')
            elif request.POST['file'].upper().endswith('.BMP') or request.POST['file'].upper().endswith('.JPG') or request.POST['file'].upper().endswith('.JPEG') or request.POST['file'].upper().endswith('.PNG'):
                try:
                    img = models.Image.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    img.archive.name = '%s/%s%s' % (org, request.POST['file_name'], os.path.splitext(request.POST['file'])[1])
                    img.save()
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename(request.POST['file'], '%s/%s%s' % (org, request.POST['file_name'], os.path.splitext(request.POST['file'])[1]))
                    messages.add_message(request, messages.SUCCESS, '修改檔案成功')
                    """
                    img_bin = models.ImageBin.objects.get(image=img)
                    img_bin.image.archive.name = '%s/%s%s' % (org, request.POST['name'], img.extension)
                    img_bin.bin.archive.name = '%s/%s%s.bin' % (org, request.POST['name'], img.extension)
                    img_bin.save()
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename(request.POST['file'], '%s/%s%s' % (org, request.POST['name'], img.extension))
                    os.rename('%s.bin' % (request.POST['file']), '%s/%s%s.bin' % (org, request.POST['name'], img.extension))
                    """
                except:
                    messages.add_message(request, messages.INFO, '修改檔案失敗')
            elif request.POST['file'].upper().endswith('.BIN'):
                try:
                    bin = models.Bin.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    bin.archive.name = '%s/%s.bin' % (org, request.POST['file_name'])
                    bin.save()
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename(request.POST['file'], '%s/%s.bin' % (org, request.POST['file_name']))
                    messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '刪除檔案失敗')

            
        return redirect('/')
    
    tag_orgs = models.TagOrg.objects.filter(organization=org)
    
    jsons = models.Json.objects.filter(organization=org)
    imgs = models.Image.objects.filter(organization=org)
    bins = models.Bin.objects.filter(organization=org)
    
    files = chain(jsons, imgs, bins)
    
    grids = []
    for bin in bins:
        img_bin = models.ImageBin.objects.get(bin=bin)
        grids.append({"name":bin.basename, "image":img_bin.image.archive})
    
    messages.get_messages(request)
    
    return render(request, 'device.html', locals())
    
    
@login_required(login_url='/login/')
def device_add(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']

    if request.method == 'POST' and request.session['permission'] == 'manager':
        if request.POST['func'] == 'addTag':
            obj, created = models.Tag.objects.get_or_create(
                mac = request.POST['mac']
            )
            if(created):
                tag_org, created = models.TagOrg.objects.get_or_create(
                    tag = obj
                )
                if(created):
                    messages.add_message(request, messages.SUCCESS, '新增裝置成功')
                    try:
                        org = models.Organization.objects.get(name=request.POST['organization'])
                        tag_org.organization = org
                        tag_org.save()
                    except models.Organization.DoesNotExist:
                        messages.add_message(request, messages.INFO, '請選擇正確的組織')
                else:
                    messages.add_message(request, messages.INFO, '裝置與組織配對失敗')
            else:
                messages.add_message(request, messages.INFO, '已經有相同的裝置： ', request.POST['mac'])
        
        elif request.POST['func'] == 'modifyTag':
            try:
                tag = models.Tag.objects.get(mac=request.POST['modify_mac'])
                org = models.Organization.objects.get(name=request.POST['mod_organization'])
                tag_org = models.TagOrg.objects.get(tag=tag)
                tag_org.organization = org
                tag_org.save()
            except:
                messages.add_message(request, messages.INFO, '修改裝置失敗')
                
        elif request.POST['func'] == 'deleteTag':
            try:
                tag = models.Tag.objects.get(mac=request.POST['modify_mac'])
                tag.delete()
                messages.add_message(request, messages.SUCCESS, '刪除裝置成功')
            except:
                messages.add_message(request, messages.INFO, '刪除裝置失敗')
                
        return redirect('/device_add')

    orgs = models.Organization.objects.all()
    tagorgs = models.TagOrg.objects.all()
    
    messages.get_messages(request)
    
    return render(request, 'device_add.html', locals())
    
    
@login_required(login_url='/login/')
def device(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']
    org = models.Organization.objects.get(name=organization)
    
    if request.method == 'POST' and request.session['permission'] == 'user':
    
        if request.POST['func'] == 'deleteTag':
            device_module.clean(request, org)
        
        if request.POST['func'] == 'modifyDevice':
            device_module.modify(request, org)
                
        return redirect('/device')
        
    tag_orgs = models.TagOrg.objects.filter(organization=org)
    jsons = models.Json.objects.filter(organization=org)
    bins = models.Bin.objects.filter(organization=org)
    
    return render(request, 'device.html', locals())
    
    
@login_required(login_url='/login/')
def upload(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']
    org = models.Organization.objects.get(name=organization)
    
    if request.method == 'POST' and request.session['permission'] == 'user':
    
        if request.POST['func'] == 'addFile':
            upload_module.add(request, org)
            

        if request.POST['func'] == 'modifyFile':
            upload_module.modify(request, org)
    

        if request.POST['func'] == 'deleteFile':
            upload_module.delete(request, org)
                    
        return redirect('/upload')
    
    jsons = models.Json.objects.filter(organization=org)
#    imgs = models.Image.objects.filter(organization=org)
    bins = models.Bin.objects.filter(organization=org)
    files = chain(jsons, bins)
    
    grids = []
    for bin in bins:
        img_bin = models.ImageBin.objects.get(bin=bin)
        grids.append({"name":bin.basename, "image":img_bin.bin.thumbnail.archive, "dirname":bin.dirname})
    
    return render(request, 'upload.html', locals())
    
    
@login_required(login_url='/login/')
def mgr_upload(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']
    org = models.Organization.objects.get(name=organization)
    
    if request.method == 'POST' and request.session['permission'] == 'manager':
        dirpath = "media/Manager/"
        if request.POST['func'] == 'addFile':
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            for upload in request.FILES.getlist('file'):
                newFilePath = '{}{}'.format(dirpath, upload)
                if not os.path.exists('{}{}'.format(dirpath, upload)):
                    with open(newFilePath, 'wb') as destination:
                        for chunk in upload.chunks():
                            destination.write(chunk)

        if request.POST['func'] == 'modifyFile':
            name = request.POST.get('file', '')
            extension = os.path.splitext(name)[1]
            rename = request.POST.get('file_name', '')
            os.rename('{}{}'.format(dirpath, name), '{}{}{}'.format(dirpath, rename, extension))

        if request.POST['func'] == 'deleteFile':
            os.remove('{}{}'.format(dirpath, request.POST['file']))
                    
        return redirect('/mgr_upload/')
    
    files = os.listdir('media/Manager')
    
    return render(request, 'mgr_upload.html', locals())
    
    
@login_required(login_url='/login/')
def template(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']
    org = models.Organization.objects.get(name=organization)
    
    if request.method == 'POST' and request.session['permission'] == 'user':
    
        if request.POST['func'] == 'addJson':
            os.chdir(settings.STATICFILES_DIRS[0] + "/layout")
            with open('layout_v2%s.json' % (settings.PRODUCT_MODEL), 'r') as f:
                data = json.load(f)
                data['field001']['param1'] = request.POST.get('receiver', '')
                data['field002']['param1'] = request.POST.get('dock_gate', '')
                data['field003']['param1'] = request.POST.get('net_weight', '')
                data['field004']['param1'] = request.POST.get('gross_weight', '')
                data['field005']['param1'] = request.POST.get('part_no1', '')
                data['field006']['param1'] = request.POST.get('part_no2', '')
                data['field007']['param1'] = request.POST.get('description', '')
                data['field008']['param1'] = request.POST.get('tel_qrcode', '')
                data['field009']['param1'] = request.POST.get('tel_num1', '') + '\r\n' + request.POST.get('tel_num2', '')
                data['field010']['param1'] = request.POST.get('fax_num1', '') + '\r\n' + request.POST.get('fax_num2', '')
                data['field011']['param1'] = request.POST.get('address_qrcode', '')
                #logger.error("test:" + request.POST['receiver'].replace("\n", "\n\r"))
                
                os.chdir(settings.MEDIA_ROOT)
                with open('%s/%s.json' % (org, request.POST['file_name']), 'w') as f:
                    json.dump(data, f, indent=4)
                """
                with open('%s/%s.json' % (org, request.POST['file_name']), 'w') as f:
                    f.write('ntx_layout_json:')
                    json.dump(data, f, indent=4)
                """
            try:
                jsonObj = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file_name'] + '.json'), organization=org)
                messages.add_message(request, messages.INFO, '新增JSON檔失敗')
            except models.Json.DoesNotExist:
                jsonObj = models.Json(archive='%s/%s' % (org, request.POST['file_name'] + '.json'), organization=org)
                jsonObj.save()
                messages.add_message(request, messages.SUCCESS, '新增JSON檔成功')
    
        if request.POST['func'] == 'modifyJson':
            """
            try:
                json = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file_name'] + '.json')), organization=org)
                #err_files.append(upload.name)
            except models.Json.DoesNotExist:
                json = models.Json(archive=upload, organization=org)
                json.save()
            """
            #logger.error('%s/%s.json' % (org, request.POST['file_name']))
            os.chdir(settings.MEDIA_ROOT)
            with open('%s/%s.json' % (org, request.POST['file_name']), 'r+') as f:
                data = json.load(f)
                #data = f.read()
                #logger.error(data.lstrip('ntx_layout_json:'))
                #data = json.loads(data.lstrip('ntx_layout_json:'))
                data['field001']['param1'] = request.POST.get('receiver', '')
                data['field002']['param1'] = request.POST.get('dock_gate', '')
                data['field003']['param1'] = request.POST.get('net_weight', '')
                data['field004']['param1'] = request.POST.get('gross_weight', '')
                data['field005']['param1'] = request.POST.get('part_no1', '')
                data['field006']['param1'] = request.POST.get('part_no2', '')
                data['field007']['param1'] = request.POST.get('description', '')
                data['field008']['param1'] = request.POST.get('tel_qrcode', '')
                data['field009']['param1'] = request.POST.get('tel_num1', '') + '\r\n' + request.POST.get('tel_num2', '')
                data['field010']['param1'] = request.POST.get('fax_num1', '') + '\r\n' + request.POST.get('fax_num2', '')
                data['field011']['param1'] = request.POST.get('address_qrcode', '')
                
                f.seek(0)
                # f.write('ntx_layout_json:')
                json.dump(data, f, indent=4)
                f.truncate()
                
            messages.add_message(request, messages.SUCCESS, '修改JSON檔成功')
            """
            try:
                jsonObj = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file_name'] + '.json'), organization=org)
                # err_files.append(json)
            except models.Json.DoesNotExist:
                jsonObj = models.Json(archive='%s/%s' % (org, request.POST['file_name'] + '.json'), organization=org)
                jsonObj.save()
            """
    
    if request.method == 'POST' and request.session['permission'] == 'user':
    
        if request.POST['func'] == 'addCHT':
            os.chdir(settings.STATICFILES_DIRS[0] + "/layout")
            with open('layout_cht%s.json' % (settings.PRODUCT_MODEL), 'r') as f:
                data = json.load(f)
                data['field001']['param1'] = request.POST.get('room_name', '')
                data['field002']['param1'] = request.POST.get('room1', '')
                data['field003']['param1'] = request.POST.get('recruiter1', '')
                data['field004']['param1'] = request.POST.get('room2', '')
                data['field005']['param1'] = request.POST.get('recruiter2', '')
                data['field006']['param1'] = request.POST.get('room3', '')
                data['field007']['param1'] = request.POST.get('recruiter3', '')
                data['field008']['param1'] = request.POST.get('room4', '')
                data['field009']['param1'] = request.POST.get('recruiter4', '')
                data['field010']['param1'] = request.POST.get('room5', '')
                data['field011']['param1'] = request.POST.get('recruiter5', '')
                
                os.chdir(settings.MEDIA_ROOT)
                with open('%s/%s.json' % (org, request.POST['file_name']), 'w') as f:
                    json.dump(data, f, indent=4)
            try:
                jsonObj = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file_name'] + '.json'), organization=org)
                messages.add_message(request, messages.INFO, '新增JSON檔失敗')
            except models.Json.DoesNotExist:
                jsonObj = models.Json(archive='%s/%s' % (org, request.POST['file_name'] + '.json'), organization=org)
                jsonObj.save()
                messages.add_message(request, messages.SUCCESS, '新增JSON檔成功')
            
        if request.POST['func'] == 'removeJson':
            try:
                jn = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                jn.delete()
                messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
            except:
                messages.add_message(request, messages.INFO, '刪除檔案失敗')
    
        if request.POST['func'] == 'modifyCHT':
            os.chdir(settings.MEDIA_ROOT)
            with open('%s/%s.json' % (org, request.POST['file_name']), 'r+') as f:
                data = json.load(f)
                data['field001']['param1'] = request.POST.get('room_name', '')
                data['field002']['param1'] = request.POST.get('room1', '')
                data['field003']['param1'] = request.POST.get('recruiter1', '')
                data['field004']['param1'] = request.POST.get('room2', '')
                data['field005']['param1'] = request.POST.get('recruiter2', '')
                data['field006']['param1'] = request.POST.get('room3', '')
                data['field007']['param1'] = request.POST.get('recruiter3', '')
                data['field008']['param1'] = request.POST.get('room4', '')
                data['field009']['param1'] = request.POST.get('recruiter4', '')
                data['field010']['param1'] = request.POST.get('room5', '')
                data['field011']['param1'] = request.POST.get('recruiter5', '')
                
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                
            messages.add_message(request, messages.SUCCESS, '修改JSON檔成功')
            
        return redirect('/template')
    
    jsons = models.Json.objects.filter(organization=org)
    imgs = models.Image.objects.filter(organization=org)
    bins = models.Bin.objects.filter(organization=org)
    files = chain(jsons, imgs, bins)
    
    return render(request, 'template.html', locals())
    
    
def login(request):
    messages = ''
        
    if request.method == 'POST' and messages == '':
    
        login_name = request.POST['username'].strip()
        login_password = request.POST['pwd']
        
        if login_name == '' and login_password == '':
            messages = '請輸入帳號與密碼。'
        elif login_name == '':
            messages = '請輸入帳號。'
        elif login_password == '':
            messages = '請輸入密碼。'
        else:
            pass
            
        if messages == '':
            user = auth.authenticate(username=login_name, password=login_password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    added = models.AddedUser.objects.get(user=user)
                    request.session['org'] = str( added.organization )
                    request.session['permission'] = str( added.permission )
                    if added.permission == 'user':
                        return redirect('/device')
                    if added.permission == 'manager':
                        return redirect('/device_add')
                else:
                    messages = '帳號不存在，請聯絡管理員。'
            else:
                messages = '請確認帳號或密碼。'

    return render(request, 'login.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def full_parameter(request):
    string = ''
    count = 0
    for para in request.POST:
        count += 1
        if count == 1:
            string = '?'
        if count > 1:
            string = '{}{}'.format(string, "&")
        string = '{}{}={}'.format(string, para, request.POST[para])
    
    return string

@csrf_exempt
def ntxcmd(request):
    logger.info('%s (%s) %s%s' % (
        datetime.today().strftime('[%Y-%m-%d %H:%M:%S]'),
        request.method,
        request.build_absolute_uri(),
        full_parameter(request)
    ))
    if 'mac' in request.POST:
        mac = request.POST['mac']
    if 'mac' in request.GET:
        mac = request.GET['mac']
    if 'updatelevel' in request.POST or 'updatelevel' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            tag_org = models.TagOrg.objects.get(tag=tag)
            """
            str.strip( '0' )
            with open('media/%s/%s' % (tag_org.organization, tag.json), 'r') as f:
                data = json.load(f)
            
            res = 'updatelevel=%s&json="%s://%s/media/%s/%s"' % (tag.level, request.scheme, request.get_host(), tag_org.organization, tag.tag_file)
            """
            if str(tag.tag_file).upper().endswith(ext.upper()):
                if settings.PRODUCT_MODEL != '':
                    leng = len(tag.tag_file.archive.read()) * 8 if bit == 1 else len(tag.tag_file.archive.read())
                    sett = width * height * (settings.IMG_COLOR - 1)
                    color = ( leng // sett ) + 2
                    return HttpResponse('%s&width="%s"&high="%s"&color="%s"&pix_bit="%s"' % (res, settings.IMG_WIDTH, settings.IMG_HEIGHT, color, settings.IMG_BIT))
                else:
                    with open(settings.STATICFILES_DIRS[0] + "/layout/layout_full_bg.json", 'r') as f:
                        data = json.load(f)
                        data['Layout']['BGImg']['Url'] = '%s://%s/media/%s/%s' % (request.scheme, request.get_host(), tag_org.organization, tag.tag_file)
                        data['Layout']['BGImg']['w'] = width
                        data['Layout']['BGImg']['h'] = height
                        data['Layout']['ImageCompressionMode'] = settings.IMG_LEVEL
                    return HttpResponse('updatelevel=%s&json=%s' % (tag.level, data))
            if str(tag.tag_file).upper().endswith('.JSON'):
                with open('media/%s/%s' % (tag_org.organization, tag.tag_file), 'r') as f:
                    data = f.read()

                res = 'updatelevel=%s&json=%s' % (tag.level, data)

                return HttpResponse(res)
            else:
                return HttpResponse('err')
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    if 'setkey' in request.POST or 'setkey' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            """
            if 'setkey' in request.POST:
                tag.level = request.POST['setkey']
            if 'setkey' in request.GET:
                tag.level = request.GET['setkey']
            tag.save()
            """
            return HttpResponse('ok')
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    if 'tagid' in request.POST or 'tagid' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            return HttpResponse('ok,group=%s' % (tag.level))
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    if 'power' in request.POST or 'power' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            if 'power' in request.POST:
                tag.power = request.POST['power']
            if 'power' in request.GET:
                tag.power = request.GET['power']
            tag.save()
            return HttpResponse('ok')
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    if 'mcuver' in request.POST and 'wifiver' in request.POST and 'tconver' in request.POST or 'mcuver' in request.GET and 'wifiver' in request.GET and 'tconver' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            if 'mcuver' in request.POST and 'wifiver' in request.POST and 'tconver' in request.POST:
                tag.mcuver = request.POST['mcuver']
                tag.wifiver = request.POST['wifiver']
                tag.tconver = request.POST['tconver']
            if 'mcuver' in request.GET and 'wifiver' in request.GET and 'tconver' in request.GET:
                tag.mcuver = request.GET['mcuver']
                tag.wifiver = request.GET['wifiver']
                tag.tconver = request.GET['tconver']
            tag.save()
            return HttpResponse('ok')
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    if 'updatecheck' in request.POST or 'updatecheck' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            return HttpResponse('updatecheck={}'.format(tag.level))
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    if 'unsetkey' in request.POST or 'unsetkey' in request.GET:
        try:
            tag = models.Tag.objects.get(mac=mac)
            return HttpResponse('ok')
        except models.Tag.DoesNotExist:
            return HttpResponse('err')

    return HttpResponse(None)


def showlog(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = BASE_DIR + "/log/" + datetime.today().strftime('%Y%m%d')
    text = ''
    if os.path.isfile(filepath):

        f = open(filepath, 'r')

        for line in f.readlines():
            text += line + '<br>'

        f.close()

    return HttpResponse(text)
