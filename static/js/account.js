
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
        });
