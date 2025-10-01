let image1File = null;
let image2File = null;

const image1Input = document.getElementById('image1');
const image2Input = document.getElementById('image2');
const upload1Div = document.getElementById('upload1');
const upload2Div = document.getElementById('upload2');
const uploadBtn = document.getElementById('uploadBtn');
const resultContainer = document.getElementById('resultContainer');
const resultBox = document.getElementById('resultBox');
const resultIcon = document.getElementById('resultIcon');
const resultTitle = document.getElementById('resultTitle');
const resultText = document.getElementById('resultText');

upload1Div.addEventListener('click', () => image1Input.click());
upload2Div.addEventListener('click', () => image2Input.click());

image1Input.addEventListener('change', (e) => handleImageSelect(e.target.files[0], 1));
image2Input.addEventListener('change', (e) => handleImageSelect(e.target.files[0], 2));

function handleImageSelect(file, imageNumber) {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        const previewHTML = `
            <div>
                <div class="relative overflow-hidden aspect-[4/3]">
                    <img src="${e.target.result}" alt="Preview ${imageNumber}" class="w-full h-full object-cover">
                </div>
                <div class="p-6 border-t-4 border-neutral-900 bg-white">
                    <div class="flex items-center gap-3">
                        <svg class="w-6 h-6 text-neutral-900 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                        <span class="font-bold text-neutral-900 truncate">${file.name}</span>
                    </div>
                </div>
            </div>
        `;

        if (imageNumber === 1) {
            image1File = file;
            document.getElementById('preview1Container').innerHTML = previewHTML;
            upload1Div.classList.add('border-neutral-900');
            upload1Div.classList.remove('border-neutral-200');
        } else {
            image2File = file;
            document.getElementById('preview2Container').innerHTML = previewHTML;
            upload2Div.classList.add('border-neutral-900');
            upload2Div.classList.remove('border-neutral-200');
        }

        checkUploadReady();
    };
    reader.readAsDataURL(file);
    
    resultContainer.style.display = 'none';
}

function checkUploadReady() {
    if (image1File && image2File) {
        uploadBtn.disabled = false;
        uploadBtn.className = 'group relative px-16 py-6 border-4 font-black text-xl transition-all duration-200 bg-neutral-900 border-neutral-900 text-white hover:translate-x-1 hover:translate-y-1 hover:shadow-none shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]';
    }
}

uploadBtn.addEventListener('click', async () => {
    if (!image1File || !image2File) return;

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `
        <span class="flex items-center gap-4">
            <div class="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
            PROCESSING...
        </span>
    `;

    const formData = new FormData();
    formData.append('image1', image1File);
    formData.append('image2', image2File);

    const backendUrl = 'https://your-python-backend.pythonanywhere.com/process-images';

    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            showResult(JSON.stringify(data, null, 2), true);
        } else {
            showResult('Error processing images. Please try again.', false);
        }
    } catch (error) {
        showResult(`Network error: ${error.message}`, false);
    }

    uploadBtn.innerHTML = `
        <span class="flex items-center gap-4">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>
            </svg>
            UPLOAD & PROCESS
        </span>
    `;
    checkUploadReady();
});

function showResult(text, isSuccess) {
    resultContainer.style.display = 'block';
    resultText.textContent = text;

    if (isSuccess) {
        resultBox.className = 'bg-white border-4 border-green-500 p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]';
        resultIcon.className = 'w-8 h-8 text-green-600';
        resultTitle.className = 'text-2xl font-black text-green-600';
        resultTitle.textContent = 'SUCCESS';
        resultIcon.innerHTML = '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>';
    } else {
        resultBox.className = 'bg-white border-4 border-red-500 p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]';
        resultIcon.className = 'w-8 h-8 text-red-600';
        resultTitle.className = 'text-2xl font-black text-red-600';
        resultTitle.textContent = 'ERROR';
        resultIcon.innerHTML = '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>';
    }
}
