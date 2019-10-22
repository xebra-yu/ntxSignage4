

$(document).ready(function() {
    
    localStorage.index = 'template';
    menuSelect(localStorage.index);
    
    $('#newKLT').on('input', '#file_name', function() {
        inputFileNameCheck('#newKLT ', '#klt_dialog ');
    });
    
    $('#newCHT').on('input', '#file_name', function() {
        inputFileNameCheck('#newCHT ', '#cht_dialog ');
    });
    /*
    $('#modifyKLT #file_name').on('change', function() {
        inputFileNameCheck('#modifyKLT' + ' ');
    });
    */
    
    $("#klt_dialog").steps({
        headerTag: "h3",
        bodyTag: "section",
        onStepChanged: function (event, currentIndex, priorIndex) {
            
            if(currentIndex === 2)
            {
                $("#klt_dialog ul[role='menu'] li").eq(2).addClass("disabled");
                $("#klt_dialog ul[role='menu'] li").eq(2).children().attr("href", "#");
            }
        },
        onFinished: function() {
            $('form[name="newKLT"]').submit();
        }
    });
    
    $("#cht_dialog").steps({
        headerTag: "h3",
        bodyTag: "section",
        onStepChanged: function (event, currentIndex, priorIndex) {
            
            if(currentIndex === 1)
            {
                $("#cht_dialog ul[role='menu'] li").eq(2).addClass("disabled");
                $("#cht_dialog ul[role='menu'] li").eq(2).children().attr("href", "#");
            }
        },
        onFinished: function() {
            $('form[name="newCHT"]').submit();
        }
    });
    
});
    
function setLayout(layout) {
    $('#selectJson').modal('toggle');
    $('#' + layout).modal('toggle');
}

function removeFileName(fileName) {
    $('#json_name').text(fileName);
    $('#remove_json').val(fileName);
}

function inputFileNameCheck(modalId, dialog) {
        
    $(modalId + 'div.input-error-msg').addClass("msg-hidden");
    //$(modalId + 'div.dialog-footer button').attr("disabled", false);
    $(dialog + "ul[role='menu'] li").eq(2).removeClass("disabled");
    $(dialog + "ul[role='menu'] li").eq(2).children().attr("href", "#finish");
        
    var search = $(modalId + '#file_name').val().trim();
    
    if(search == "") {
        $(modalId + 'div.input-error-msg p').text("請輸入檔名");
        $(modalId + 'div.input-error-msg').removeClass("msg-hidden");
        //$(modalId + 'div.dialog-footer button').attr("disabled", true);
        $(dialog + "ul[role='menu'] li").eq(2).addClass("disabled");
        $(dialog + "ul[role='menu'] li").eq(2).children().attr("href", "#");
    } else {
        var search = $(modalId + '#file_name').val() + '.json';
        for(let jn of tableData) {
            if(jn.toUpperCase() == search.toUpperCase()) {
                $(modalId + 'div.input-error-msg p').text("檔案已經存在");
                $(modalId + 'div.input-error-msg').removeClass("msg-hidden");
                //$(modalId + 'div.dialog-footer button').attr("disabled", true);
                $(dialog + "ul[role='menu'] li").eq(2).addClass("disabled");
                $(dialog + "ul[role='menu'] li").eq(2).children().attr("href", "#");
            }
        }
    }
    
}

