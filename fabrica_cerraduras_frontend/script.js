// La dirección (URL) de tu backend Flask. ¡Asegúrate de que coincida con donde se está ejecutando Flask!
// Por defecto, Flask corre en el puerto 5000 en tu propia computadora (localhost).
const API_URL = 'http://127.0.0.1:5000/api';

// --- Funciones para manejar la Interfaz (lo que el usuario ve) ---

// Esta función es para cambiar qué sección de la página se muestra (Insumos, Artículos, Reportes).
function showSection(sectionId) {
    // Primero, ocultamos todas las secciones posibles
    document.querySelectorAll('main section').forEach(section => {
        section.classList.add('hidden'); // Le añade la clase 'hidden' (definida en style.css para ocultar)
        section.classList.remove('active'); // Quita la clase 'active'
    });
    // Luego, mostramos solo la sección que nos interesa
    document.getElementById(sectionId).classList.remove('hidden'); // Le quita 'hidden'
    document.getElementById(sectionId).classList.add('active'); // Le añade 'active' (para mostrar)

    // Cuando cambiamos de sección, cargamos los datos correspondientes automáticamente
    if (sectionId === 'insumos-section') {
        loadInsumos(); // Llama a la función para cargar insumos
    } else if (sectionId === 'articulos-section') {
        loadArticulos(); // Llama a la función para cargar artículos
    }
    // El reporte de insumos bajo stock no se carga automáticamente, tiene un botón propio.
}

// Funciones para abrir y cerrar las ventanas emergentes (los "modals")
function openModal(modalId, itemData = null) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'block'; // Cambia el estilo para que se muestre

    // Si es el modal de editar insumo, necesitamos cargar los datos del insumo específico
    if (modalId === 'editInsumoModal' && itemData !== null) {
        loadInsumoForEdit(itemData); // itemData aquí es el ID del insumo
    }
    // Si es el modal de producir artículo, cargamos el nombre y ID del artículo
    if (modalId === 'producirArticuloModal' && itemData !== null) {
        loadArticuloForProduce(itemData); // itemData aquí es un objeto { id, nombre } del artículo
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none'; // Cambia el estilo para que se oculte
}

// También cerramos el modal si el usuario hace clic fuera de la ventana del modal
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) { // Si el clic fue en el fondo semi-transparente del modal
        event.target.style.display = 'none'; // Lo oculta
    }
};

// --- Funciones para la Gestión de INSUMOS (aquí el frontend "habla" con tu backend) ---

