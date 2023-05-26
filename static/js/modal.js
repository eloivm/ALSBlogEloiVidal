document.addEventListener('DOMContentLoaded', function() {
    var deleteButtons = document.querySelectorAll('.post-delete');
    var deleteModal = document.getElementById('deleteModal');
    var deleteConfirmButton = document.getElementById('deleteConfirm');
    var deleteCancelButton = document.getElementById('deleteCancel');
    var deleteUrl = '';

    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            deleteUrl = event.target.href;
            deleteModal.style.display = 'block';
        });
    });

    deleteConfirmButton.addEventListener('click', function() {
        window.location.href = deleteUrl;
    });

    deleteCancelButton.addEventListener('click', function() {
        deleteModal.style.display = 'none';
    });
});