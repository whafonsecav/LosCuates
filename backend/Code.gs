/**
 * Backend de la encuesta Los Cuates · Google Apps Script + Google Sheets (gratis).
 *
 * Cómo se instala (detalle en ../GUIA-PUBLICAR.md):
 * 1. Crea una hoja de cálculo nueva en Google Sheets.
 * 2. Extensiones > Apps Script. Borra lo que haya y pega TODO este archivo.
 * 3. Implementar > Nueva implementación > Tipo: Aplicación web.
 *    Ejecutar como: Yo.  Quién tiene acceso: Cualquier persona.
 * 4. Copia la URL que termina en /exec y pégala en ENDPOINT, dentro de encuesta/index.html.
 *
 * Cada respuesta queda en una fila de la pestaña "Respuestas". Las preguntas de
 * selección múltiple se guardan separadas por " | " (por ejemplo "mango | fresa").
 */
const HOJA = 'Respuestas';
const COLUMNAS = ['recibido', 'id', 'fecha_cliente', 'duracion_seg', 'ruta', 'edad', 'probado',
  'sabores', 'favorito', 'gusta', 'mejorar', 'tequila', 'plan', 'precio', 'sustituto', 'entero', 'persona', 'recomienda',
  'frena', 'conoce', 'conoce_otro', 'toma_normal', 'favorita', 'paga', 'cambiaria', 'probaria', 'sabor_primero',
  'nuevo_sabor', 'genero', 'ciudad', 'estrato', 'dispositivo', 'fuente', 'version'];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(15000);                                   // evita que dos respuestas simultáneas se pisen
  try {
    const raw = (e && e.postData && e.postData.contents) || '';
    if (raw.length > 8000) return salida({ ok: false, error: 'demasiado grande' });
    const d = JSON.parse(raw);
    if (!d.id || !d.version || d.edad === 'menor') return salida({ ok: false, error: 'incompleta' });

    const hoja = obtenerHoja();
    // no duplicar si el navegador reintenta el mismo envío
    const ids = hoja.getLastRow() > 1 ? hoja.getRange(2, 2, hoja.getLastRow() - 1, 1).getValues().flat() : [];
    if (ids.indexOf(d.id) >= 0) return salida({ ok: true, duplicado: true });

    d.recibido = new Date();
    const fila = COLUMNAS.map(c => limpiar(d[c]));
    fila[0] = d.recibido;
    hoja.appendRow(fila);
    return salida({ ok: true });
  } catch (err) {
    return salida({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Abrir la URL /exec en el navegador sirve para comprobar que está viva.
function doGet() {
  return salida({ ok: true, respuestas: Math.max(obtenerHoja().getLastRow() - 1, 0) });
}

function obtenerHoja() {
  const libro = SpreadsheetApp.getActiveSpreadsheet();
  let hoja = libro.getSheetByName(HOJA);
  if (!hoja) {
    hoja = libro.insertSheet(HOJA);
    hoja.getRange(1, 1, 1, COLUMNAS.length).setValues([COLUMNAS]).setFontWeight('bold').setBackground('#f8a21c');
    hoja.setFrozenRows(1);
  }
  return hoja;
}

// Texto corto y sin fórmulas (evita que alguien inyecte "=IMPORTXML(...)" en el campo "otro").
function limpiar(v) {
  if (v === undefined || v === null) return '';
  let s = String(v).slice(0, 200);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function salida(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Ejecútala una vez desde el editor (botón ▶) para crear la pestaña y autorizar el script.
function prueba() {
  obtenerHoja();
  Logger.log('Listo: pestaña "' + HOJA + '" creada.');
}
