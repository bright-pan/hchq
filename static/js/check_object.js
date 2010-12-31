$(document).ready(function(){
                $.getJSON("/service_area/service_area_name_ajax/",
                          {
                          },
                          function(data) {
                                  $("#id_service_area_name").autocomplete(data, {
                                          minChars: 0,
                                                          max: 12,
//                                                          autoFill: true,
//                                                          mustMatch: true,
                                                          matchContains: true,
                                                          scrollHeight: 220,
                                                          formatItem: function(data, i, total) {
                                                          // don't show the current month in the list of values (for whatever reason)
                                                          //if ( data[0] == months[new Date().getMonth()] ) 
                                                          //return false;
                                                          return data[0];
                                                  }
                                          });
                                  $("#id_mate_service_area_name").autocomplete(data, {
                                          minChars: 0,
                                                          max: 12,
//                                                          autoFill: true,
//                                                          mustMatch: true,
                                                          matchContains: true,
                                                          scrollHeight: 220,
                                                          formatItem: function(data, i, total) {
                                                          // don't show the current month in the list of values (for whatever reason)
                                                          //if ( data[0] == months[new Date().getMonth()] ) 
                                                          //return false;
                                                          return data[0];
                                                  }
                                          });

                          });
                $("#id_service_area_name").blur(function() {
                                service_area_name_old = '';
                                service_area_name = $("#id_service_area_name").val();
                                if (service_area_name != '' && service_area_name != service_area_name_old)
                                {
//                                        alert('********');
                                        service_area_name_old = service_area_name;
                                        $("#id_department_name").unautocomplete();
                                        $.getJSON("/department/department_name_ajax/",
                                                  {
                                                  service_area_name :$("#id_service_area_name").val()
                                                                  },
                                                  function(data) {
                                                          $("#id_department_name").autocomplete(data, {
                                                                  minChars: 0,
                                                                                  max: 12,
//                                                          autoFill: true,
//                                                          mustMatch: true,
                                                                                  matchContains: true,
                                                                                  scrollHeight: 220,
                                                                                  formatItem: function(data, i, total) {
                                                                                  // don't show the current month in the list of values (for whatever reason)
                                                                                  //if ( data[0] == months[new Date().getMonth()] ) 
                                                                                  //return false;
                                                                                  return data[0];
                                                                          }
                                                                  });

                                                  });

                                }
                                
                        });
                $("#id_mate_service_area_name").blur(function() {
                                mate_service_area_name_old = '';
                                mate_service_area_name = $("#id_mate_service_area_name").val();
                                if (mate_service_area_name != '' && mate_service_area_name != mate_service_area_name_old)
                                {
//                                        alert('********');
                                        mate_service_area_name_old = mate_service_area_name;
                                        $("#id_mate_department_name").unautocomplete();
                                        $.getJSON("/department/department_name_ajax/",
                                                  {
                                                  service_area_name :$("#id_mate_service_area_name").val()
                                                                  },
                                                  function(data) {
                                                          $("#id_mate_department_name").autocomplete(data, {
                                                                  minChars: 0,
                                                                                  max: 12,
//                                                          autoFill: true,
//                                                          mustMatch: true,
                                                                                  matchContains: true,
                                                                                  scrollHeight: 220,
                                                                                  formatItem: function(data, i, total) {
                                                                                  // don't show the current month in the list of values (for whatever reason)
                                                                                  //if ( data[0] == months[new Date().getMonth()] ) 
                                                                                  //return false;
                                                                                  return data[0];
                                                                          }
                                                                  });

                                                  });

                                }
                                
                        });

                var photo_ready = false;
                $("#uploader_dialog").dialog({ autoOpen: false ,
                                        modal:true,
                                        buttons: [
                                                {id:"uploader",text:"上传文件",},
                                                {text:"确定",click:function(){$(this).dialog('close')}}
                                                ],
                                        });
                $('#open_uploader_dialog').click(function(){
                                $("#uploader_dialog").dialog("open");
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
                                        $('#id_photo').attr('')
                                        
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
