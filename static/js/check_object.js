$().ready(function(){
                var photo_ready = false;
                $("#dialog").dialog({ autoOpen: false });
		$('#open_uploader_dialog').click(function(){
                                $("#dialog").dialog("open");
                                return false;	
                        });
                var csrf_token = $('#csrf_token >div >input').attr("value");

		new AjaxUpload('uploader', {
			action: '/check_object/add/uploader/',
                                        name: 'photo',
                                        data: {
                                csrfmiddlewaretoken : csrf_token,
                                                },
                                        onSubmit : function(file , ext){
                                        if (ext && /^(jpg|png|jpeg|gif)$/.test(ext)){
                                                /* Setting data */
                                                $('#uploader').text('正在上传 ' + file);
                                                this.disable();
                                        } else {					
                                                // extension is not allowed
                                                $('#uploader').text('请上传jpg|png|jpeg|gif格式的文件');
                                                // cancel upload
                                                return false;				
                                        }
                                },
                                        onComplete : function(file){
                                        photo_ready = true;
                                        $('#uploader').text('成功上传 ' + file);
                                        
                                }		
		});
                $('#id_form_add').submit(function(){
                                if(photo_ready == true)
                                {
                                        return true;
                                }
                                else
                                {
                                        $('#id_submit_error').text('请先上传照片或者拍照！').show().fadeOut(5000);
                                        return false;
                                }
                        });
        });
