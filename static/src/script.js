document.addEventListener('DOMContentLoaded', function() {
  const videos = document.querySelectorAll('.hero-video video');
  let currentVideo = 0;

  function changeVideo() {
    videos[currentVideo].classList.remove('active');
    currentVideo = (currentVideo + 1) % videos.length;
    videos[currentVideo].classList.add('active');
  }

  // Troca o vídeo a cada 5 segundos (ajuste o tempo)
  setInterval(changeVideo, 5000);
});

document.addEventListener("DOMContentLoaded", function() {
    const analyzeBtn = document.getElementById("analyzeBtn");

    analyzeBtn.addEventListener("click", async () => {
        const fileInput = document.getElementById("medicalFileInput");

        if (fileInput.files.length === 0) {
            alert("Selecione uma imagem primeiro!");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            console.log(data);

            // Atualiza confiança do Keras
            document.getElementById("confidenceValue").innerText =
                (data.keras.confidence * 100).toFixed(1) + "%";

            document.getElementById("taxaDeErro").innerText =
                ((100 - data.keras.confidence * 100)).toFixed(1) + "%";
            // Aqui você pode adicionar para YOLO também
            // exemplo: console.log("YOLO:", data.yolo);

        } catch (error) {
            console.error("Erro ao enviar imagem:", error);
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("medicalFileInput");

    // Clicar na zona abre o seletor de arquivos
    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    // Opcional: destacar área quando arrastar
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("drag-over");
    });

    // Se soltar imagem na área
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("drag-over");
        fileInput.files = e.dataTransfer.files;
    });
});

document.getElementById("analyzeBtn").addEventListener("click", () => {
    const fileInput = document.getElementById("medicalFileInput");
    if (fileInput.files.length === 0) {
        fileInput.click(); // abre modal para selecionar
    } else {
        // aqui chama a função de envio para o backend
        enviarImagem();
    }
});