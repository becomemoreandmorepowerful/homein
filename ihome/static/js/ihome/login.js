function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        // 向后端发送请求，提交用户的登录           信息
        var req_data = {
            mobile: mobile,
            password: passwd
        };
        // 将js对象转换为json字符串
        req_json = JSON.stringify(req_data);
        $.ajax({
            url: "/api/v1_0/sessions" ,// 请求路径url
            type: "post", // 请求方式
            data: req_json, // 发送的请求体数据
            contentType: "application/json",  // 指明向后端发送的是json格式数据
            dataType: "json", // 指明从后端收到的数据是json格式的
            headers: {
                // 获取设置的cookie中的csrf_token中的值
                "X-CSRFToken": getCookie("csrf_token")
            },  // 自定义的请求头
            success: function (resp) {
                if ( resp.errno == 0 ) {
                    // 注册成功, 引导到主页页面
                    location.href = "/";
                    return;
                }
                else {
                    // 其他错误信息，在页面中展示
                    $("#password-err span").html(resp.errmsg);
                    $("#password-err").show();
                    return;
                }
            }
        })

    });
})