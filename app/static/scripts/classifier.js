document.getElementById('imageInput').addEventListener('change', function() {
    const form = document.getElementById("upload-form");
    const formData = new FormData(form);

    console.log("IN EVENT LISTENER")
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Upload failed.');
        return response.text(); 
    })
    .then(result => {
        console.log('Upload successful:', result);
    })
    .catch(error => {
        console.error('Error:', error);
    });
})