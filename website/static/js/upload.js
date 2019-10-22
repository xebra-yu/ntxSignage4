

$(document).ready(function() {
    
    localStorage.index = 'upload';
    menuSelect(localStorage.index);
    
    fileviewChange(localStorage.upload);
});

function fileviewChange(check) {
    
    check = check || '';
    
    if(check == '') {
        if(localStorage.upload == "table") {
            localStorage.upload = "grid";
        } else if(localStorage.upload == "grid") {
            localStorage.upload = "table";
        } else {
            localStorage.upload = "table";
        }
    }
    
    if (localStorage.upload == "grid")
	{
		document.getElementById('tableview').style.display = 'none';
		document.getElementById('gridview').style.display = '';
        document.getElementById("myImg").src = '/static/img/ic-table.png';
	}
	else
	{
		document.getElementById('gridview').style.display = 'none';
		document.getElementById('tableview').style.display = '';
        document.getElementById("myImg").src = '/static/img/ic-gridview.png';
	}
}
        
function modify(name) {
    $('#modify_name').val(name);
    $('#file_name').val(name.substring(0, name.lastIndexOf(".")));
    $('#file_ext').text(name.substring(name.lastIndexOf(".")));
    $('#modFilename').modal('toggle');
}
        
function remove(name) {
    $('#remove_name').text(name);
    $('#remove_file').val(name);
    $('#remvFile').modal('toggle');
}

function fileUploadNew() {
    const realInput = document.getElementById('fileupload');
    realInput.click();
//	realInput.addEventListener('change', () => {
		

//	document.getElementById("upload_new_file").submit()
//  });
    realInput.addEventListener('change', () => {
        const name = realInput.value.split(/\\|\//).pop();
        const truncated = name.length > 20  ? name.substr(name.length - 20)  : name;
        
        fileInfo.innerHTML = truncated;
    });
}

function toggleFext(fext) {
	hideRows();
	showRow(fext);
	if (fext=='file')
		document.getElementById('file_type').innerHTML = '檔案類型';
	else if (fext=='filejpg')
		document.getElementById('file_type').innerHTML = 'JPG';
	else if (fext=='filepng')
		document.getElementById('file_type').innerHTML = 'PNG';
	else if (fext=='filebmp')
		document.getElementById('file_type').innerHTML = 'BMP';
	else if (fext=='filebin')
		document.getElementById('file_type').innerHTML = 'BIN';
	else if (fext=='filejson')
		document.getElementById('file_type').innerHTML = 'JSON';
}