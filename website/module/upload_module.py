from bitarray import bitarray
from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from website import models
from PIL import Image, ImageColor

import logging
import numpy as np
import os
import random
import string
import sys

logger = logging.getLogger(__name__)
# logger.error()

W = settings.IMG_WIDTH
H = settings.IMG_HEIGHT
width = settings.IMG_WIDTH
height = settings.IMG_HEIGHT
level = settings.IMG_LEVEL
ext = settings.BINARY_EXT
if level == 0:
    bit = 8
elif level == 1:
    bit = 1
elif level == 2:
    bit = 1
else:
    bit = 1
# bit = settings.IMG_BIT


# Create your views here.
def add(request, org):
    
    for upload in request.FILES.getlist('file'):
    
        err_files = []
        name = upload.name
        
        if name.upper().endswith('.JSON'):
            # upload json file
            jn = models.Json.objects.filter(archive__iexact='%s/%s' % (org, name), organization=org)
            if jn.count() > 0:
                messages.add_message(request, messages.INFO, '%s 已經存在' % (name))
                continue
            else:
                jn = models.Json(archive=upload, organization=org)
                jn.save()
                
        elif name.upper().endswith('.BMP') or name.upper().endswith('.JPG') or name.upper().endswith('.JPEG') or name.upper().endswith('.PNG'):
            # ImgToBin(upload, '', level, width, height, org)
            # upload image file
            img = models.Image.objects.filter(archive__iexact='%s/%s' % (org, name), organization=org)
            if img.count() > 0:
                messages.add_message(request, messages.INFO, '%s 已經存在' % (name))
                continue
            else:
                img = models.Image(archive='%s/%s' % (org, upload), organization=org)
                img.save()
                im = Image.open(upload)
                if im.size[0] != width or im.size[1] != height:
                    x = width / im.size[0]
                    y = height / im.size[1]
                    if x > y:
                        nim = im.resize((width, int(im.size[1] * x)))
                    else:
                        nim = im.resize((int(im.size[0] * y), height))
                                
                    im = nim.crop((0, 0, width, height))
                            
                im.save('%s%s/%s' % (settings.MEDIA_ROOT, org, name))
                
            # add Bin
            bin = models.Bin.objects.filter(archive__iexact='%s/%s%s' % (org, name, ext), organization=org)
            if bin.count() > 0:
                messages.add_message(request, messages.INFO, '%s 已經存在' % (name))
                continue
            else:
                bn = Image.open('%s%s/%s' % (settings.MEDIA_ROOT, org, name))
                pix = bn.load()

                raw = img_convert(pix, 2)
                
                thumb = thumb_nail(raw, org)
                
                if level == 2:
                    raw = memoryview(raw).tobytes()
                    logger.error(len(raw))
                    arrRle = np.zeros(int(W*H/4), np.uint8)
                    ss = rle_compress(raw, arrRle, int(W*H/4))
                    arrRle.resize(ss)
                    raw = arrRle
                    

                output = open('%s%s/%s%s' % (settings.MEDIA_ROOT, org, name, ext), "wb")
                output.write(raw)
                output.close()

                img = models.Image.objects.get(archive='%s/%s' % (org, name), organization=org)

                bin = models.Bin(archive='%s/%s%s' % (org, name, ext), organization=org, thumbnail=thumb)
                bin.save()

                img_bin, created = models.ImageBin.objects.get_or_create(
                    image = img,
                    bin = bin
                )

        elif name.upper().endswith(ext.upper()):
            # upload bin file
            if level == 2:
                raw = upload.read()
            else:
                raw = init_raw(upload.read())
                
            bin = models.Bin.objects.filter(archive__iexact='%s/%s' % (org, name), organization=org)
            if bin.count() > 0:
                messages.add_message(request, messages.INFO, '%s 已經存在' % (name))
                continue
            else:
                size = 0
                if bit == 1:
                    size = width * height * (settings.IMG_COLOR - 1)
                if bit == 8:
                    size = width * height

                if level == 2 and len(raw) < width * height * (settings.IMG_COLOR - 1):
                    arrRle = np.zeros(int(W*H/4), np.uint8)
                    try:
                        ss = rle_uncompress(raw, arrRle, len(raw))
                        arrRle.resize(ss)
                        arr = bitarray(endian='big')
                        arr.frombytes(arrRle.tostring())
                        raw = arr
                    except IndexError:
                        messages.add_message(request, messages.INFO, '%s 檔案大小錯誤' % (name))
                        continue
                    storage = get_messages(request)
                    msg_count = 0
                    for message in storage:
                        msg_count += 1
                
                if (bit == 1 and size%len(raw) == 0) or (bit == 8 and len(raw) == size):
                    if msg_count == 0:
                        logger.error(len(raw))
                        thumb = thumb_nail(raw, org)
                        bin = models.Bin(archive=upload, organization=org, thumbnail=thumb)
                        bin.save()
                else:
                    if msg_count == 0:
                        messages.add_message(request, messages.INFO, '%s 檔案大小錯誤' % (name))
                    continue
            
            # add Image
            img = models.Image.objects.filter(archive__iexact='%s/%s.png' % (org, name), organization=org)
            if img.count() > 0:
                messages.add_message(request, messages.INFO, '%s 已經存在' % (name))
                continue
            else:
                if bit == 1:
                    data = bytearray(width * height * (settings.IMG_COLOR - 1))
                    for index, i in enumerate(raw):
                        data[index] = 0xFF if i == 1 else 0x00
                if bit == 8:
                    data = np.array(raw)
                
                raw = data

                newImage = Image.new('RGB', (width,height), 'White')

                for h in range(height):
                    for w in range(width):
                        if bit == 1:
                            if raw[w+width*h] == 0:
                                newImage.putpixel((w,h), ImageColor.getcolor("black","RGB"))
                            if raw[w+width*(h+height)] == 0xFF:
                                newImage.putpixel((w,h), ImageColor.getcolor("red","RGB"))
                        if bit == 8:
                            if raw[w+width*h] == 0:
                                newImage.putpixel((w,h), ImageColor.getcolor("black","RGB"))
                            if raw[w+width*h] == 0x80:
                                newImage.putpixel((w,h), ImageColor.getcolor("red","RGB"))
                newImage.save('%s%s/%s.png' % (settings.MEDIA_ROOT, org, name))

                img = models.Image(archive='%s/%s.png' % (org, name), organization=org)
                img.save()

                bin = models.Bin.objects.get(archive='%s/%s' % (org, name), organization=org)
                img_bin, created = models.ImageBin.objects.get_or_create(
                    bin = bin,
                    image = img
                )

        else:
            messages.add_message(request, messages.INFO, '%s 檔案類型錯誤' % (name))
            
        """
        for err in err_files:
            messages.add_message(request, messages.INFO, '%s 已經存在' % (err))
        """


