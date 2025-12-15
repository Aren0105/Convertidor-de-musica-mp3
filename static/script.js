document.getElementById('btnConvert').addEventListener('click', async () => {
    const url = document.getElementById('url').value;
    const format = document.querySelector('input[name="format"]:checked').value;
    const btn = document.getElementById('btnConvert');
    const loader = document.getElementById('loader');

    if (!url) {
        alert("Por favor, ingresa una URL válida.");
        return;
    }

    // Ocultar botón y mostrar cargando
    btn.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, format: format })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Falló la conversión');
        }

        // --- INICIO DE LA CORRECCIÓN DEL NOMBRE ---
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');

        // 1. Intentamos leer la etiqueta que manda el servidor
        const disposition = response.headers.get('Content-Disposition');

        // 2. Nombre por defecto (por si todo falla)
        let filename = `cancion_descargada.${format}`;

        // 3. Lógica mejorada para extraer el nombre real
        if (disposition && disposition.includes('filename=')) {
            // Cortamos el texto justo después de "filename="
            let rawName = disposition.split('filename=')[1];
            // Si hay un punto y coma después (a veces pasa), lo quitamos
            if (rawName.includes(';')) {
                rawName = rawName.split(';')[0];
            }
            // Quitamos comillas si las tiene
            filename = rawName.replace(/['"]/g, '').trim();
        }

        a.href = downloadUrl;
        a.download = filename; // Aquí asignamos el nombre corregido
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);
        // --- FIN DE LA CORRECCIÓN ---

    } catch (e) {
        alert("Error: " + e.message);
    } finally {
        // Restaurar la interfaz
        btn.classList.remove('hidden');
        loader.classList.add('hidden');
    }
});