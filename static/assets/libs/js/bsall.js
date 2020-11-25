function nowdate() {
    let date = new Date();
    console.log(date.toISOString());
    return date.toISOString();
// console.log(date.toLocaleString());
// -> 2016. 10. 20. 오후 3:15:26
}

$('.bsingbtn').click(function () {
    bsname = $(this).attr('name');
    $.ajax({
        type: 'POST',
        url: 'bsingcheck',
        data: {bsname: bsname},
        success: function (re) {
            window.location.reload();
        }
    })
})

$('.bsingbtnreset').click(function () {
    bsname = $(this).attr('name');
    $.ajax({
        type: 'POST',
        url: 'bsingcheckreset',
        data: {bsname: bsname},
        success: function (re) {
            window.location.reload();
        }
    })
})

$('.bsdonebtn').click(function () {
    bsname = $(this).attr('name');
    ckname = $('input:text[name="' + bsname + '"]').val();
    ckbsing = $('.bsingbtn[name="' + bsname + '"]').val();
    /*if (!ckname) {
        alert('이름을 입력해주세요.');
    } 
    else */
    if (ckbsing == '미점검') {
        alert('점검 중의 미점검을 완료하세요.');
    } else {
        $.ajax({
            type: 'POST',
            url: 'bsdonecheck',
            data: {bsname: bsname, ckname: ckname, ckdate: nowdate()},
            success: function (re) {
                window.location.reload();
            }
        })
    }
})

$('.bsdonebtnreset').click(function () {
    bsname = $(this).attr('name');
    ckbsing = $('.bsingbtn[name="' + bsname + '"]').val();
    $.ajax({
        type: 'POST',
        url: 'bsdonecheckreset',
        data: {bsname: bsname},
        success: function (re) {
            window.location.reload();
        }
    })
})


function bdadd() {
    bdname = $('#bd-select1').val();
    if (bdname != '추가')
        return
    else {
        $('#bd-select1').prop('selectedIndex', 0);
        $("#bd-select1").hide()
        $('#editbtn1').hide()
        $('#delbtn1').hide()
        $('#addbtn1').show()
        $('#cancelbtn1').show()
        $('input[name=bdname]').show()
    }
}

function bsadd() {
    bsname = $('#bs-select1').val();
    if (bsname != '추가')
        return
    else {
        $('input[name=bsname]').val('');
        $('#bs-select1').prop('selectedIndex', 0);
        $("#bs-select1").hide()
        $('#editbtn2').hide()
        $('#delbtn2').hide()
        $('#addbtn2').show()
        $('#cancelbtn2').show()
        $('input[name=bsname]').show()
    }
}

function bdselected() {
    $('#bs-select1').empty();
    $('input[name=org_bdname2]').val($('#bd-select2').val())
    $('input[name=org_bdname2]').show()
    $('#cancelbtn2').show()
    $('#bd-select2').hide()
    let bdname = $('#bd-select2').val()
    $.ajax({
        type: 'POST',
        url: 'bs',
        data: {bdname: bdname},
        success: function (re) {
            if (re['BS'].length == 0) {
                $('#bs-select1').append('<option selected disabled>추가</option>' +
                    '<option>추가</option>')
            } else {
                for (let i = 0; i < re['BS'].length; i++) {
                    let tmpHtml = `<option>${re['BS'][i]['BSname']}</option>`;
                    $('#bs-select1').append(tmpHtml);
                }
                $('#bs-select1').append('<option>추가</option>');
            }
        }
    })
}

function bseditevent() {
    if ($('#bsedit').css('display') == 'none') {
        $('#bsedit').show();
        $('#plusminus2').attr('class', 'fas fa-minus')
    } else {
        $('#plusminus2').attr('class', 'fas fa-plus')
        $('#bsedit').hide();
    }
}

function canclebtn() {
    $('#editbtn1').show()
    $('#editbtn11').hide()
    $('input[name=bdname]').hide();
    $('#bd-select1').show();
    $('#delbtn1').show()
    $('#cancelbtn1').hide()
    $('#addbtn1').hide()
}

function canclebtn2() {
    $('#editbtn2').show()
    $('#editbtn22').hide()
    $('input[name=bsname]').hide();
    $('#bs-select1').show();
    $('#delbtn2').show()
    $('#cancelbtn2').hide()
    $('#addbtn2').hide()
    $('input[name=org_bdname2]').hide()
    $('#bd-select2').show()
}

function bdeditbtn() {
    bdname = $('#bd-select1').val()
    if (!bdname || bdname == '추가') {
        return
    } else {
        $('#editbtn1').hide()
        $('#editbtn11').show()
        $('#bd-select1').hide();
        $('#delbtn1').hide();
        $('#cancelbtn1').show();
        $('input[name=bdname]').show();
        $('input[name=org_bdname]').val($('#bd-select1').val())
        $('input[name=bdname]').val($('#bd-select1').val())
    }
}

function bdeditevent() {
    if ($('#bdedit').css('display') == 'none') {
        $('#bdedit').show();
        $('#plusminus1').attr('class', 'fas fa-minus')
    } else {
        $('#plusminus1').attr('class', 'fas fa-plus')
        $('#bdedit').hide();
    }
}


function bddelete() {
    bdname = $('#bd-select1').val()
    if (!bdname || bdname == '추가') {
        return
    } else {
        location.href = 'bddel/' + bdname
    }
}

function bseditbtn() {
    bsname = $('#bs-select1').val()
    if (!bsname) {
        return
    } else {
        $('#bs-select1').hide()
        $('#editbtn2').hide()
        $('#editbtn22').show()
        $('#delbtn2').hide()
        $('#cancelbtn2').show()
        $('input[name=org_bsname]').val(bsname)
        $('input[name=bsname]').val(bsname)
        $('input[name=bsname]').show()
    }
}

function bsdelete() {
    bsname = $('#bs-select1').val()
    bdname = $('#bd-select2').val()
    {
        if (!bsname) {
            return
        } else {
            $.ajax({
                type: 'POST',
                url: '/bsdel',
                data: {bdname: bdname, bsname: bsname},
                success: function (re) {
                    alert(re)
                }
            })
        }
    }
    if (!bsname) {
        return
    } else {
        location.href = 'bsdel/' + bdname + '/' + bsname
    }
}