def modify(request, org):

    name = request.POST.get('file', '')
    extension = os.path.splitext(name)[1]
    rename = request.POST.get('file_name', '')
    os.chdir(settings.MEDIA_ROOT)
    os.rename('%s/%s' % (org, name), '%s/%s%s' % (org, rename, extension))
    
    if name.upper().endswith('.JSON'):
        try:
            json = models.Json.objects.get(archive='%s/%s' % (org, name), organization=org)
            json.archive.name = '%s/%s%s' % (org, rename, extension)
            json.save()
            messages.add_message(request, messages.SUCCESS, '修改檔案成功')
        except:
            messages.add_message(request, messages.INFO, '修改檔案失敗')
    elif name.upper().endswith('.BMP') or name.upper().endswith('.JPG') or name.upper().endswith('.JPEG') or name.upper().endswith('.PNG'):
        try:
            img = models.Image.objects.get(archive='%s/%s' % (org, name), organization=org)
            img.archive.name = '%s/%s%s' % (org, rename, extension)
            img.save()
            messages.add_message(request, messages.SUCCESS, '修改檔案成功')
        except:
            messages.add_message(request, messages.INFO, '修改檔案失敗')
    elif name.upper().endswith(ext.upper()):
        try:
            bin = models.Bin.objects.get(archive='%s/%s' % (org, name), organization=org)
            bin.archive.name = '%s/%s%s' % (org, rename, extension)
            bin.save()
            messages.add_message(request, messages.SUCCESS, '修改檔案成功')
        except:
            messages.add_message(request, messages.INFO, '修改檔案失敗')
 

