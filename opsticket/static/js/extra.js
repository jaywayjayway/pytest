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
            $.Notification.notify('error','top right','啊啊啊啊啊啊', '网络有点问题了 >.<');
        }
    })
    $('#form-modal').modal('hide');
}

function broadcast(data){
    data = JSON.parse(data);
    if(data.success){
        $.Notification.notify('success','top right','通知', data.msg);
    }else{
        $.Notification.notify('warning','top right','警告', data.msg);
    }
}

function droptablerow(row){
    var i=row.parentNode.parentNode.rowIndex;
    document.getElementById('data-table').deleteRow(i);
    if(body){
        console.log(body)
        delete body["data"].i;
    }
}

function addtablerow(data){
    var table=document.getElementById('data-table').getElementsByTagName("tbody")[0];
    var row=table.insertRow();
    for(var i in data){
        row.insertCell().innerText = data[i]["text"];
    }
    //row.insertCell().innerHTML="<a class='btn-danger' onclick='droptablerow(this)'>删除</a>";
    console.log("adddddd..............")
    return row
}

function delete_resource(url, row){
    if(confirm('确定要删除该数据?')){
        $.ajax({
            url:url,
            type:'DELETE',
            success:function(data){
                broadcast(data);
                droptablerow(row);
            }
        })
    }else{
        return ;
    };
}
