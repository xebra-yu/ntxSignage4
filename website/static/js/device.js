

$(document).ready(function() {
    
    localStorage.index = 'device';
    menuSelect(localStorage.index);
            
    $("#sel_file").change(function() {
        setJson('None');
    });
        
});

function modiDev(tag) {
    $('#modify_dev').text(tag.mac);
    $('#modify_mac').val(tag.mac);
    $('#dev_name').val(tag.name);
    setLevel(tag.level);
    $('#keeper').val(tag.owner);
    setJson(tag.json);

    /*
    serverUpload();
    document.getElementById('jsonfile').innerHTML = j;
    if(j == "None") {
        j = "";
    }
    document.getElementById('set_file_value').value = j;
    document.getElementById('set_lvl_value').value='2';
    document.getElementById('set_lvl').innerHTML='更新等級2';
    */
}

function setLevel(lv) {
    $('#set_lvl').text('更新等級' + lv);
    $('#set_lvl_value').val(lv);
}

function setJson(jn) {
    $('#set_file').text(jn);
    $('#json_drop').text(jn);
    $('#set_file_value').val(jn);
}

function remvMac(mac) {
    $('#remove_mac').text(mac);
    $('#clean_mac').val(mac);
}

function fileUpload() {
  var server_file = document.getElementById("server_file");
  server_file.style.display="none";
  const uploadButton = document.querySelector('.device-upload');
  const fileInfo = document.querySelector('.file-info');
  const realInput = document.getElementById('sel_file');

  // uploadButton.addEventListener('click', (e) => {
    realInput.click();
  // });

  realInput.addEventListener('change', () => {
    const name = realInput.value.split(/\\|\//).pop();
    const truncated = name.length > 20 ? name.substr(name.length - 20) : name;
    
    fileInfo.innerHTML = truncated;
  });
  document.getElementById("upload_txt").textContent="從裝置";
}

function serverUpload() {
  var server_file = document.getElementById("server_file");
  server_file.style.display="inline-block";
  document.getElementById("upload_txt").textContent="伺服器";
}

function toggleLi(select) {
	hideRows();
	showRow(select);
	if (select=='updatelevel') 
		document.getElementById('lvl_value').innerHTML = "更新等級";
	else if (select=='updatelevel0') 
		document.getElementById('lvl_value').innerHTML = "更新等級0";
	else if (select=='updatelevel1') 
		document.getElementById('lvl_value').innerHTML = "更新等級1";
	else if (select=='updatelevel2') 
		document.getElementById('lvl_value').innerHTML = "更新等級2";
}