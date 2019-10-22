

function openNav(){
  var btnOpenMenu = document.getElementById("topnav_btn_open_menu");
  btnOpenMenu.style.display = "none";
  var btnCloseMenu = document.getElementById("topnav_btn_close_menu");
  btnCloseMenu.style.display = "inline-block";
  var mySidenav = document.getElementById("menu");
  mySidenav.style.width = "200px";
}

function closeNav() {
  var btnOpenMenu = document.getElementById("topnav_btn_open_menu");
  btnOpenMenu.style.display = "inline-block";
  var btnCloseMenu = document.getElementById("topnav_btn_close_menu");
  btnCloseMenu.style.display = "none";
  var mySidenav = document.getElementById("menu");
  mySidenav.style.width = "0px";
}

function topNavSearchbarOpen(){
  var titleSearchClose = document.getElementById("topnav_btn_search_close");
  titleSearchClose.style.display = "block";

  var title_search_bar = document.getElementById("topnav_search");
  title_search_bar.style.display = "none";

  var titleSearchbar = document.getElementById("topnav_search_bar_container");
  titleSearchbar.style.display = "block";

  var search = document.getElementById("topnav_search_input_container");
  search.classList.add("search-input-container-after");

  var search_area = document.getElementById("topnav_search_input_container");
  var input = document.createElement("input");
  input.setAttribute("id","topnav_search_input");
  //input.setAttribute("onkeyup","TopNavSearchItem()");
  input.classList.add("topnav-search-input");
    
  input.addEventListener('input', function() {
    var search = $('#topnav_search_input').val().toUpperCase();
    searchTableItem(search);
  }, false);
  
  search_area.appendChild(input);
}

function topNavSearchbarClose(){
  var titleSearchbar = document.getElementById("topnav_search_bar_container");
  titleSearchbar.style.display = "none";

  var titleSearchClose = document.getElementById("topnav_btn_search_close");
  titleSearchClose.style.display = "none";

  var title_search_bar = document.getElementById("topnav_search");
  title_search_bar.style.display = "block";

  // var input = document.getElementById("topnav_search_input");
  document.getElementById("topnav_search_input").value = "";
  document.getElementById("topnav_search_input").remove();
  searchTableItem("");
}


// Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis
// Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis
// Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis Dennis

$(document).ready(function() {
    $('#search_input').on('input', function() {
        var search = $('#search_input').val().toUpperCase();
        searchTableItem(search);
    });
});
            
$(function(){
    jQuery('img.svg, img.table-svg').each(function() {
        var $img = jQuery(this);
        var imgID = $img.attr('id');
        var imgClass = $img.attr('class');
        var imgURL = $img.attr('src');
            
        jQuery.get(imgURL, function(data) {
            // Get the SVG tag, ignore the rest
            var $svg = jQuery(data).find('svg');
            
            // Add replaced image's ID to the new SVG
             if(typeof imgID !== 'undefined') {
                $svg = $svg.attr('id', imgID);
            }
            // Add replaced image's classes to the new SVG
            if(typeof imgClass !== 'undefined') {
                $svg = $svg.attr('class', imgClass+' replaced-svg');
            }
            
            // Remove any invalid XML tags as per http://validator.w3.org
            $svg = $svg.removeAttr('xmlns:a');
                    
            // Check if the viewport is set, else we gonna set it if we can.
            if(!$svg.attr('viewBox') && $svg.attr('height') && $svg.attr('width')) {
                $svg.attr('viewBox', '0 0 ' + $svg.attr('height') + ' ' + $svg.attr('width'))
            }
            
            // Replace image with new SVG
            $img.replaceWith($svg);
            
        }, 'xml');
            
    });
});

function searchBarOpen() {
    $('#search').addClass("search-input-container-after");
    $('#search_close').addClass("search-close-after");
    $('#search_input').removeClass("search-input-none");
}

function searchBarClose() {
    $('#search').removeClass("search-input-container-after");
    $('#search_close').removeClass("search-close-after");
    $('#search_input').addClass("search-input-none");
    $('#search_input').val("");
    searchTableItem("");
}

function searchTableItem(search) {
    tbody = document.getElementsByClassName("tbody")[0];
    tr = tbody.getElementsByClassName("tr");
    for(i = 0; i < tr.length; i++) {
        tr[i].style.display = "none";
        td = tr[i].getElementsByClassName("td");
        for (j = 0; j < td.length - 1; j++) {
            if(td[j].innerText.toUpperCase().indexOf(search) > -1) {
                tr[i].style.display = "";
            }
        }
    }
    
    if(localStorage.index == "upload") {
        searchGridItem(search);
    }
}

function searchGridItem(search) {
    tbody = document.getElementsByClassName("gridview")[0];
    tr = tbody.getElementsByClassName("myfile");
    for(i = 0; i < tr.length; i++) {
        tr[i].style.display = "none";
        td = tr[i].getElementsByClassName("img-line")[0];
        if(td.innerText.toUpperCase().indexOf(search) > -1) {
            tr[i].style.display = "";
        }
    }
}