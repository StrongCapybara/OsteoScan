document.addEventListener('DOMContentLoaded', function() {
    // X-ray upload elements
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const fileInfo = document.getElementById('fileInfo');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const resultStatus = document.getElementById('resultStatus');
    const resultConfidence = document.getElementById('resultConfidence');
    const resultRecommendation = document.getElementById('resultRecommendation');

    // X-ray upload handling
    uploadButton.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            fileInfo.textContent = `Selected file: ${file.name} (${fileSize}MB)`;
            uploadFile(file);
        }
    });

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Reset UI
        error.classList.add('d-none');
        results.classList.add('d-none');
        loadingIndicator.classList.remove('d-none');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('d-none');

            if (data.error) {
                showError(data.error);
                return;
            }

            showResults(data);
        })
        .catch(err => {
            loadingIndicator.classList.add('d-none');
            showError('An error occurred while processing the image.');
            console.error('Error:', err);
        });
    }

    function showResults(data) {
        results.classList.remove('d-none');

        const statusClass = data.result === 'positive' ? 'text-danger' : 'text-success';
        resultStatus.innerHTML = `
            <h4 class="${statusClass}">
                <i data-feather="${data.result === 'positive' ? 'alert-triangle' : 'check-circle'}"></i>
                ${data.condition}
            </h4>
        `;

        resultConfidence.innerHTML = `
            <div class="progress mb-2" style="height: 20px;">
                <div class="progress-bar" role="progressbar" 
                     style="width: ${data.confidence * 100}%;" 
                     aria-valuenow="${data.confidence * 100}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${Math.round(data.confidence * 100)}%
                </div>
            </div>
            <small class="text-muted">Confidence Level</small>
        `;

        resultRecommendation.innerHTML = `
            <div class="alert alert-info">
                <i data-feather="info"></i>
                ${data.recommendation}
            </div>
        `;

        feather.replace();
    }

    function showError(message) {
        error.textContent = message;
        error.classList.remove('d-none');
    }
});