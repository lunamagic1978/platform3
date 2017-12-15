/**
 * Created by smzdm on 2017/12/13.
 */
        function displayCreate() {
            $('#createApi').css({display:'flex'});
        }

        function hiddenCreate() {
            $('#createApi').css({display:'none'});
        }

        function editDate() {
            $('#editbefore').hide();
            $('#editafter').show();
        }

        $('#id_request_method').change(function () {
            var post_method = ($(this).children('option:selected').val());
            console.log(post_method);
            if (post_method=="POST"){
                $('#post-method').show();
            }
            else{
                $('#post-method').hide();
            };
        })