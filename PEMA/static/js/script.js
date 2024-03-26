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