// Esta función pide la lista de todos los insumos a tu backend y los muestra en la tabla
async function loadInsumos() {
    const insumosTableBody = document.getElementById('insumos-table-body');
    insumosTableBody.innerHTML = '<tr><td colspan="4">Cargando insumos...</td></tr>'; // Mensaje mientras carga

    try {
        // Hacemos una petición GET a tu endpoint de Flask: http://127.0.0.1:5000/api/insumos
        const response = await fetch(`${API_URL}/insumos`);
        // Si la respuesta del servidor no fue "OK" (ej. 404, 500), lanzamos un error
        if (!response.ok) {
            // Intentamos leer el error que nos dio Flask si lo envió en JSON
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP! Estado: ${response.status}`);
        }
        const insumos = await response.json(); // Convertimos la respuesta (JSON) en un objeto JavaScript

        insumosTableBody.innerHTML = ''; // Limpiamos la tabla para no duplicar datos
        if (insumos.length === 0) {
            insumosTableBody.innerHTML = '<tr><td colspan="4">No hay insumos disponibles.</td></tr>';
        } else {
            // Recorremos cada insumo que recibimos del backend
            insumos.forEach(insumo => {
                const row = insumosTableBody.insertRow(); // Creamos una nueva fila en la tabla HTML
                row.insertCell().textContent = insumo.idInsumo; // Añadimos la celda del ID
                row.insertCell().textContent = insumo.nombreInsumo; // Añadimos la celda del nombre
                row.insertCell().textContent = insumo.cantidadInsumo; // Añadimos la celda de la cantidad
                const actionsCell = row.insertCell(); // Celda para los botones de acción

                // Creamos el botón "Editar"
                const editButton = document.createElement('button');
                editButton.textContent = 'Editar';
                editButton.className = 'edit'; // Le damos una clase CSS para que se vea bonito
                editButton.onclick = () => openModal('editInsumoModal', insumo.idInsumo); // Cuando se haga clic, abre el modal de edición
                actionsCell.appendChild(editButton); // Agregamos el botón a la celda

                // Creamos el botón "Eliminar"
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Eliminar';
                deleteButton.className = 'delete'; // Clase CSS para estilo
                deleteButton.onclick = () => deleteInsumo(insumo.idInsumo); // Cuando se haga clic, llama a la función para eliminar
                actionsCell.appendChild(deleteButton);
            });
        }
    } catch (error) {
        console.error('Error al cargar insumos:', error); // Muestra el error en la consola del navegador (F12)
        insumosTableBody.innerHTML = `<tr><td colspan="4" style="color: red;">Error al cargar insumos: ${error.message}</td></tr>`;
    }
}

// Esta función se activa cuando se envía el formulario para agregar un insumo
document.getElementById('add-insumo-form').addEventListener('submit', async (event) => {
    event.preventDefault(); // IMPORTANTE: Evita que la página se recargue al enviar el formulario

    const nombre = document.getElementById('add-nombre').value; // Obtiene el valor del campo "Nombre"
    const cantidad = parseInt(document.getElementById('add-cantidad').value); // Obtiene el valor del campo "Cantidad" y lo convierte a número

    // Validaciones básicas del lado del frontend
    if (!nombre || isNaN(cantidad)) {
        alert('Por favor, ingresa un nombre y una cantidad válida.');
        return; // Detiene la función si la validación falla
    }

    try {
        // Hacemos una petición POST a tu endpoint: http://127.0.0.1:5000/api/insumos
        const response = await fetch(`${API_URL}/insumos`, {
            method: 'POST', // Es una petición POST
            headers: {
                'Content-Type': 'application/json' // Le decimos al backend que le enviamos JSON
            },
            body: JSON.stringify({ // Convertimos el objeto JavaScript a una cadena JSON
                nombreInsumo: nombre,
                cantidadInsumo: cantidad
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP! Estado: ${response.status}`);
        }

        const result = await response.json(); // Recibimos la respuesta de éxito del backend
        alert(result.message); // Mostramos el mensaje (ej. "Insumo añadido exitosamente")
        closeModal('addInsumoModal'); // Cerramos la ventana de agregar
        loadInsumos(); // Recargamos la lista para ver el nuevo insumo
        document.getElementById('add-insumo-form').reset(); // Limpiamos el formulario
    } catch (error) {
        console.error('Error al agregar insumo:', error);
        alert(`Error al agregar insumo: ${error.message}`); // Mostramos un error al usuario
    }
});

// Carga los datos de un insumo específico en el formulario de edición cuando se abre el modal
async function loadInsumoForEdit(id) {
    try {
        const response = await fetch(`${API_URL}/insumos/${id}`); // Petición GET al backend para obtener un insumo por su ID
        if (!response.ok) {
            throw new Error(`Error HTTP! Estado: ${response.status}`);
        }
        const insumo = await response.json(); // Obtenemos los datos del insumo
        // Llenamos los campos del formulario de edición con los datos del insumo
        document.getElementById('edit-id').value = insumo.idInsumo; // Campo oculto para el ID
        document.getElementById('edit-nombre').value = insumo.nombreInsumo;
        document.getElementById('edit-cantidad').value = insumo.cantidadInsumo;
    } catch (error) {
        console.error('Error al cargar insumo para edición:', error);
        alert(`Error al cargar insumo para edición: ${error.message}`);
    }
}