function modifyJson(url) {
    var href = location.href + '../' + url;
    var file = href.substring(href.lastIndexOf("/") + 1)
    var name = file.split(".")[0];
    $.getJSON(href, function(json) {
        if(json['layout-name'] == 'layout_v2' + PRODUCT_MODEL + '.json') {
            $('#modifyKLTLabel').text(file);
            $('form[name="modifyKLT"] input[name="file_name"]').val(name);
            $('form[name="modifyKLT"] textarea[name="receiver"]').val(json.field001.param1);
            $('form[name="modifyKLT"] input[name="dock_gate"]').val(json.field002.param1);
            $('form[name="modifyKLT"] input[name="net_weight"]').val(json.field003.param1);
            $('form[name="modifyKLT"] input[name="gross_weight"]').val(json.field004.param1);
            $('form[name="modifyKLT"] input[name="part_no1"]').val(json.field005.param1);
            $('form[name="modifyKLT"] input[name="part_no2"]').val(json.field006.param1);
            $('form[name="modifyKLT"] input[name="description"]').val(json.field007.param1);
            $('form[name="modifyKLT"] input[name="tel_qrcode"]').val(json.field008.param1);
            $('form[name="modifyKLT"] input[name="tel_num1"]').val(json.field009.param1.split('\r\n')[0]);
            $('form[name="modifyKLT"] input[name="tel_num2"]').val(json.field009.param1.split('\r\n')[1]);
            $('form[name="modifyKLT"] input[name="fax_num1"]').val(json.field010.param1.split('\r\n')[0]);
            $('form[name="modifyKLT"] input[name="fax_num2"]').val(json.field010.param1.split('\r\n')[1]);
            $('form[name="modifyKLT"] input[name="address_qrcode"]').val(json.field011.param1);
            $('#modifyKLT').modal('toggle');
        } else if(json['layout-name'] == 'layout_cht' + PRODUCT_MODEL + '.json') {
            $('#modifyCHTLabel').text(file);
            $('form[name="modifyCHT"] input[name="file_name"]').val(name);
            $('form[name="modifyCHT"] input[name="room_name"]').val(json.field001.param1);
            $('form[name="modifyCHT"] input[name="room1"]').val(json.field002.param1);
            $('form[name="modifyCHT"] input[name="recruiter1"]').val(json.field003.param1);
            $('form[name="modifyCHT"] input[name="room2"]').val(json.field004.param1);
            $('form[name="modifyCHT"] input[name="recruiter2"]').val(json.field005.param1);
            $('form[name="modifyCHT"] input[name="room3"]').val(json.field006.param1);
            $('form[name="modifyCHT"] input[name="recruiter3"]').val(json.field007.param1);
            $('form[name="modifyCHT"] input[name="room4"]').val(json.field008.param1);
            $('form[name="modifyCHT"] input[name="recruiter4"]').val(json.field009.param1);
            $('form[name="modifyCHT"] input[name="room5"]').val(json.field010.param1);
            $('form[name="modifyCHT"] input[name="recruiter5"]').val(json.field011.param1);
            $('#modifyCHT').modal('toggle');
        } else {
            $('#messageModal .modal-body.m-1').html('<div class="alert alert-info fade show">此檔案不符合模板的格式</div>');
            $('#messageModal').modal('toggle');
        }
    });
    /*
    var request = new XMLHttpRequest();
    request.open('GET', href, true);
    request.send(null);
    request.onreadystatechange = function () {
        if(request.readyState === 4 && request.status === 200) {
            var type = request.getResponseHeader('Content-Type');
            if(type.indexOf("text") !== 1) {
                var json = request.responseText;
                var str = 'ntx_layout_json:';
                if(json.search(str) != -1) {
                    json = JSON.parse(json.substring(str.length))
                } else {
                    json = JSON.parse(json)
                }

                //json.hasOwnProperty('layout-name') && 
                if(json['layout-name'] == 'layout_v2.json') { 
                    var name = href.substring(href.lastIndexOf("/") + 1).split(".")[0];
                    $('form[name="modifyKLT"] input[name="file_name"]').val(name);
                    $('form[name="modifyKLT"] textarea[name="receiver"]').val(json.field001.param1);
                    $('form[name="modifyKLT"] input[name="dock_gate"]').val(json.field002.param1);
                    $('form[name="modifyKLT"] input[name="net_weight"]').val(json.field003.param1);
                    $('form[name="modifyKLT"] input[name="gross_weight"]').val(json.field004.param1);
                    $('form[name="modifyKLT"] input[name="part_no1"]').val(json.field005.param1);
                    $('form[name="modifyKLT"] input[name="part_no2"]').val(json.field006.param1);
                    $('form[name="modifyKLT"] input[name="description"]').val(json.field007.param1);
                    $('form[name="modifyKLT"] input[name="tel_qrcode"]').val(json.field008.param1);
                    $('form[name="modifyKLT"] input[name="tel_num1"]').val(json.field009.param1.split('\r\n')[0]);
                    $('form[name="modifyKLT"] input[name="tel_num2"]').val(json.field009.param1.split('\r\n')[1]);
                    $('form[name="modifyKLT"] input[name="fax_num1"]').val(json.field010.param1.split('\r\n')[0]);
                    $('form[name="modifyKLT"] input[name="fax_num2"]').val(json.field010.param1.split('\r\n')[1]);
                    $('form[name="modifyKLT"] input[name="address_qrcode"]').val(json.field011.param1);
                    $('#modifyKLT').modal('toggle');
                } else {
                    $('#messageModal .modal-body.m-1').html('<div class="alert alert-info fade show">此檔案不符合模板的格式</div>');
                    $('#messageModal').modal('toggle');
                }
        
                //return request.responseText;
            }
        }
    }
    */
}