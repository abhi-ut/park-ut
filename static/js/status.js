dom = {};

function reset() {
    dom.$garagesContainer.hide();
    dom.$reservationContainer.hide();
    dom.$garagesContainer.empty();
    dom.$reservationContainer.empty();
}

function renderGarages(data) {
    dom.$garagesContainer.show();
    dom.$garagesContainer.append(`<h1>Choose a garage to book</h1>`);
    dom.$garagesContainer.append(`<br/>`);

    _.forEach(data, (garage) => {
        if (!garage.spots || garage.spots.length === 0) {
            return false;
        }
        const id = _.uniqueId('garage-box-');
        const spotCount = garage.spots.length;
        const availableSpotCount = _.chain(garage.spots)
            .filter((spot) => !spot.reservation)
            .size()
            .value();

        dom.$garagesContainer.append(`<div id=${id} class="garage-box card border shadow-sm mb-4 bg-white rounded">
<h3>${garage.name}</h3>
<h5>${garage.address}</h5>
<a>Available spots: ${availableSpotCount} / ${spotCount}</a>
</div>`);

        if (availableSpotCount > 0) {
            $(`#${id}`)
                .addClass('clickable')
                .click(function () {
                    $.post({
                        type: "POST",
                        contentType: "application/json",
                        url: '/reserve/' + garage.id,
                        dataType: "json"
                    })
                        .done(fetchDetails);
                });
        }

    });
}

function renderReservation(garage) {
    dom.$reservationContainer.show();
    dom.$reservationContainer.append(`<h2>Your spot is currently reserved for 10 minutes</h2>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<h4>Reservation details</h4>`);
    dom.$reservationContainer.append(`<p>Garage name: ${garage.name}</p>`);
    dom.$reservationContainer.append(`<p>Garage address: ${garage.address}</p>`);
    dom.$reservationContainer.append(`<p>Spot location: ${garage.spot.location}</p>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<h4>Your reservation is valid until ${garage.spot.reservation.time}</h4>`);
    dom.$reservationContainer.append(`<p>After this time, you will lose your spot</p>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<h4>You may occupy your spot once you are at the garage</h4>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<button class="btn btn-primary btn-block">Occupy</button>`);

    dom.$reservationContainer.find('button').click(() => {
        $.post({
            contentType: "application/json",
            url: '/occupy',
            dataType: "json"
        })
            .done(fetchDetails);
    });
}


function renderOccupancy(garage) {
    dom.$reservationContainer.show();
    dom.$reservationContainer.append(`<h2>You are currently holding a spot</h2>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<h4>Occupancy details</h4>`);
    dom.$reservationContainer.append(`<p>Garage name: ${garage.name}</p>`);
    dom.$reservationContainer.append(`<p>Garage address: ${garage.address}</p>`);
    dom.$reservationContainer.append(`<p>Spot location: ${garage.spot.location}</p>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<h4>This spot has been held since ${garage.spot.reservation.time}</h4>`);
    dom.$reservationContainer.append(`<p>You will be billed based on how long you have stayed</p>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<h4>You may choose to checkout at anytime</h4>`);
    dom.$reservationContainer.append(`<br/>`);

    dom.$reservationContainer.append(`<button class="btn btn-primary btn-block">Checkout</button>`);

    dom.$reservationContainer.find('button').click(() => {
        $.post({
            contentType: "application/json",
            url: '/clear',
            dataType: "json"
        })
            .done(fetchDetails);
    });
}


function fetchDetails() {
    $.get({
        contentType: "application/json",
        url: '/details',
        dataType: "json"
    })
        .done((response) => {
            reset();
            if (_.isArray(response)) {
                renderGarages(response);
            } else if (_.isObject(response)) {
                (response.spot.reservation.occupied ? renderOccupancy : renderReservation)(response);
            } else {
                window.alert('Illegal state.');
            }
        });
}

window.onload = () => {
    dom.$garagesContainer = $('#garages-container');
    dom.$reservationContainer = $('#reservation-container');

    fetchDetails()
};