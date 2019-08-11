// const dom = {};
//
// function attemptLogin() {
//     const email = dom.$email.val();
//     const password = dom.$password.val();
//
//     $.post({
//         type: "POST",
//         contentType: "application/json",
//         url: '/login',
//         data: JSON.stringify({email, password}),
//         //dataType: "json"
//     })
//         .done((response) => {
//             dom.$warning.hide();
//             if (response.redirect) {
//                 window.location.href = response.redirect;
//             }
//         })
//         .fail(() => {
//             dom.$warning.show();
//         });
// }
//
// window.onload = () => {
//     dom.$email = $("#email");
//     dom.$password = $("#password");
//     dom.$loginForm = $("#login-form");
//     dom.$warning = $("#warning");
//     dom.$login = $("#login");
//
//     dom.$login.click(attemptLogin);
//     dom.$loginForm
//         .on('keypress', (e) => {
//             if (e.keyCode === 13)
//                 attemptLogin();
//         });
// };

dom = {};

function renderGarages(data) {
    _.forEach(data, (garage) => {
        if (!garage.spots || garage.spots.length === 0) {
            return false;
        }
        const spotCount = garage.spots.length;
        const occupiedSpotCount = _.chain(garage.spots)
            .filter((spot) => !spot.reservation)
            .size()
            .value();

        dom.$garagesContent.append(`<br/>
<div data-id=${garage.id} class="garage-box border">
<h3>${garage.name}</h3>
<h4>${garage.address}</h4>
<p>Available spots: ${occupiedSpotCount} / ${spotCount}</p>
</div>`);
    });

    dom.$garagesContent.find('.garage-box').click(function () {
        const garageId = $(this).attr('data-id');
        $.post({
            type: "POST",
            contentType: "application/json",
            url: '/reserve/' + garageId,
            dataType: "json"
        })
            .done(fetch);
    });
}

function reset() {
    dom.$garagesContainer.hide();
    dom.$occupyContainer.hide();
    dom.$leaveContainer.hide();

    dom.$garagesContent.empty();
}

function renderReservation() {
    dom.$occupyContainer.show();
    dom.$occupyContainer.append(`<h2>Your spot is currently reserved</h2>`);
}

function fetch() {
    $.post({
        type: "POST",
        contentType: "application/json",
        url: '/details',
        dataType: "json"
    })
        .done((response) => {
            reset();
            if (_.isArray(response)) {
                dom.$garagesContainer.show();
                renderGarages(response);
            } else if (response) {
                renderReservation();
            }
        });
}

window.onload = () => {
    dom.$garagesContainer = $('#garages-container');
    dom.$garagesContent = $('#garages-content');
    dom.$occupyContainer = $('#occupy-container');
    dom.$leaveContainer = $('#leave-container');

    fetch()
};