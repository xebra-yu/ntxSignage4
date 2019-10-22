var PRODUCT_MODEL = '';

$(document).ready(function() {

    $('.tablesorter').click(function(event) {
        select = $('.tablesorter').index(this);
        $('.tablesorter').each(function(index, item) {
            if(select == index) {
                if(item.classList.contains('tablesorter-header')) {
                    item.classList.remove('tablesorter-header');
                    item.classList.add('tablesorter-headerAsc');
                    sortTable(select, "Asc");
                } else if(item.classList.contains('tablesorter-headerAsc')) {
                    item.classList.remove('tablesorter-headerAsc');
                    item.classList.add('tablesorter-headerDesc');
                    sortTable(select, "Desc");
                } else if(item.classList.contains('tablesorter-headerDesc')) {
                    item.classList.remove('tablesorter-headerDesc');
                    item.classList.add('tablesorter-headerAsc');
                    sortTable(select, "Asc");
                } else {
                
                }
            } else {
                item.classList.remove('tablesorter-headerAsc');
                item.classList.remove('tablesorter-headerDesc');
                item.classList.add('tablesorter-header');
            }
        });
    });
    
});

function sortTable(select, sorter) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementsByClassName("tableview")[0];
    switching = true;
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
        //start by saying: no switching is done:
        switching = false;
        //rows = table.rows;
        rows = table.getElementsByClassName("tr");
        /*Loop through all table rows (except the
        first, which contains table headers):*/
        for (i = 1; i < (rows.length - 1); i++) {
            //start by saying there should be no switching:
            shouldSwitch = false;
            /*Get the two elements you want to compare,
            one from current row and one from the next:*/
            x = rows[i].getElementsByClassName("td")[select];
            y = rows[i + 1].getElementsByClassName("td")[select];
            //check if the two rows should switch place:
            if ((x.innerHTML > y.innerHTML) && sorter == "Asc") {
                //if so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
            if ((x.innerHTML < y.innerHTML) && sorter == "Desc") {
                //if so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
          /*If a switch has been marked, make the switch
          and mark that a switch has been done:*/
          rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
          switching = true;
        }
    }
}

function menuSelect(check) {
    
    closeNav();
	switch (check) {
		case 'device':
            $('#device_menu').addClass("active");
			break;
		case 'upload':
            $('#upload_menu').addClass("active");
			break;
		case 'template':
            $('#template_menu').addClass("active");
            break;	
	}
	return false;
}

function hideRows() {
	let rows = document.getElementsByClassName("myfile");
	for (var row=0; row<rows.length; row++)
		if (rows[row].id != '')
			rows[row].style.display = 'none';

}

function showRow(id) {
	let rows = document.getElementsByClassName("myfile");
	for (var row=0; row<rows.length; row++)
		if (rows[row].id.includes(id))
			rows[row].style.display = '';
}

function copyStringToClipboard(str) {
   
    var clip_area = document.createElement('textarea');
    var href = location.href.slice(0, -1);
    clip_area.textContent = href.substring(0, href.lastIndexOf("/") + 1) + str;

    document.body.appendChild(clip_area);
    clip_area.select();
                
    document.execCommand('copy');
    clip_area.remove();
    $('#messageModal .modal-body.m-1').html('<div class="alert alert-success fade show">複製路徑到剪貼簿成功</div>');
    $('#messageModal').modal('toggle');
    
}
        
function loadingStart() {
	$.blockUI({
		message: 
			'<div class="sk-fading-circle">' +
				'<div class="sk-circle1 sk-circle"></div>' +
				'<div class="sk-circle2 sk-circle"></div>' +
				'<div class="sk-circle3 sk-circle"></div>' +
				'<div class="sk-circle4 sk-circle"></div>' +
				'<div class="sk-circle5 sk-circle"></div>' +
				'<div class="sk-circle6 sk-circle"></div>' +
				'<div class="sk-circle7 sk-circle"></div>' +
				'<div class="sk-circle8 sk-circle"></div>' +
				'<div class="sk-circle9 sk-circle"></div>' +
				'<div class="sk-circle10 sk-circle"></div>' +
				'<div class="sk-circle11 sk-circle"></div>' +
				'<div class="sk-circle12 sk-circle"></div>' +
			'</div>',
		css: { borderWidth: '0px', backgroundColor: 'transparent' },
	});
	//setTimeout($.unblockUI, 5000);
}

function loadingStop() {
    if(wifiStatusNow) {
        setTimeout($.unblockUI, 100);
    }
}