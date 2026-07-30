/**
 * 3_logos_institucionales.js
 * Define las rutas locales de los logos institucionales y las precarga
 * en memoria como objetos Image del navegador. jsPDF necesita la imagen
 * YA cargada (no acepta una ruta de archivo directamente); por eso este
 * módulo expone una promesa cacheada que pdf_generator.js espera antes
 * de dibujar el encabezado.
 *
 * Los archivos deben existir en: assets/img/Planeacion_dorado.png
 *                                 assets/img/CEAA_dorado.png
 * (Dash los sirve automáticamente por estar dentro de /assets).
 */

window.LOGOS_INSTITUCIONALES = {
    planeacion: {
        path: "/assets/Imagenes/Planeacion_dorado.png",
        anchoNatural: 1035,
        altoNatural: 178,
        img: null,
    },
    ceaa: {
        path: "/assets/Imagenes/CEAA_dorado.png",
        anchoNatural: 541,
        altoNatural: 214,
        img: null,
    },
};

function _cargarImagenLocal(ruta) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error(`No se pudo cargar el logo: ${ruta}`));
        img.src = ruta;
    });
}

/**
 * Precarga (una sola vez, con cache) todos los logos definidos arriba.
 * Devuelve el mismo objeto LOGOS_INSTITUCIONALES, ahora con "img" listo
 * para usarse en doc.addImage(logo.img, ...).
 */
window.precargarLogosInstitucionales = async function () {
    const logos = window.LOGOS_INSTITUCIONALES;
    const claves = Object.keys(logos);

    await Promise.all(
        claves.map(async (clave) => {
            if (!logos[clave].img) {
                try {
                    logos[clave].img = await _cargarImagenLocal(logos[clave].path);
                } catch (err) {
                    console.error(err);
                    logos[clave].img = null; // el reporte se genera igual, sin ese logo
                }
            }
        })
    );

    return logos;
};

// Precarga "en caliente" apenas se carga la página, para que al hacer clic
// en "Descargar PDF" los logos ya estén en cache y no haya demora.
window.precargarLogosInstitucionales();
