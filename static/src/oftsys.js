document.addEventListener("DOMContentLoaded", () => {
    // Seleciona todos os elementos essenciais no início
    const elements = {
        analyzeBtn: document.getElementById("analyzeBtn"),
        clearBtn: document.getElementById("clearBtn"),
        fileInput: document.getElementById("medicalFileInput"),
        dropZone: document.getElementById("dropZone"),
        thumbnailContainer: document.getElementById("thumbnailContainer")
    };

    // Verifica se todos os elementos foram encontrados
    for (const key in elements) {
        if (!elements[key]) {
            console.error(`Erro Crítico: Elemento '${key}' não foi encontrado no HTML.`);
            return;
        }
    }

    let selectedFiles = []; // Array para armazenar os arquivos selecionados

    /**
     * Atualiza a interface do usuário com base nos arquivos selecionados.
     */
    function updateUI() {
        elements.thumbnailContainer.innerHTML = ''; // Limpa as miniaturas existentes
        
        selectedFiles.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    // Cria a miniatura da imagem
                    const thumbnailWrapper = document.createElement('div');
                    thumbnailWrapper.className = 'thumbnail-preview';
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    
                    const overlay = document.createElement('div');
                    overlay.className = 'thumbnail-overlay';
                    overlay.textContent = file.name;

                    thumbnailWrapper.appendChild(img);
                    thumbnailWrapper.appendChild(overlay);
                    elements.thumbnailContainer.appendChild(thumbnailWrapper);
                };
                reader.readAsDataURL(file);
            }
        });

        // Atualiza o estado da drop-zone e do botão de análise
        if (selectedFiles.length > 0) {
            elements.dropZone.classList.add('has-files');
            elements.analyzeBtn.disabled = false;
        } else {
            elements.dropZone.classList.remove('has-files');
            elements.analyzeBtn.disabled = true;
        }
    }

    /**
     * Limpa toda a seleção de arquivos e reseta a interface.
     */
    function clearSelection() {
        selectedFiles = [];
        elements.fileInput.value = ''; // Reseta o input de arquivo
        updateUI(); // Atualiza a UI para o estado inicial
    }

    /**
     * Adiciona novos arquivos à seleção.
     * @param {FileList} newFiles - A lista de novos arquivos a serem adicionados.
     */
    function handleFileSelection(newFiles) {
        // Converte FileList para Array e adiciona aos arquivos existentes
        selectedFiles.push(...Array.from(newFiles));
        updateUI();
    }

    /**
     * Envia as imagens para o backend para análise.
     * @param {File[]} files - A lista de arquivos a serem enviados.
     */
    async function sendImages(files) {
        if (files.length === 0) return;

        elements.analyzeBtn.disabled = true;
        elements.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ANALISANDO...';

        const formData = new FormData();
        files.forEach(file => {
            formData.append("files[]", file);
        });

        try {
            const response = await fetch("/predict", { method: "POST", body: formData });

            // Agora o servidor devolve HTML completo, então usamos response.text()
            const html = await response.text();

            // Substitui o conteúdo atual da página pelo HTML retornado
            document.open();
            document.write(html);
            document.close();

        } catch (error) {
            console.error("Erro ao enviar imagens:", error);
            alert(`Erro na predição: ${error.message}`);
        } finally {
            // Caso ocorra erro antes da troca de página, restaura o botão
            elements.analyzeBtn.disabled = false;
            elements.analyzeBtn.innerHTML = '<i class="fas fa-search-plus"></i> ANALISAR IMAGENS';
        }
    }


    // --- Vincula os Event Listeners ---
    elements.analyzeBtn.addEventListener("click", () => sendImages(selectedFiles));
    elements.clearBtn.addEventListener("click", clearSelection);
    elements.dropZone.addEventListener("click", () => elements.fileInput.click());
    elements.fileInput.addEventListener("change", () => handleFileSelection(elements.fileInput.files));

    // Eventos de Drag & Drop
    elements.dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        elements.dropZone.classList.add("drag-over");
    });
    elements.dropZone.addEventListener("dragleave", () => {
        elements.dropZone.classList.remove("drag-over");
    });
    elements.dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        elements.dropZone.classList.remove("drag-over");
        handleFileSelection(e.dataTransfer.files);
    });
});