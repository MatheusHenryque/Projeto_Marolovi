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