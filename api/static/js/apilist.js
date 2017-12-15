/**
 * Created by smzdm on 2017/12/13.
 */
        function displayCreate() {
            $('#createApi').css({display:'flex'});
        }

        $('#id_request_methond').change(function () {
            var post_method = ($(this).children('option:selected').val());
            console.log(post_method);
            if (post_method=="POST"){
                $('#post-method').show();
            }
            else{
                $('#post-method').hide();
            };
        })