// Esta función se activa cuando se envía el formulario para actualizar un insumo
document.getElementById('edit-insumo-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const id = document.getElementById('edit-id').value; // Obtenemos el ID del insumo a actualizar
    const nombre = document.getElementById('edit-nombre').value;
    const cantidad = document.getElementById('edit-cantidad').value;

    // Creamos un objeto para enviar solo los datos que el usuario cambió
    const updateData = {};
    if (nombre) { // Si el campo nombre no está vacío
        updateData.nombreInsumo = nombre;
    }
    if (cantidad !== '' && cantidad !== null) { // Si el campo cantidad tiene algo (incluido 0)
        updateData.cantidadInsumo = parseInt(cantidad);
    }

    if (Object.keys(updateData).length === 0) { // Si el objeto está vacío, no hay nada que actualizar
        alert('No hay datos para actualizar. Ingresa al menos un campo.');
        return;
    }

    try {
        // Petición PUT para actualizar: http://127.0.0.1:5000/api/insumos/ID_DEL_INSUMO
        const response = await fetch(`${API_URL}/insumos/${id}`, {
            method: 'PUT', // Es una petición PUT
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData) // Enviamos solo los datos cambiados
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP! Estado: ${response.status}`);
        }

        const result = await response.json();
        alert(result.message);
        closeModal('editInsumoModal');
        loadInsumos(); // Recargamos la lista para ver los cambios
    } catch (error) {
        console.error('Error al actualizar insumo:', error);
        alert(`Error al actualizar insumo: ${error.message}`);
    }
});

// Función para eliminar un insumo
async function deleteInsumo(id) {
    // Pedimos confirmación antes de eliminar para evitar accidentes
    if (!confirm('¿Estás seguro de que quieres eliminar este insumo? Esta acción es irreversible.')) {
        return; // Si el usuario dice que no, la función se detiene
    }

    try {
        // Petición DELETE: http://127.0.0.1:5000/api/insumos/ID_DEL_INSUMO
        const response = await fetch(`${API_URL}/insumos/${id}`, {
            method: 'DELETE' // Es una petición DELETE
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP! Estado: ${response.status}`);
        }

        const result = await response.json();
        alert(result.message);
        loadInsumos(); // Recargamos la lista para que el insumo eliminado desaparezca
    } catch (error) {
        console.error('Error al eliminar insumo:', error);
        alert(`Error al eliminar insumo: ${error.message}`);
    }
}

// --- Funciones para la Gestión de ARTICULOS ---

// Carga y muestra la lista de artículos
async function loadArticulos() {
    const articulosTableBody = document.getElementById('articulos-table-body');
    articulosTableBody.innerHTML = '<tr><td colspan="5">Cargando artículos...</td></tr>';

    try {
        // Petición GET para obtener artículos: http://127.0.0.1:5000/api/articulos
        const response = await fetch(`${API_URL}/articulos`);
        if (!response.ok) {
            throw new Error(`Error HTTP! Estado: ${response.status}`);
        }
        const articulos = await response.json();

        articulosTableBody.innerHTML = '';
        if (articulos.length === 0) {
            articulosTableBody.innerHTML = '<tr><td colspan="5">No hay artículos disponibles.</td></tr>';
        } else {
            articulos.forEach(articulo => {
                const row = articulosTableBody.insertRow();
                row.insertCell().textContent = articulo.idArticulo;
                row.insertCell().textContent = articulo.nombreArticulo;
                row.insertCell().textContent = articulo.tipoArticulo;
                row.insertCell().textContent = articulo.cantidadDisponible; // Muestra el stock
                const actionsCell = row.insertCell();

                // Botón "Producir"
                const produceButton = document.createElement('button');
                produceButton.textContent = 'Producir';
                produceButton.className = 'produce';
                // Al hacer clic, abrimos el modal y le pasamos el ID y nombre del artículo
                produceButton.onclick = () => openModal('producirArticuloModal', { id: articulo.idArticulo, nombre: articulo.nombreArticulo });
                actionsCell.appendChild(produceButton);
            });
        }
    } catch (error) {
        console.error('Error al cargar artículos:', error);
        articulosTableBody.innerHTML = `<tr><td colspan="5" style="color: red;">Error al cargar artículos: ${error.message}</td></tr>`;
    }
}

