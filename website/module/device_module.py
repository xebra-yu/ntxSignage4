from django.conf import settings
from django.contrib import messages
from website import models

import logging
logger = logging.getLogger(__name__)
# logger.error()


ext = settings.BINARY_EXT


# Create your views here.
def modify(request, org):
    tfile = request.POST.get('tagfile', '')
    if tfile == 'None':
        if 'tagfile' in request.FILES:
            upload = request.FILES['tagfile']
            if upload.name.upper().endswith('.JSON'):
                jn = models.Json.objects.filter(archive__iexact='%s/%s' % (org, upload), organization=org)
                if jn.count() > 0:
                    messages.add_message(request, messages.INFO, '%s 已經存在' % (upload.name))
                else:
                    jn = models.Json(archive=upload, organization=org)
                    jn.save()
                    tfile = upload.name
            else:
                messages.add_message(request, messages.INFO, '%s 檔案類型錯誤' % (upload))  
            
    try:
        mac = request.POST.get('modify_mac', '')
        tagorg = models.TagOrg.objects.get(tag__mac=mac, organization = org)
        tagorg.tag.name = request.POST['dev_name']
        tagorg.tag.level = request.POST['level']
        tagorg.tag.owner = request.POST['keeper']
        """
        if jfile == 'None':
            tagorg.tag.json = None
        else:
            jn = models.Json.objects.get(archive='%s/%s' % (org, jfile), organization=org)
            tagorg.tag.json = jn
        """
        if tfile == 'None':
            tagorg.tag.tag_file = None
        else:
            if tfile.upper().endswith('.JSON'):
                jn = models.Json.objects.get(archive='%s/%s' % (org, tfile), organization=org)
                tagorg.tag.tag_file = jn
            if tfile.upper().endswith(ext.upper()):
                bn = models.Bin.objects.get(archive='%s/%s' % (org, tfile), organization=org)
                tagorg.tag.tag_file = bn
        tagorg.tag.save()
                
    except models.TagOrg.DoesNotExist:
        messages.add_message(request, messages.INFO, '請選擇正確的裝置')
 
 
def clean(request, org):
    mac = request.POST.get('clean_mac', '')
    if mac.strip() == '':
        messages.add_message(request, messages.INFO, '請選擇正確的裝置')
    else:
        try:
            tagorg = models.TagOrg.objects.get(tag__mac=mac, organization = org)
            tagorg.tag.name = ''
            tagorg.tag.level = 0
            tagorg.tag.owner = ''
            tagorg.tag.tag_file = None
            tagorg.tag.save()
        except models.TagOrg.DoesNotExist:
            messages.add_message(request, messages.INFO, '請選擇正確的裝置')
    

"""
def test(request):
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
                
        return redirect('/device')
        
    tag_orgs = models.TagOrg.objects.filter(organization=org)
    jsons = models.Json.objects.filter(organization=org)
    
    return render(request, 'device.html', locals())
"""