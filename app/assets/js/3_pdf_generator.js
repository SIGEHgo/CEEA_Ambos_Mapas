/**
 * pdf_generator.js
 * Generación de reportes PDF en el cliente usando jsPDF + jspdf-autotable.
 * Requiere que jsPDF y el plugin autoTable estén cargados antes (ver app.py:
 * external_scripts, o vendorizados en /assets/js/).
 *
 * Uso desde un clientside_callback de Dash:
 *   window.generarReportePDF(payload)
 *
 * Forma esperada de "payload" (construido en Python):
 * {
 *   nombreArchivo: "Reporte_Pozo_123",
 *   titulo: "Fuente de Abastecimiento: Pozo profundo",
 *   subtitulos: ["Municipio: Ensenada", "Localidad: El Sauzal"],
 *   tablas: [
 *     {
 *       titulo: "Detalle del pozo",
 *       columnas: ["Parámetro", "Valor"],
 *       filas: [["Profundidad", "120 m"], ["Caudal", "15 lps"]]
 *     }
 *   ]
 * }
 */

function generarReportePDF(payload) {
    if (!payload) {
        console.warn("generarReportePDF: no hay datos para generar el PDF.");
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: "pt", format: "letter" });

    const marginX = 40;
    const pageWidth = doc.internal.pageSize.getWidth();
    let cursorY = 0;

    // --- Encabezado institucional ---
    doc.setFillColor(15, 76, 129); // azul institucional (ajustar a la paleta real)
    doc.rect(0, 0, pageWidth, 68, "F");

    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(15);
    doc.text("Reporte de Acciones de Desinfección", marginX, 28);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    const fecha = new Date().toLocaleDateString("es-MX", {
        year: "numeric", month: "long", day: "numeric"
    });
    doc.text(`Generado el ${fecha}`, marginX, 46);

    cursorY = 92;

    // --- Título y subtítulos del reporte ---
    doc.setTextColor(25, 25, 25);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text(payload.titulo || "", marginX, cursorY);
    cursorY += 18;

    if (Array.isArray(payload.subtitulos)) {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(70, 70, 70);
        payload.subtitulos.forEach((linea) => {
            if (!linea) return;
            doc.text(String(linea), marginX, cursorY);
            cursorY += 14;
        });
        cursorY += 8;
    }

    // --- Tablas de datos ---
    (payload.tablas || []).forEach((tabla) => {
        if (!tabla || !tabla.filas || !tabla.filas.length) return;

        if (tabla.titulo) {
            doc.setFont("helvetica", "bold");
            doc.setFontSize(11);
            doc.setTextColor(15, 76, 129);
            doc.text(tabla.titulo, marginX, cursorY);
            cursorY += 10;
        }

        doc.autoTable({
            startY: cursorY,
            head: [tabla.columnas || []],
            body: tabla.filas,
            margin: { left: marginX, right: marginX },
            styles: { fontSize: 9, cellPadding: 5, textColor: [40, 40, 40] },
            headStyles: { fillColor: [15, 76, 129], textColor: 255, fontStyle: "bold" },
            alternateRowStyles: { fillColor: [245, 247, 250] },
        });

        cursorY = doc.lastAutoTable.finalY + 24;
    });

    // --- Pie de página con numeración ---
    const totalPaginas = doc.internal.getNumberOfPages();
    for (let i = 1; i <= totalPaginas; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(140, 140, 140);
        doc.text(
            `Página ${i} de ${totalPaginas} · Generado automáticamente`,
            marginX,
            doc.internal.pageSize.getHeight() - 20
        );
    }

    doc.save(`${payload.nombreArchivo || "reporte"}.pdf`);
}

// Expuesto globalmente para ser llamado desde clientside_callback de Dash
window.generarReportePDF = generarReportePDF;
