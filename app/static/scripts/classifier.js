document.getElementById('imageInput').addEventListener('change', function(event) {
    const form = document.getElementById("upload-form");
    const file = event.target.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append('imageInput', file);

    // Upload the file to the server
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Upload failed.');
        return response.json(); 
    })
    .then(data => {
        const filename = data.filename;

        document.getElementById('upload-placeholder').style.display = 'none';

        const imagePreview = document.getElementById('image-preview');

        const wrapper = document.createElement('div');
        wrapper.className = 'image-wrapper';

        const img = document.createElement('img');
        img.src = `/static/uploads/${filename}`;
        img.alt = "Uploaded Image";
        img.className = 'preview-image';

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '×';
        deleteBtn.className = 'delete-button';

        deleteBtn.onclick = function() {
            fetch('/delete-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: filename })
            })
            .then(response => {
                if (!response.ok) throw new Error('Delete failed.');
                
                wrapper.remove(); 
                document.getElementById('imageInput').value = '';  
                
                const preview = document.getElementById('image-preview');
                if (preview.children.length === 0) {
                    document.getElementById('upload-placeholder').style.display = 'flex';
                }
            })
            .catch(error => {
                console.error('Error deleting image:', error);
            });
        };

        wrapper.appendChild(deleteBtn);
        wrapper.appendChild(img);
        imagePreview.appendChild(wrapper);
    })
    .catch(error => {
        console.error('Error uploading image:', error);
    });
});
