function toggleMenu() {
    document.getElementById('menu').classList.toggle('open');
}

var lastInputs = {};
var listId = 0;

var formSubmits = [
    {
        element: document.getElementById('routeSubmit'),
        restText: 'Izveidot maršrutus',
        loadingText: 'Veido maršrutus'
    },
    {
        element: document.getElementById('courierSubmit'),
        restText: 'Izvēlēties maršrutu',
        loadingText: 'Ielādē maršrutu'
    },
    {
        element: document.getElementById('orderSubmit'),
        restText: 'Pasūtīt',
        loadingText: 'Veido pasūtījumu'
    }
];

mapInputLists();

function mapInputLists() {
    let inputLists = document.getElementsByClassName('menu-content__body-input-list');

    for (let i = 0; i < inputLists.length; i++) {
        updateLastInput(inputLists[i]);
    }
}

function updateLastInput(list) {
    if (!list.id) {
        list.id = 'inputList-' + listId++;
    }

    imputs = list.getElementsByTagName('input');

    lastInputs[list.id] = imputs[imputs.length - 1];
}

function updateInputList(input) {
    let list = input.parentNode.parentNode;

    if (input.value === '' && list.getElementsByTagName('input').length > 1) {
        input.parentNode.remove();
        return;
    }

    if (lastInputs[list.id] !== input) return;

    let maxSize = parseInt(list.getAttribute('max-size'));
    if (maxSize && list.getElementsByTagName('input').length >= maxSize) return;

    let newItem = lastInputs[list.id].parentNode.cloneNode(true);
    let newInput = newItem.getElementsByTagName('input')[0];

    newInput.value = '';

    list.appendChild(newItem);
    updateLastInput(list);
}

function collectInfo() {
    let info = {};

    let inputLists = document.getElementsByClassName('menu-content__body-input-list');

    for (let i = 0; i < inputLists.length; i++) {
        let inputList = inputLists[i];
        let inputListId = inputList.id;

        let inputs = inputList.getElementsByTagName('input');

        let inputListInfo = [];
        for (let j = 0; j < inputs.length; j++) {
            let inputValue = inputs[j].value;

            if (inputValue) {
                inputListInfo.push(inputValue);
            }
        }

        if (inputListInfo.length > 0) {
            info[inputListId] = inputListInfo;
        } else {
            throw new Error('Input list ' + inputListId + ' is empty');
        }
    }

    let optionLists = document.getElementsByClassName('menu-content__body-option-list');
    for (let i = 0; i < optionLists.length; i++) {
        let optionList = optionLists[i];
        let optionListId = optionList.id;

        let options = optionList.getElementsByClassName('menu-content__body-option-list-item');

        let optionListInfo = [];
        for (let j = 0; j < options.length; j++) {
            if (!options[j].getElementsByTagName('input')[0].checked)
              continue;
            let optionValue = options[j].getElementsByTagName('label')[0].innerText;
            let optionId = options[j].getElementsByTagName('input')[0].id.split('-')[1];

            if (optionValue) {
                optionListInfo.push([optionValue, optionId]);
            }
        }

        if (optionListInfo.length > 0) {
            info[optionListId] = optionListInfo;
        } else {
            throw new Error('Input list ' + optionListId + ' is empty');
        }
    }

    return info;
}

function disableFormSubmits() {
    for (let i = 0; i < formSubmits.length; i++) {
        if (formSubmits[i].element === null)
          continue;

        formSubmits[i].element.disabled = true;
        formSubmits[i].element.getElementsByTagName('span')[0].innerHTML = formSubmits[i].loadingText;
    }
}

function enableFormSubmits() {
    for (let i = 0; i < formSubmits.length; i++) {
        if (formSubmits[i].element === null)
          continue;

        formSubmits[i].element.disabled = false;
        formSubmits[i].element.getElementsByTagName('span')[0].innerHTML = formSubmits[i].restText;
    }
}

function sendAdminInfo(serverHost) {
    disableFormSubmits();

    let info = null;
    try {
        info = collectInfo();
    } catch (e) {
        // Error collecting info, form validation failed
        enableFormSubmits();
        return;
    }

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://' + serverHost + '/api/admin', true);

    sendRequest(xhr, info);
}

function sendCourierInfo(serverHost) {
    disableFormSubmits();

    let info = null;
    try {
        info = collectInfo();
    } catch (e) {
        // Error collecting info, form validation failed
        enableFormSubmits();
        return;
    }

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://' + serverHost + '/api/courier', true);

    sendRequest(xhr, info);
}

function sendOrderInfo(serverHost, userId) {
    disableFormSubmits();

    let info = null;
    try {
        info = collectInfo();
    } catch (e) {
        // Error collecting info, form validation failed
        enableFormSubmits();
        return;
    }
    info['user_id'] = userId;

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://' + serverHost + '/api/user/save-order', true);

}

function findOrderRoute(serverHost) {
    disableFormSubmits();

    let info = null;
    try {
        info = collectInfo();
    } catch (e) {
        // Error collecting info, form validation failed
        enableFormSubmits();
        return;
    }

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://' + serverHost + '/api/user/find-order-route', true);

    sendRequest(xhr, info);
}

function sendRequest(xhr, info) {
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function () {
        try {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    let response_json = JSON.parse(xhr.responseText);
                    drawRoutes(response_json);
                } else {
                    alert(
                        'Error sending info: ' +
                        (xhr.status === 0 ? 'API could not be reached or is not configured!' : '') +
                        (xhr.responseText ? '\nResponse: ' + xhr.responseText : '') +
                        '\nStatus: ' +
                        xhr.status
                    );
                }
            }
        } finally {
            enableFormSubmits();
        }
    };

    xhr.ontimeout = function () {
        alert('Request timed out!');
        enableFormSubmits();
    };

    xhr.send(JSON.stringify(info));
}
