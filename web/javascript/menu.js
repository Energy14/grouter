function toggleMenu() {
  document.getElementById('menu').classList.toggle('open');
}

var lastInputs = {};
var listId = 0;

mapInputLists();

function mapInputLists() {
  let inputLists = document.getElementsByClassName(
    'menu-content__body-input-list'
  );

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

  let inputLists = document.getElementsByClassName(
    'menu-content__body-input-list'
  );

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
  try {
    let info = collectInfo();
    console.log('Sending: ', info);

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'API_GOES_HERE', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        console.log(xhr.responseText);
      } else {
        console.log('Error: ' + xhr.status);
      }
    };

    xhr.send(JSON.stringify(info));
  } catch (e) {
    // Error collecting info, do nothing
  }
}
