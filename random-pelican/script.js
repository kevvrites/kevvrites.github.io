document.getElementById('newImage').addEventListener('click', function() {
  fetch('https://api.unsplash.com/photos/random?query=pelican&client_id=50JaSmCkjZSFtUms6eOWi3NQFZDAAdNCHURx9cewjmg')
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      document.getElementById('pelicanImage').src = data.urls.small;
    })
    .catch(function(error) {
      console.error('Error:', error);
    });
});
