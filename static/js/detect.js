import { initializeApp } from "https://www.gstatic.com/firebasejs/9.19.1/firebase-app.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/9.19.1/firebase-storage.js";

const firebaseConfig = {
  apiKey: "AIzaSyCBo6OLIpwzcBZmcKqU2J_yDjFpkrqFwRs",
  authDomain: "skin-detection-app-59904.firebaseapp.com",
  projectId: "skin-detection-app-59904",
  storageBucket: "skin-detection-app-59904.appspot.com",
  messagingSenderId: "573690391196",
  appId: "1:573690391196:web:47692f5e8e880f8a051b59",
  measurementId: "G-0MKFKY74N2"
};

const app = initializeApp(firebaseConfig);
const storage = getStorage(app);


let uploadButton = document.getElementById("upload");
let chosenImage = document.getElementById("chosen-image");

const dummyResult = document.getElementById("result_dummy")
const result = document.getElementById("results")

let resultBtn = document.getElementById("resultBtn");
resultBtn.addEventListener("click", detectFunction)

uploadButton.onchange = () => {
  let reader = new FileReader();
  reader.readAsDataURL(uploadButton.files[0]);
  reader.onload = () => {
    chosenImage.setAttribute("src", reader.result);
  }
  result.style.display = "none"
  dummyResult.style.display = "block"
}


function showLoadingSpinner() {
  var spinner = document.getElementById('loading-spinner');
  spinner.style.display = 'flex';
}

function hideLoadingSpinner() {
  var spinner = document.getElementById('loading-spinner');
  spinner.style.display = 'none';
}


function displayResponse(response) {
  // Get the result container element
  // resultContainer.style.display = "flex"
  resultContainer.style.cssText = `
    display: flex;
    flex-direction: column;
    background-color: transparent;
    /* Add more styles here */
`;
  resultContainer.style.marginTop = "22px"
  // Clear the container
  resultContainer.innerHTML = '';

  // Create the disease element
  var diseaseElement = document.createElement('p');
  diseaseElement.textContent = 'Disease: ' + response.disease;
  diseaseElement.style.color = 'white';
  diseaseElement.style.marginTop = '7px';

  // Create the accuracy element
  var accuracyElement = document.createElement('p');
  accuracyElement.textContent = 'Accuracy: ' + response.accuracy + " %";
  accuracyElement.style.color = 'white';
  accuracyElement.style.marginTop = '7px';

  // Create the medicine element
  var medicineElement = document.createElement('p');
  medicineElement.textContent = 'Medicine: ' + response.medicine;
  medicineElement.style.color = 'white';
  medicineElement.style.marginTop = '7px';

  // Append the elements to the container
  resultContainer.appendChild(diseaseElement);
  resultContainer.appendChild(accuracyElement);
  resultContainer.appendChild(medicineElement);

  var mapButton = document.createElement("button");
  mapButton.className = "mapButton";
  mapButton.innerHTML = "Look for Clinics";
  var body = document.getElementsByTagName("body")[0];
  body.appendChild(mapButton);

  mapButton.addEventListener("click", function () {
    //window.open(map.html);
    window.open('https://www.google.com/maps/search/Pharmacies');
  });

  //document.getElementById(results).hidden=true;
}

// Display Data
function displayResponseData(response) {

  dummyResult.style.display = "none"
  result.style.display = "block"

  const disease = document.getElementById("disease")
  const accuracy = document.getElementById("accuracy")
  const medicine = document.getElementById("medicine")

  disease.innerHTML = response?.disease
  accuracy.innerHTML = response?.accuracy
  medicine.innerHTML = response?.medicine

  hideLoadingSpinner()

}

function displayError(message) {
  // Get the error container element
  var errorContainer = document.getElementById('error-container');

  // Set the error message
  // Clear previous error messages
  errorContainer.innerHTML = '';

  // Create the <h4> element
  var errorMessageElement = document.createElement('h4');

  // Apply styles to the <h4> element
  errorContainer.style.marginTop = '55px';
  errorMessageElement.style.color = 'red';
  errorMessageElement.style.backgroundColor = 'transparent';



  errorMessageElement.textContent = message;

  // Append the <h4> element to the error container
  errorContainer.appendChild(errorMessageElement);


}



function submitForm() {
  var form = document.getElementById('uploadForm');
  var formData = new FormData(form);

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/detect', true);
  xhr.onload = function () {
    if (xhr.status === 200) {
      alert(xhr.responseText);
    } else {
      alert('Error occurred while uploading the file.');
    }
  };
  xhr.send(formData);
}


async function detectFunction() {
  // Show loading spinner
  showLoadingSpinner();

  const username = sessionStorage.getItem("sdd_user")

  // Get the form and the selected file
  var fileInput = document.getElementById('upload');
  const fbImage = await uploadFirebaseImage(fileInput.files[0], username)

  // Create a FormData object and append the selected file
  var formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('username', username);
  formData.append('image', fbImage);

  // Send a POST request to the server
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/detect', true);
  xhr.onload = function () {
    if (xhr.status === 200) {
      // Hide loading spinner
      hideLoadingSpinner();

      // Parse the response JSON
      var response = JSON.parse(xhr.responseText);

      resultBtn.style.display = "none"
      document.getElementById("seeDoctors").style.display = "block"

      // Display the response
      displayResponseData(response);

    } else {
      // Hide loading spinner
      hideLoadingSpinner();

      var response = JSON.parse(xhr.responseText);
      // Show an error message
      displayError('Error: ' + response.message);
      setTimeout(() => {
        displayError('');

      }, 1000);
    }
  };
  xhr.send(formData);
}


async function uploadFirebaseImage(file, name){
  const path = `${name}/${Date.now()}-${file.name.split('.')[0]}.jpg`
  const imgUrlRef = ref(storage,path)
  await uploadBytes(imgUrlRef,file)
  const imgUrl = await getDownloadURL(imgUrlRef)

  return imgUrl;
}