def delete(request, org):

    name = request.POST.get('file', '')

    if name.upper().endswith('.JSON'):
        try:
            json = models.Json.objects.get(archive='%s/%s' % (org, name), organization=org)
            json.delete()
            messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
        except:
            messages.add_message(request, messages.INFO, '刪除檔案失敗')
    elif name.upper().endswith('.BMP') or name.upper().endswith('.JPG') or name.upper().endswith('.JPEG') or name.upper().endswith('.PNG'):
        try:
            img = models.Image.objects.get(archive='%s/%s' % (org, name), organization=org)
            img_bin = models.ImageBin.objects.get(image=img)
            img_bin.bin.thumbnail.delete()
            img_bin.bin.delete()
            img.delete()
            messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
        except models.ImageBin.DoesNotExist:
            img = models.Image.objects.get(archive='%s/%s' % (org, name), organization=org)
            img.delete()
            messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
        except:
            messages.add_message(request, messages.INFO, '刪除檔案失敗')
    elif name.upper().endswith(ext.upper()):
        try:
            bin = models.Bin.objects.get(archive='%s/%s' % (org, name), organization=org)
            img_bin = models.ImageBin.objects.get(bin=bin)
            img_bin.image.delete()
            bin.thumbnail.delete()
            bin.delete()
            messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
        except models.ImageBin.DoesNotExist:
            bin = models.Bin.objects.get(archive='%s/%s' % (org, name), organization=org)
            bin.delete()
            messages.add_message(request, messages.SUCCESS, '刪除檔案成功')
        except:
            messages.add_message(request, messages.INFO, '刪除檔案失敗')


def img_convert(pix, num):
    
    raw = init_raw(None)

    for h in range(height):
        for w in range(width):
            
            if len(pix[w, h]) == 3:
                r, g, b = pix[w, h]
            else:
                r, g, b, a = pix[w, h]

            if bit == 1:
                if num == 2:                
                    black = 0.3*r + 0.587*g + 0.114*b
                    if black < 0x90:
                        raw[w+h*width] = raw_color('bl')
                    else:
                        raw[w+h*width] = raw_color('wh')

                if num == 3:
                    if r > 0x80 and g < 0x80 and b < 0x80:
                        raw[w+h*width] = raw_color('re')
                    else:
                        raw[w+h*width] = raw_color('bl')
                        
            if bit == 8:
                if r > 0x80 and g < 0x80 and b < 0x80:
                    raw[w+h*width] = raw_color('re')
                else:
                    black = 0.3*r + 0.587*g + 0.114*b
                    if black < 0x90:
                        raw[w+h*width] = raw_color('bl')
                    else:
                        raw[w+h*width] = raw_color('wh')

    if bit == 1 and num < settings.IMG_COLOR:
        raw.extend(img_convert(pix, num + 1))
    
    return raw          


def init_raw(data):
    size = data or width * height
    if bit == 1:
        if data:
            raw = bitarray(endian='big')
            raw.frombytes(size)
        else:
            raw = bitarray(size)
    if bit == 8:
        raw = bytearray(size)
    return raw


def raw_color(color):
    if bit == 1:
        if color == 're':
            val = 1
        if color == 'wh':
            val = 1
        if color == 'bl':
            val = 0
    if bit == 8:
        if color == 're':
            val = 0x80
        if color == 'wh':
            val = 0xFF
        if color == 'bl':
            val = 0
    return val


def thumb_nail(raw, org):
    
    str = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    
    thumb = models.Thumbnail.objects.filter(archive__iexact='%s/%s.png' % (org, str), organization=org)
    if thumb.count() > 0:
        thumb_nail(raw)
    else:
        #raw = numpy.array(raw)

        newImage = Image.new('RGB', (width,height), 'White')
        
        for h in range(height):
            for w in range(width):
                if bit == 1:
                    if(raw[w+width*h] == 0):
                        newImage.putpixel((w,h), ImageColor.getcolor("black","RGB"))
                    if settings.IMG_COLOR == 3 and len(raw) == width * height * (settings.IMG_COLOR - 1):
                        if (raw[w+width*(h+height)] == 1):
                            newImage.putpixel((w,h), ImageColor.getcolor("red","RGB"))
                if bit == 8:
                    if(raw[w+width*h] == 0):
                        newImage.putpixel((w,h), ImageColor.getcolor("black","RGB"))
                    if(raw[w+width*h] == 128):
                        newImage.putpixel((w,h), ImageColor.getcolor("red","RGB"))
        newImage.save('%s%s/%s.png' % (settings.MEDIA_ROOT, org, str))

        thumb = models.Thumbnail(archive='%s/%s.png' % (org, str), organization=org)
        thumb.save()
        
        return thumb


