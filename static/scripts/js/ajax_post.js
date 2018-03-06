// FUNCTION : Campaign Poll
window.categoryCampaignPoll = function(requestID){

    // Set up recurring loop to check campaign query every X ms
    setTimeout(function() {

        // add loop counter to set a max
        window.categoryCampaignPoll_count = window.categoryCampaignPoll_count || 0; // calculate current loop       
        window.categoryCampaignPoll_count++ // increase loop count
        window.categoryCampaignPoll_count_loop_max = 40; // set max loops to run
        window.categoryCampaignPoll_count_loop_interval = 5000; // Interval between loops

        // check if loop exceeded
        if(window.categoryCampaignPoll_count_loop_max < window.categoryCampaignPoll_count){
            window.categoryCampaignPoll_stoploop = true;
        }

        if (!window.categoryCampaignPoll_stoploop){

            // Format request data
            request_data = "requestID=" + requestID;

            $.ajax({
                    url: '/category_campaign_grabber_poll',
                    data: request_data,
                    type: 'POST',
                    success: function(response) {
                        
                        // Parse response so we can read it
                        response = JSON.parse(response);

                        // If job completed : send back to form
                        if (response.status === "completed"){

                            // Push data into form                                                                
                            var pretty_data = JSON.stringify(response.data,undefined,3);                            
                            jQuery("#apiResponse").text(pretty_data);
                            notify_inprogress.dismiss();
                            alertify.notify('Success! Your results are in the box ', 'success', 5);

                            // Stop loop
                            window.categoryCampaignPoll_stoploop = true; 

                        // If job not completed : try again
                        } else if (response.status.indexOf('not completed') > -1){

                            // Poll again
                            window.categoryCampaignPoll(requestID);
                        };
                        
                    },
                    error: function(error) {
                        
                        // Stop job
                        console.log("ERROR : See below");
                        console.log(error);
                        window.categoryCampaignPoll(requestID);                        
                    }
                });
            } else {

                // Polling Stopped                
                notify_inprogress.dismiss(); // remove in progress message
                alertify.error("Query taken too long - this query probably won't work :("); // error message
                jQuery("#apiResponse").text("Query taken too long - this query probably won't work :(");
            }

        
    },window.categoryCampaignPoll_count_loop_interval);

};

// FUNCTION : Campaign Query
window.categoryCampaignQuery = function(){

        // Reset poll limit
        window.categoryCampaignPoll_count = 0;
        window.categoryCampaignPoll_stoploop = false;

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
            window.notify_inprogress = alertify.notify('Request in progress.', 'custom', 1000);

            //Generate request ID
            requestID = Math.random()*1000000000000000000;

            // Join form data to requestID to pass to server
            request_data = $('form').serialize() + "&requestID=" + requestID;

            // API Return Response
            $.ajax({
                url: '/category_campaign_grabber_queue',
                data: request_data,
                type: 'POST',
                success: function(response) {
                                        
                    // FIGURE OUT TO DO WITH RESPONSE
                },
                error: function(error) {
                    alertify.error(error.statusText + "<br> Check your credentials/category ID");
                    notify_inprogress.dismiss();
                    jQuery("#apiResponse").html("<br>Failure - either credentials are wrong or something is broken (send your category ID to roshan.gonsalkorale@oracle.com)...<br><br>Public Key = " + form_fields.apiPublicKey + "<br>Secret Key = " + form_fields.apiSecretKey + "<br>Category ID = " + form_fields.categoryID);
                }
            });

            // Begin polling API to see if ready
            categoryCampaignPoll(requestID);
        }

    };

// Add Tracking to form submit
$(function() {
    $('button').click(function(){        
        categoryCampaignQuery()});
});