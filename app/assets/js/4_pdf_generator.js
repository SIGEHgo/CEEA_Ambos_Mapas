/**
 * 4_pdf_generator.js
 * Generación de reportes PDF en el cliente usando jsPDF + jspdf-autotable,
 * con la identidad institucional (vino/dorado) y los logos de
 * Planeación y CEAA, siguiendo el mismo estilo que reporte_grafica.js.
 *
 * Requiere (cargados antes, ver assets/js):
 *   1_jspdf.umd.min.js
 *   2_jspdf.plugin.autotable.min.js
 *   3_logos_institucionales.js   -> window.LOGOS_INSTITUCIONALES / precargarLogosInstitucionales()
 *
 * NOTA: la función es "async" porque espera a que los logos (cargados
 * desde assets/img/ como archivos locales, no base64) estén listos en
 * memoria antes de dibujarlos. Llamarla desde el clientside_callback
 * de Dash normalmente NO requiere "await": se dispara y, cuando termina,
 * el navegador descarga el PDF solo.
 *
 * Uso desde un clientside_callback de Dash:
 *   window.generarReportePDF(payload)
 *
 * Forma esperada de "payload" (construido en Python):
 * {
 *   nombreArchivo: "Reporte_Pozo_123",
 *   titulo: "Fuente de Abastecimiento: Pozo profundo",
 *   subtitulos: ["Municipio: Ensenada", "Localidad: El Sauzal"],
 *   tarjetas: [                                  // OPCIONAL
 *     { titulo: "Número de pozos", valor: "12", sub: "en el municipio" }
 *   ],
 *   tablas: [
 *     {
 *       titulo: "Detalle del pozo",
 *       columnas: ["Parámetro", "Valor"],
 *       filas: [["Profundidad", "120 m"], ["Caudal", "15 lps"]]
 *     }
 *   ],
 *   fuente: "Comisión Estatal del Agua y Alcantarillado (CEAA)"   // OPCIONAL
 * }
 */

