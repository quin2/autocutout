/* If you're feeling fancy you can add interactivity 
    to your site with Javascript */

// prints "hi" in the browser's dev tools console
function mySubmitFunction(e) {
  e.preventDefault();
  
  var status = document.getElementById("status")
  status.innerHTML = "Loading..."
  
  let photo = document.getElementById("image-file").files[0];
  let formData = new FormData();
  
  formData.append("file", photo);
  fetch('../v1/matisse/', {
    body: formData,
    method: "POST",
    
  }).then(response => response.json())
    .then(data => {
    
    status.innerHTML = "Done :D"
    
    var mySVG = data.svg;
    mySVG = mySVG.replace(/\"/g, "\""); 
    
    console.log(mySVG)
    
    var space = document.getElementById("svgSpace");
    space.innerHTML = mySVG;
    
  });

  
  return false;
}
