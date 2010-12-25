
//var data = ['我的家里', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

$().ready(function() {

                $.getJSON("/account/role_name_ajax/",
                          {
                          },
                          function(data) {
                                  $("#id_role_name").autocomplete(data, {
                                          minChars: 0,
                                                          max: 12,
//                                                          autoFill: true,
//                                                          mustMatch: true,
//                                                          matchContains: false,
                                                          scrollHeight: 220,
                                                          formatItem: function(data, i, total) {
                                                          // don't show the current month in the list of values (for whatever reason)
                                                          //if ( data[0] == months[new Date().getMonth()] ) 
                                                          //return false;
                                                          return data[0];
                                                  }
                                          });

                          });
                $.getJSON("/service_area/service_area_name_ajax/",
                          {
                          },
                          function(data) {
                                  $("#id_service_area_name").autocomplete(data, {
                                          minChars: 0,
                                                          max: 12,
//                                                          autoFill: true,
//                                                          mustMatch: true,
//                                                          matchContains: false,
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
//                                                          matchContains: false,
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
        });
