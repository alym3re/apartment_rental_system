// Initialize tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

// Initialize popovers
$(function () {
    $('[data-toggle="popover"]').popover()
})

// Form submission handling
$(document).ready(function() {
    // Handle form submissions with loading indicators
    $('form').submit(function() {
        var submitBtn = $(this).find('button[type="submit"]')
        submitBtn.prop('disabled', true)
        submitBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...')
    })
    
    // Image preview for file inputs
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
    
    // Auto-close alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close')
    }, 5000)
    
    // Enable datepickers
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true
    })
    
    // Initialize DataTables
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

// Custom file input display
document.querySelectorAll('.custom-file-input').forEach(function(input) {
    input.addEventListener('change', function(e) {
        var fileName = e.target.files[0].name
        var label = e.target.nextElementSibling
        label.querySelector('span').textContent = fileName
    })
})