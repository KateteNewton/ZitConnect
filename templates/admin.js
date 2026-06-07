// Select all approve buttons
const approveButtons =
    document.querySelectorAll('.approve-btn');


// Select all reject buttons
const rejectButtons =
    document.querySelectorAll('.reject-btn');


// APPROVE FUNCTION
approveButtons.forEach(button => {

    button.addEventListener('click', () => {

        const confirmed = confirm(
            "Are you sure you want to approve this tutor?"
        );

        if(confirmed){

            alert("Tutor approved successfully.");

            // Optional:
            // button.parentElement.parentElement.remove();
        }
    });
});


// REJECT FUNCTION
rejectButtons.forEach(button => {

    button.addEventListener('click', () => {

        const confirmed = confirm(
            "Are you sure you want to reject this tutor?"
        );

        if(confirmed){

            alert("Tutor rejected.");

            // Optional:
            // button.parentElement.parentElement.remove();
        }
    });
});