def _RLE_WriteRep(outB, outpos, marker, symbol, count):
    idx = outpos
    if (count <= 3):
        if (symbol == marker):
            outB[idx] = marker
            idx += 1
            outB[idx] = count - 1
            idx += 1
        else:
            for i in range(count):
                outB[idx] = symbol
                idx += 1
    else:
        outB[idx] = marker
        idx += 1
        count -= 1
        if (count >= 128):
            outB[idx] = count >> 8 | 0x80
            idx += 1

        outB[idx] = count & 0xFF
        idx += 1
        outB[idx] = symbol
        idx += 1

    return idx


def _RLE_WriteNonRep(outB, outpos, marker, symbol):
    idx = outpos
    if (symbol == marker):
        outB[idx] = marker
        idx += 1
        outB[idx] = 0
        idx += 1
    else:
        outB[idx] = symbol
        idx += 1

    return idx


def rle_compress(inB, outB, insize):
    if (insize < 1):
        return 0;
        
    histogam = np.zeros(256, np.uint8)

    for i in range(insize):
        histogam[inB[i]] += 1    

    marker = 0

    for i in range(1,256):
        if (histogam[i] < histogam[marker]):
            marker = i

    outB[0]  = marker
    outpos = 1

    byte1 = inB[0]
    inpos = 1
    count = 1

    if (insize > 2):
        byte2 = inB[inpos]
        inpos +=1
        count = 2

        #while ((inpos < insize) or (count >=2)):
        while (1):
            if (byte1 == byte2):
                while ((inpos < insize) and (byte1 == byte2) and (count < 32768)):
                    byte2 = inB[inpos]
                    inpos += 1
                    count += 1

                if (byte1 == byte2):
                    outpos = _RLE_WriteRep(outB, outpos, marker, byte1, count)
                    if (inpos < insize):
                        byte1 = inB[inpos]
                        inpos += 1
                        count = 1
                    else:
                        count = 0
                else:
                    outpos = _RLE_WriteRep(outB, outpos, marker, byte1, count -1)
                    byte1 = byte2
                    count =1
            else:
                outpos = _RLE_WriteNonRep(outB, outpos, marker, byte1)
                byte1 = byte2
                count = 1

            if (inpos < insize):
                byte2 = inB[inpos]
                inpos += 1
                count = 2

            if ((inpos >= insize) and (count <2)):
                break;

    if (count == 1):
        _RLE_WriteNonRep(outB, outpos, marker, byte1)

    return outpos


def rle_uncompress(inB, outB, insize):

    if insize < 1:
        return 0

    inpos = 0
    marker = inB[ inpos ]
    inpos += 1

    outpos = 0
    while True:
        symbol = inB[ inpos ]
        inpos += 1
        if symbol == marker:
            count = inB[ inpos ]
            inpos += 1
            if count <= 2:
                for i in range(count+1):
                    outB[ outpos ] = marker
                    outpos += 1
            else:
                if count & 0x80:
                    count = ((count & 0x7f) << 8) + inB[ inpos ]
                    inpos += 1
                symbol = inB[ inpos ]
                inpos += 1
                for i in range(count+1):
                    outB[ outpos ] = symbol
                    outpos += 1
        else:
            outB[ outpos ] = symbol
            outpos += 1
            
        if inpos >= insize:
            break


"""
def CropImage(im, w, h):
    im = Image.open(im)
    imW = im.size[0]
    imH = im.size[1]
    if imW != w or imH != h:
        x = w / imW
        y = h / imH
        if x > y:
            nim = im.resize((w, int(imH * x)))
        else:
            nim = im.resize((int(imW * y), h))

        im = nim.crop((0, 0, w, h))
    return im


def ImgToBin(input, output, level, w, h, org):
    if os.path.isfile('{}{}/{}'.format(settings.MEDIA_ROOT, org, input.name)):
        messages.add_message(request, messages.INFO, '%s 已經存在' % (input.name))
    else:
        im = CropImage(input, w, h)
        pix = im.load()
        
        logger.error(os.stat('{}{}/{}'.format(settings.MEDIA_ROOT, org, '12.jpg.raw')).st_size)
    pass

def BinToImg(input, output, level, w, h):
    pass
"""