async function generarReportePDF(payload) {
    if (!payload) {
        console.warn("generarReportePDF: no hay datos para generar el PDF.");
        return;
    }

    // Espera a que los logos estén cargados en memoria (normalmente ya lo
    // están, gracias a la precarga en caliente de 3_logos_institucionales.js;
    // este await solo bloquea si el usuario hace clic muy rápido tras cargar
    // la página).
    const logos = await window.precargarLogosInstitucionales();

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: "pt", format: "letter" });

    const W = doc.internal.pageSize.getWidth();
    const H = doc.internal.pageSize.getHeight();
    const margen = 40;
    let y = 0;

    // ── Paleta institucional (misma que reporte_grafica.js) ─────────────────
    const vino      = [98, 17, 50];
    const dorado    = [179, 142, 93];
    const rosado    = [243, 194, 213];
    const grisClaro = [245, 245, 245];
    const blanco    = [255, 255, 255];
    const negro     = [30, 30, 30];

    const txt = (v) => (v === null || v === undefined || v === "" ? "N/A" : String(v));

    // ══════════════════════════════════════════════════════════════════════
    // ENCABEZADO
    // ══════════════════════════════════════════════════════════════════════
    const alturaEncabezado = 70;
    doc.setFillColor(...vino);
    doc.rect(0, 0, W, alturaEncabezado, "F");

    // Franja dorada inferior del encabezado (detalle institucional)
    doc.setFillColor(...dorado);
    doc.rect(0, alturaEncabezado - 3, W, 3, "F");

    doc.setTextColor(...blanco);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text(payload.tituloEncabezado || "Reporte de Acciones de Desinfección", margen, 36);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    const fecha = new Date().toLocaleDateString("es-MX", {
        year: "numeric", month: "long", day: "numeric",
    });
    doc.text(`Generado el ${fecha}`, margen, 52);


    // ── Logos (Planeación y CEAA), alineados a la derecha ───────────────────
    const alturaLogo = 24;
    const separacionLogos = 14;
    let xCursorLogo = W - margen;

    if (logos.ceaa && logos.ceaa.img) {
        const anchoCEAA = (logos.ceaa.anchoNatural / logos.ceaa.altoNatural) * alturaLogo;
        const xCEAA = xCursorLogo - anchoCEAA;
        const yCEAA = (alturaEncabezado - alturaLogo) / 2 - 2;
        doc.addImage(logos.ceaa.img, "PNG", xCEAA, yCEAA, anchoCEAA, alturaLogo);
        xCursorLogo = xCEAA - separacionLogos;
    }

    if (logos.planeacion && logos.planeacion.img) {
        const anchoPlaneacion = (logos.planeacion.anchoNatural / logos.planeacion.altoNatural) * alturaLogo;
        const xPlaneacion = xCursorLogo - anchoPlaneacion;
        const yPlaneacion = (alturaEncabezado - alturaLogo) / 2 - 2;
        doc.addImage(logos.planeacion.img, "PNG", xPlaneacion, yPlaneacion, anchoPlaneacion, alturaLogo);
    }

    y = alturaEncabezado + 20;

    // ══════════════════════════════════════════════════════════════════════
    // TÍTULO Y SUBTÍTULOS DEL REPORTE
    // ══════════════════════════════════════════════════════════════════════
    doc.setTextColor(...vino);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text(txt(payload.titulo), margen, y);
    y += 16;

    if (Array.isArray(payload.subtitulos) && payload.subtitulos.length) {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(...negro);
        payload.subtitulos.forEach((linea) => {
            if (!linea) return;
            doc.text(txt(linea), margen, y);
            y += 13;
        });
    }
    y += 6;

    // ══════════════════════════════════════════════════════════════════════
    // TARJETAS DE RESUMEN (opcional)
    // ══════════════════════════════════════════════════════════════════════
    if (Array.isArray(payload.tarjetas) && payload.tarjetas.length) {
        const n = Math.min(payload.tarjetas.length, 4);
        const gap = 6;
        const tarjW = (W - margen * 2 - gap * (n - 1)) / n;
        const tarjH = 44;

        payload.tarjetas.slice(0, n).forEach((t, i) => {
            const x = margen + i * (tarjW + gap);

            doc.setFillColor(...rosado);
            doc.roundedRect(x, y, tarjW, tarjH, 3, 3, "F");
            doc.setFillColor(...vino);
            doc.rect(x, y, tarjW, 10, "F");

            doc.setTextColor(...blanco);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(8);
            doc.text(txt(t.titulo), x + tarjW / 2, y + 7, { align: "center" });

            doc.setTextColor(...vino);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(14);
            doc.text(txt(t.valor), x + tarjW / 2, y + 26, { align: "center" });

            if (t.sub) {
                doc.setTextColor(...negro);
                doc.setFont("helvetica", "normal");
                doc.setFontSize(7.5);
                doc.text(txt(t.sub), x + tarjW / 2, y + 37, { align: "center" });
            }
        });

        y += tarjH + 20;
    }

    // ══════════════════════════════════════════════════════════════════════
    // TABLAS DE DATOS (autoTable con estilo vino/dorado)
    // ══════════════════════════════════════════════════════════════════════
    (payload.tablas || []).forEach((tabla) => {
        if (!tabla || !tabla.filas || !tabla.filas.length) return;

        // Barra de título de sección, estilo "1. Datos Generales"
        if (tabla.titulo) {
            doc.setFillColor(...vino);
            doc.rect(margen, y, W - margen * 2, 20, "F");
            doc.setTextColor(...blanco);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(10);
            doc.text(txt(tabla.titulo), margen + 8, y + 14);
            y += 20;
        }

        doc.autoTable({
            startY: y,
            head: [tabla.columnas || []],
            body: tabla.filas,
            margin: { left: margen, right: margen },
            styles: { fontSize: 8.5, cellPadding: 5, textColor: negro, lineColor: vino, lineWidth: 0.3 },
            headStyles: { fillColor: dorado, textColor: blanco, fontStyle: "bold" },
            alternateRowStyles: { fillColor: grisClaro },
            tableLineColor: vino,
            tableLineWidth: 0.3,
        });

        y = doc.lastAutoTable.finalY + 22;

        // Salto de página si ya no cabe una tabla siguiente razonable
        if (y > H - 100) {
            doc.addPage();
            y = 30;
        }
    });

    // ══════════════════════════════════════════════════════════════════════
    // PIE DE PÁGINA institucional (todas las páginas)
    // ══════════════════════════════════════════════════════════════════════
    // Normas aplicables al reporte. Se muestran de forma discreta: fuente
    // pequeña (6.5pt) y color dorado (menos contrastante que el blanco del
    // resto del pie), centradas en una franja delgada justo encima del pie
    // principal. Editable vía payload.normasAplicables (array de strings);
    // si no se manda, se usan las normas por defecto.
    const normasAplicables = Array.isArray(payload.normasAplicables) && payload.normasAplicables.length
        ? payload.normasAplicables
        : ["ISO 9001:2015", "ISO/IEC 17025:2017"];
    const textoNormas = normasAplicables.join("  ·  ");

    const alturaPie = 26;
    const totalPaginas = doc.internal.getNumberOfPages();
    for (let i = 1; i <= totalPaginas; i++) {
        doc.setPage(i);

        doc.setFillColor(...vino);
        doc.rect(0, H - alturaPie, W, alturaPie, "F");
        doc.setFillColor(...dorado);
        doc.rect(0, H - alturaPie, W, 2, "F");

        // Línea discreta de normas aplicables, justo por encima del pie
        doc.setTextColor(...dorado);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(6.5);
        doc.text(textoNormas, W / 2, H - alturaPie - 4, { align: "center" });

        doc.setTextColor(...blanco);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7.5);
        doc.text(
            txt(payload.fuente || "Comisión Estatal del Agua y Alcantarillado (CEAA)"),
            margen,
            H - 10
        );
        doc.text(
            `Página ${i} de ${totalPaginas}`,
            W - margen,
            H - 10,
            { align: "right" }
        );
    }

    doc.save(`${payload.nombreArchivo || "reporte"}.pdf`);
}

// Expuesto globalmente para ser llamado desde clientside_callback de Dash
window.generarReportePDF = generarReportePDF;