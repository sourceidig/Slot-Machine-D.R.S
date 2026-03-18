// OCR Captura de Cámara
// Sistema de captura y procesamiento OCR para lecturas de máquinas

;(() => {
  // Variables globales
  let stream = null
  let video = null
  let canvas = null
  let capturedImage = null
  const bootstrap = window.bootstrap 

  // Inicializar al cargar el DOM
  document.addEventListener("DOMContentLoaded", () => {
    // Obtener elementos del DOM
    video = document.getElementById("video")
    canvas = document.getElementById("canvas")
    capturedImage = document.getElementById("capturedImage")

    const btnCapturarCamara = document.getElementById("btnCapturarCamara")
    const btnTomarFoto = document.getElementById("btnTomarFoto")
    const btnProcesarFoto = document.getElementById("btnProcesarFoto")
    const btnRetomar = document.getElementById("btnRetomar")
    const btnCerrarModal = document.getElementById("btnCerrarModal")
    const cameraModal = document.getElementById("cameraModal")

    // Event Listeners
    if (btnCapturarCamara) {
      btnCapturarCamara.addEventListener("click", abrirCamara)
    }

    if (btnTomarFoto) {
      btnTomarFoto.addEventListener("click", tomarFoto)
    }

    if (btnProcesarFoto) {
      btnProcesarFoto.addEventListener("click", procesarConOCR)
    }

    if (btnRetomar) {
      btnRetomar.addEventListener("click", retomarFoto)
    }

    if (btnCerrarModal) {
      btnCerrarModal.addEventListener("click", cerrarCamara)
    }

    // Cerrar cámara cuando se cierra el modal
    if (cameraModal) {
      cameraModal.addEventListener("hidden.bs.modal", cerrarCamara)
    }
  })

  // Función para abrir la cámara
  function abrirCamara() {
    const modal = new bootstrap.Modal(document.getElementById("cameraModal"))
    modal.show()

    // Resetear estado
    video.style.display = "none"
    capturedImage.style.display = "none"
    canvas.style.display = "none"
    document.getElementById("processingSpinner").style.display = "none"
    document.getElementById("btnTomarFoto").style.display = "inline-block"
    document.getElementById("btnProcesarFoto").style.display = "none"
    document.getElementById("btnRetomar").style.display = "none"

    // Solicitar acceso a la cámara
    const constraints = {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: "environment", // Usar cámara trasera en móviles
      },
    }

    navigator.mediaDevices
      .getUserMedia(constraints)
      .then((mediaStream) => {
        stream = mediaStream
        video.srcObject = stream
        video.style.display = "block"
        mostrarEstado("Cámara lista. ubique el dispositivo entre 15 y 30 cm de la pantalla de la máquina.", "info")
      })
      .catch((err) => {
        console.error("Error al acceder a la cámara:", err)
        mostrarEstado("Error: No se pudo acceder a la cámara. " + err.message, "danger")
      })
  }

  // Función para tomar la foto
  function tomarFoto() {
    if (!stream) {
      mostrarEstado("Error: La cámara no está activa", "danger")
      return
    }

    // Configurar el canvas con las dimensiones del video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Capturar el frame actual del video
    const context = canvas.getContext("2d")
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Convertir a imagen y mostrar
    const imageDataUrl = canvas.toDataURL("image/jpeg", 0.9)
    capturedImage.src = imageDataUrl
    capturedImage.style.display = "block"

    // Ocultar video y mostrar botones
    video.style.display = "none"
    document.getElementById("btnTomarFoto").style.display = "none"
    document.getElementById("btnProcesarFoto").style.display = "inline-block"
    document.getElementById("btnRetomar").style.display = "inline-block"

    mostrarEstado('Foto capturada. Presiona "Procesar con OCR" para extraer los datos.', "success")
  }

  // Función para retomar foto
  function retomarFoto() {
    capturedImage.style.display = "none"
    video.style.display = "block"
    document.getElementById("btnTomarFoto").style.display = "inline-block"
    document.getElementById("btnProcesarFoto").style.display = "none"
    document.getElementById("btnRetomar").style.display = "none"
    mostrarEstado("Cámara lista. Ubique el dispositivo entre 15 y 30 cm de la pantalla de la máquina.", "info")
  }

  // Función para procesar la imagen con OCR
  function procesarConOCR() {
    // Ocultar imagen y mostrar spinner
    capturedImage.style.display = "none"
    document.getElementById("processingSpinner").style.display = "block"
    document.getElementById("btnProcesarFoto").disabled = true
    document.getElementById("btnRetomar").disabled = true

    mostrarEstado("Procesando imagen...", "info")

    // Convertir canvas a blob — PNG lossless para mejor calidad OCR
    canvas.toBlob(
      (blob) => {
        // Crear FormData para enviar la imagen
        const formData = new FormData()
        formData.append("imagen", blob, "captura.png")

        // Obtener CSRF token
        const csrftoken = getCookie("csrftoken")

        // Enviar al servidor
        fetch("/api/ocr-lectura/", {
          method: "POST",
          headers: {
            "X-CSRFToken": csrftoken,
          },
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            document.getElementById("processingSpinner").style.display = "none"

            if (data.success) {
              // Rellenar los campos del formulario
              document.getElementById("id_entrada").value = data.entrada
              document.getElementById("id_salida").value = data.salida
              document.getElementById("id_total").value = data.total

              const iconoConfianza = data.confianza === "alta" ? "✅" : data.confianza === "media" ? "⚠️" : "⚠️"
              const alertaTipo = data.confianza === "baja" ? "warning" : "success"
              mostrarEstado(
                `${iconoConfianza} Entrada: ${data.entrada} | Salida: ${data.salida} | Total: ${data.total}` +
                (data.confianza !== "alta" ? ` — Confianza ${data.confianza}, verifica los valores` : ""),
                alertaTipo,
              )

              // Cerrar modal después de 2 segundos
              setTimeout(() => {
                cerrarCamara()
                const modal = bootstrap.Modal.getInstance(document.getElementById("cameraModal"))
                if (modal) modal.hide()
              }, 2000)
            } else {
              // Mostrar error + lo que leyó el OCR para diagnóstico
              let msg = data.error || "No se pudieron extraer los datos"
              if (data.debug_texto && data.debug_texto !== "(sin texto)") {
                msg += `<br><small style="opacity:.7">OCR leyó: <em>${data.debug_texto}</em></small>`
              } else if (data.errores_ocr && data.errores_ocr.length > 0) {
                msg += `<br><small style="opacity:.7">Error técnico: ${data.errores_ocr[0]}</small>`
              } else {
                msg += `<br><small style="opacity:.7">Tesseract no detectó texto. Intenta más cerca y con luz.</small>`
              }
              mostrarEstadoHtml(msg, "danger")
              // Log completo en consola para diagnóstico
              console.log("OCR debug:", data)
              capturedImage.style.display = "block"
              document.getElementById("btnProcesarFoto").disabled = false
              document.getElementById("btnRetomar").disabled = false
            }
          })
          .catch((error) => {
            console.error("Error:", error)
            document.getElementById("processingSpinner").style.display = "none"
            mostrarEstado("Error de conexión: " + error.message, "danger")
            capturedImage.style.display = "block"
            document.getElementById("btnProcesarFoto").disabled = false
            document.getElementById("btnRetomar").disabled = false
          })
      },
      "image/png",
    )
  }

  // Función para cerrar la cámara
  function cerrarCamara() {
    if (stream) {
      const tracks = stream.getTracks()
      tracks.forEach((track) => track.stop())
      stream = null
    }

    if (video) {
      video.srcObject = null
    }
  }

  // Función para mostrar mensajes de estado (texto plano)
  function mostrarEstado(mensaje, tipo) {
    const statusDiv = document.getElementById("cameraStatus")
    statusDiv.className = `alert alert-${tipo} mt-3`
    statusDiv.textContent = mensaje
    statusDiv.style.display = "block"
  }

  // Función para mostrar mensajes con HTML (para debug del OCR)
  function mostrarEstadoHtml(mensaje, tipo) {
    const statusDiv = document.getElementById("cameraStatus")
    statusDiv.className = `alert alert-${tipo} mt-3`
    statusDiv.innerHTML = mensaje
    statusDiv.style.display = "block"
  }

  // Función para obtener cookie CSRF
  function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";")
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }
})()