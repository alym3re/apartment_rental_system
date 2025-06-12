$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

$(function () {
    $('[data-toggle="popover"]').popover()
})

$(document).ready(function() {
    $('form').submit(function() {
        var submitBtn = $(this).find('button[type="submit"]')
        submitBtn.prop('disabled', true)
        submitBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...')
    })
    
    $('.img-preview-input').change(function() {
        var input = this
        var preview = $(this).data('preview')
        
        if (input.files && input.files[0]) {
            var reader = new FileReader()
            
            reader.onload = function(e) {
                $(preview).attr('src', e.target.result)
                $(preview).show()
            }
            
            reader.readAsDataURL(input.files[0])
        }
    })
    
    setTimeout(function() {
        $('.alert').alert('close')
    }, 5000)
    
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true
    })
    
    if ($.fn.DataTable) {
        $('#dataTable').DataTable({
            responsive: true,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
            }
        })
    }
})

document.querySelectorAll('.custom-file-input').forEach(function(input) {
    input.addEventListener('change', function(e) {
        var fileName = e.target.files[0].name
        var label = e.target.nextElementSibling
        label.querySelector('span').textContent = fileName
    })
})