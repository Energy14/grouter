function toggleMenu() {
  document.getElementById('menu').classList.toggle('open');
}

var lastInputs = {};
var listId = 0;

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

function addInput(input) {
  list = input.parentNode.parentNode;

  if (lastInputs[list.id] !== input) return;

  let newItem = lastInputs[list.id].parentNode.cloneNode(true);
  let newInput = newItem.getElementsByTagName('input')[0];

  newInput.value = '';

  list.appendChild(newItem);
  updateLastInput(list);
}

function removeInput(input) {
  input.parentNode.removeChild(input);
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

  return info;
}

function sendInfo() {
  let info = null;
  try {
    info = collectInfo();
    console.log('Sending: ', info);
  } catch (e) {
    // Error collecting info, form validation failed
    return;
  }

  let xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://localhost:5000/api', true);
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.onreadystatechange = function () {
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
  };

  xhr.send(JSON.stringify(info));
}
