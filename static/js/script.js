// Función para mostrar u ocultar el campo del lugar según la selección del radio button
function toggleLugarField() {
    var dentroNo = document.getElementById('dentroNo');
    var lugarGroup = document.getElementById('lugarGroup');
    
    // Si el radio button "Fuera de las instalaciones" está seleccionado, mostrar el campo del lugar
    if (dentroNo.checked) {
        lugarGroup.style.display = 'block';
    } else {
        lugarGroup.style.display = 'none';
    }
}

function toggleLugarField() {
    var lugarGroup = document.getElementById('lugarGroup');
    var dentroNo = document.getElementById('dentroNo');
    
    // Mostrar el campo de lugar si se selecciona "Fuera de las instalaciones
    if (dentroNo.checked) {
        lugarGroup.style.display = 'block'; // Mostrar el campo de lugar
    } else {
        lugarGroup.style.display = 'none'; // Ocultar el campo de lugar si no se selecciona "Fuera de las instalaciones"
    }
}

// Validación del formulario antes de enviar
document.getElementById('solicitudForm').addEventListener('submit', function(event) {
    var nombre = document.getElementById('nombre').value.trim();
    var NumeroCelular = document.getElementById('NumeroCelular').value.trim();
    var correo = document.getElementById('correo').value.trim();
    var dentroSi = document.getElementById('dentroSi').checked;
    var lugar = document.getElementById('lugar').value.trim();
    var lugarGroup = document.getElementById('lugarGroup');
    var errorMessage = "";

    // Validación de campos obligatorios
    if (nombre === "") {
        errorMessage += "Por favor, ingresa el nombre de la práctica.\n";
    }
    if (NumeroCelular === "") {
        errorMessage += "Por favor, ingresa el número de celular.\n";
    }
    if (correo === "") {
        errorMessage += "Por favor, ingresa el correo electrónico del corresponsable.\n";
    }
    if (!dentroSi && lugar === "" && lugarGroup.style.display === 'block') {
        errorMessage += "Por favor, ingresa el lugar si la práctica es fuera de las instalaciones.\n";
    }

    // Mostrar mensaje de error si es necesario
    if (errorMessage !== "") {
        alert(errorMessage);
        event.preventDefault(); // Evitar el envío del formulario si hay errores
    }
});

function confirmarCancelacion() {
    // Muestra un cuadro de diálogo de confirmación
    var confirmacion = confirm("¿Seguro que deseas cancelar la orden?");

    if (confirmacion) {
        window.location.href = "prestatario"; 
    }
}