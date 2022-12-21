document.addEventListener('DOMContentLoaded', function() {
    var closeButton = document.querySelector('.js-modal-close'),
        overlay = document.querySelector('.js-overlay-modal'),
        openModalButton = document.querySelector('.js-open-modal'),

        modalElem = document.querySelector('.investments-modal');

        openModalButton.addEventListener('click', function(e){
            e.preventDefault();

            modalElem.classList.add('active');
            overlay.classList.add('active')
        });

        closeButton.addEventListener('click', function (e) {
            modalElem.classList.remove('active');
            overlay.classList.remove('active');
        });

        overlay.addEventListener('click', function() {
            document.querySelector('.investments-modal.active').classList.remove('active');
            this.classList.remove('active');
        });
});