// Prepara el modal de producción con los datos del artículo seleccionado
function loadArticuloForProduce(articuloInfo) {
    document.getElementById('producir-articulo-id').textContent = articuloInfo.id;
    document.getElementById('producir-articulo-nombre').textContent = articuloInfo.nombre;
    // Guardamos el ID en el formulario (como un atributo 'data-id-articulo') para usarlo al enviar
    document.getElementById('producir-articulo-form').setAttribute('data-id-articulo', articuloInfo.id);
    document.getElementById('produccion-cantidad').value = ''; // Limpiamos el campo de cantidad
}

// Esta función se activa cuando se envía el formulario para producir un artículo
document.getElementById('producir-articulo-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    // Obtenemos el ID del artículo que guardamos en el formulario y la cantidad a producir
    const idArticulo = document.getElementById('producir-articulo-form').getAttribute('data-id-articulo');
    const cantidadProducir = parseInt(document.getElementById('produccion-cantidad').value);

    // Validaciones
    if (isNaN(cantidadProducir) || cantidadProducir <= 0) {
        alert('Por favor, ingresa una cantidad válida y positiva a producir.');
        return;
    }

    try {
        // Petición POST para producir: http://127.0.0.1:5000/api/articulos/producir
        const response = await fetch(`${API_URL}/articulos/producir`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                idArticulo: parseInt(idArticulo), // Aseguramos que sea un número
                cantidadProducir: cantidadProducir
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            // Esto capturará los errores de tu Stored Procedure de MySQL
            throw new Error(errorData.error || `Error HTTP! Estado: ${response.status}`);
        }

        const result = await response.json();
        // Muestra un mensaje de éxito, y si el backend devolvió el nuevo stock, también lo muestra
        alert(result.message + (result.nuevo_stock_articulo !== undefined ? ` Nuevo stock: ${result.nuevo_stock_articulo}` : ''));
        closeModal('producirArticuloModal'); // Cierra el modal
        loadArticulos(); // Recarga la lista de artículos para ver el stock actualizado
        loadInsumos(); // Recarga los insumos también, porque la producción los descuenta
    } catch (error) {
        console.error('Error al producir artículo:', error);
        alert(`Error al producir artículo: ${error.message}`);
    }
});

// --- Funciones para REPORTES ---

// Carga y muestra el reporte de insumos bajo stock
async function loadInsumosBajoStock() {
    const reporteTableBody = document.getElementById('reporte-insumos-body');
    reporteTableBody.innerHTML = '<tr><td colspan="4">Cargando reporte...</td></tr>';

    try {
        // Petición GET para el reporte: http://127.0.0.1:5000/api/reportes/insumos_bajo_stock
        const response = await fetch(`${API_URL}/reportes/insumos_bajo_stock`);
        if (!response.ok) {
            throw new Error(`Error HTTP! Estado: ${response.status}`);
        }
        const insumos = await response.json();

        reporteTableBody.innerHTML = '';
        if (insumos.length === 0) {
            reporteTableBody.innerHTML = '<tr><td colspan="4">No hay insumos bajo stock mínimo.</td></tr>';
        } else {
            insumos.forEach(insumo => {
                const row = reporteTableBody.insertRow();
                row.insertCell().textContent = insumo.idInsumo;
                row.insertCell().textContent = insumo.nombreInsumo;
                row.insertCell().textContent = insumo.cantidadInsumo;
                row.insertCell().textContent = insumo.umbralMinimo;
            });
        }
    } catch (error) {
        console.error('Error al cargar reporte de insumos bajo stock:', error);
        reporteTableBody.innerHTML = `<tr><td colspan="4" style="color: red;">Error al cargar reporte: ${error.message}</td></tr>`;
    }
}

// --- Inicialización (esto se ejecuta cuando la página se carga por primera vez) ---

// Cuando todo el contenido HTML de la página esté cargado...
document.addEventListener('DOMContentLoaded', () => {
    showSection('insumos-section'); // ...mostramos la sección de insumos por defecto
});