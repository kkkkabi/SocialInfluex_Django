function handleFiles(event) {
    var fileList = document.getElementById('uploadFileLists');
    fileList.innerHTML = ''; // Clear any previous content
    
    var files = event.target.files;

    for (var i = 0; i < files.length; i++) {
        var file = files[i];

        // Create an <img> element to display the image
        var img = document.createElement('img');
        img.classList.add('upload-images'); // Corrected class name
        fileList.appendChild(img);

        // Create a FileReader object to read the file as a data URL
        var reader = new FileReader();
        reader.onload = (function(image) {
            return function(e) {
                image.src = e.target.result; // Set the data URL as the image source
            };
        })(img);
        reader.readAsDataURL(file); // Read the file as a data URL
    }

    // // Include CSRF token in form data before submission
    // var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    // var form = document.querySelector('form');
    // var formData = new FormData(form);
    // formData.append('csrfmiddlewaretoken', csrfToken); // Append CSRF token to form data

    // // Perform form submission with updated form data
    // var xhr = new XMLHttpRequest();
    // xhr.open('POST', form.action);
    // xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    // xhr.onload = function() {
    //     // Handle response
    //     console.log(xhr.responseText);
    // };
    // xhr.send(formData);
}



// function previewImage(event) {
//     var preview = document.querySelector("#uploadFileLists");
//     if(this.files){
//         [].forEach.call(this.files, readAndPreview);

//         function readAndPreview(file){
//             if(!/\.(jpe?g|png|svg|gif)$/i.test(file.name)){
//                 return alert(file.name + "is not image file.");
//             }
//             var reader = new FileReader();
//             reader.addEventListener("load", function(){
//                 var image = new Image();
//                 image.title = file.name;
//                 image.src = this.result;
//                 preview.appendChild(image);

//             })

//             reader.readAsDataURL(file);

//         } 
//     }
//  }

// document.querySelector("#uploadFiles").addEventListener("change", previewImage)