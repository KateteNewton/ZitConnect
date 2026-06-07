const stars = document.querySelectorAll('.star');

const ratingValue =
    document.getElementById('rating-value');

const ratingMessage =
    document.getElementById('rating-message');


stars.forEach((star, index) => {

    // Hover effect
    star.addEventListener('mouseover', () => {

        highlightStars(index);

    });

    // Click event
    star.addEventListener('click', () => {

        ratingValue.value = index + 1;

        ratingMessage.textContent =
            `You rated ${index + 1} star(s).`;

    });
});


// Highlight stars
function highlightStars(index){

    stars.forEach((star, i) => {

        if(i <= index){

            star.classList.add('active-star');

        } else {

            star.classList.remove('active-star');
        }
    });
}