"""
def upload(request):
    name = '%s %s' % (request.user.first_name, request.user.last_name)
    organization = request.session['org']
    org = models.Organization.objects.get(name=organization)
    
    if request.method == 'POST' and request.session['permission'] == 'user':
    
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
                    """"""
                    # add ImageBin
                    try:
                        img = models.Image.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img_bin, created = models.ImageBin.objects.get_or_create(
                            image = img
                        )
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Add ImageBin fail')
                    """"""
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
                    """"""
                    # map Image and Bin
                    try:
                        img = models.Image.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        bin = models.Bin.objects.get(archive='%s/%s.bin' % (org, upload), organization=org)
                        img_bin = models.ImageBin.objects.get(image=img)
                        img_bin.bin = bin
                        img_bin.save()
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Map Image and Bin fail')
                    """"""
                        
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
                    """"""
                    # add ImageBin
                    try:
                        bin = models.Bin.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img_bin, created = models.ImageBin.objects.get_or_create(
                            bin = bin
                        )
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Add ImageBin fail')
                    """"""
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
                    """"""
                    # map Image and Bin
                    try:
                        bin = models.Bin.objects.get(archive='%s/%s' % (org, upload), organization=org)
                        img = models.Image.objects.get(archive='%s/%s.png' % (org, upload), organization=org)
                        img_bin = models.ImageBin.objects.get(bin=bin)
                        img_bin.image = img
                        img_bin.save()
                    except models.ImageBin.DoesNotExist:
                        messages.add_message(request, messages.INFO, 'Map Image and Bin fail')
                    """"""
                else:
                    messages.add_message(request, messages.INFO, '%s 檔案類型錯誤' % (upload))
                
                for err in err_files:
                    messages.add_message(request, messages.INFO, '%s 已經存在' % (err))


        if request.POST['func'] == 'modifyFile':
            if request.POST['file'].upper().endswith('.JSON'):
                try:
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename('%s/%s' % (org, request.POST['file']), '%s/%s.json' % (org, request.POST['file_name']))
                    json = models.Json.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    json.archive.name = '%s/%s.json' % (org, request.POST['file_name'])
                    json.save()
                    messages.add_message(request, messages.SUCCESS, '修改檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '修改檔案失敗')
            elif request.POST['file'].upper().endswith('.BMP') or request.POST['file'].upper().endswith('.JPG') or request.POST['file'].upper().endswith('.JPEG') or request.POST['file'].upper().endswith('.PNG'):
                try:
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename('%s/%s' % (org, request.POST['file']), '%s/%s%s' % (org, request.POST['file_name'], os.path.splitext(request.POST['file'])[1]))
                    img = models.Image.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    img.archive.name = '%s/%s%s' % (org, request.POST['file_name'], os.path.splitext(request.POST['file'])[1])
                    img.save()
                    messages.add_message(request, messages.SUCCESS, '修改檔案成功')
                    """"""
                    img_bin = models.ImageBin.objects.get(image=img)
                    img_bin.image.archive.name = '%s/%s%s' % (org, request.POST['name'], img.extension)
                    img_bin.bin.archive.name = '%s/%s%s.bin' % (org, request.POST['name'], img.extension)
                    img_bin.save()
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename(request.POST['file'], '%s/%s%s' % (org, request.POST['name'], img.extension))
                    os.rename('%s.bin' % (request.POST['file']), '%s/%s%s.bin' % (org, request.POST['name'], img.extension))
                    """"""
                except:
                    messages.add_message(request, messages.INFO, '修改檔案失敗')
            elif request.POST['file'].upper().endswith('.BIN'):
                try:
                    os.chdir(settings.MEDIA_ROOT)
                    os.rename('%s/%s' % (org, request.POST['file']), '%s/%s.bin' % (org, request.POST['file_name']))
                    bin = models.Bin.objects.get(archive='%s/%s' % (org, request.POST['file']), organization=org)
                    bin.archive.name = '%s/%s.bin' % (org, request.POST['file_name'])
                    bin.save()
                    messages.add_message(request, messages.SUCCESS, '修改檔案成功')
                except:
                    messages.add_message(request, messages.INFO, '修改檔案失敗')
    

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
                    
        return redirect('/upload')
    
    jsons = models.Json.objects.filter(organization=org)
    imgs = models.Image.objects.filter(organization=org)
    bins = models.Bin.objects.filter(organization=org)
    files = chain(jsons, imgs, bins)
    
    grids = []
    for bin in bins:
        img_bin = models.ImageBin.objects.get(bin=bin)
        grids.append({"name":bin.basename, "image":img_bin.image.archive, "dirname":bin.dirname})
    
    return render(request, 'upload.html', locals())
"""