$(function() {
    $('button').click(function() {

        // ALERTIFY : Notifications (requires alertify.js)        
        var alertify_notification = "DATA SUBMITTED:<br><br>";        
        var form_fields_array = $('form').serialize().split('&');
        var form_fields = {};
        var fail = false;
        for (var i = 0; i < form_fields_array.length; i++) {
            var kvp = form_fields_array[i].split('=');
            form_fields[kvp[0]] = kvp[1]
            if (!kvp[1]) {
                fail = true
            };
            alertify_notification = alertify_notification + form_fields_array[i] + "<br>";
        }

        // If data missing
        if (fail) {

            alertify.error('ERROR : Missing Field - please fill in all fields');
            jQuery("#apiResponse").text("Missing Field - please fill in all fields");

        // Otherwise allow data

        } else {
            
            jQuery("#apiResponse").html("<br>Awaiting API results (may take a minute or two (if it fails it will say here))...<br><br>Public Key = " + form_fields.apiPublicKey + "<br>Secret Key = " + form_fields.apiSecretKey + "<br>Category ID = " + form_fields.categoryID);
            var notify_inprogress = alertify.notify('Request in progress.', 'custom', 1000);

            $.ajax({
                url: '/category_campaign_grabber_details',
                data: $('form').serialize(),
                type: 'POST',
                success: function(response) {

                    // Handle notifications       
                    notify_inprogress.dismiss();             
                    alertify.notify("SUCCESS! Audiences/Campaigns Retrieved", 'success', 5, function() {}); // success

                    // Push data into form
                    var data = JSON.parse(response);
                    var pretty_data = JSON.stringify(data,undefined,3);
                    jQuery("#apiResponse").text(pretty_data);
                


                },
                error: function(error) {
                    alertify.error(error.statusText + "<br> Check your credentials/category ID");
                    notify_inprogress.dismiss();
                    jQuery("#apiResponse").html("<br>Failure - either credentials are wrong or something is broken (send your category ID to roshan.gonsalkorale@oracle.com)...<br><br>Public Key = " + form_fields.apiPublicKey + "<br>Secret Key = " + form_fields.apiSecretKey + "<br>Category ID = " + form_fields.categoryID);
                }
            });
        }



    });
});