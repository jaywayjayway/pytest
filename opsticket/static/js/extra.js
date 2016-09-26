Array.prototype.remove = function(index){
    this.splice(index,1);
}

function ajax_replace(url, id, e){
    var box = $('#'+id);
    $.ajax({
        url:url,
        cache:false,
        success:function(html){
            box.html(html);
        }
    })
}

function ajax_submit(url, id, msg){
    $.ajax({
        cache:false,
        url:url,
        type:'POST',
        data:$('#'+id).serialize(),
        success:function(data){
            broadcast(data);
        },
        error:function(data){
            console.log(data.status);
            $.Notification.notify('error','bottom right','啊啊啊啊啊啊', '网络有点问题了 >.<');
        }
    })
    $('#form-modal').modal('hide');
}

function broadcast(data){
    if(data.success){
        $.Notification.notify('success','bottom right','通知', data.msg);
    }else{
        $.Notification.notify('warning','bottom right','警告', data.msg);
    }
}

function droptablerow(row){
    var i=row.parentNode.parentNode.rowIndex;
    document.getElementById('data-table').deleteRow(i);
}

function addtablerow(data){
    var table=document.getElementById('data-table').getElementsByTagName("tbody")[0];
    var row=table.insertRow();
    for(var i in data){
        row.insertCell().innerText = data[i]["text"];
    }
    return row
}

function confirm_delete(url, row){
    swal({
        title: "你确认要删除?",
        text: "我告诉你,你可想好了,删了就木有了,谁也帮不了你!",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: 'btn-warning',
        confirmButtonText: "是的,我想好了!",
        cancelButtonText: "算了,不删了",
        closeOnConfirm: false
    }, function () {
        $.ajax({
            url:url,
            type:'DELETE',
            success:function(data){
                if(data.success){
                    swal("成功!", data["msg"], "success");
                    droptablerow(row);
                }else{
                    swal("失败!", data["msg"], "error");
                }
            },
            error:function(data){
                swal("失败!", "恭喜你现在还有后悔的机会.", "error");
            }
        });
    });
}
