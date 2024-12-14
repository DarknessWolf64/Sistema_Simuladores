document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const togglePassword = document.getElementById('toggle-password');
    const passwordForm = document.getElementById('password-form');
    const responseMessage = document.getElementById('response-message');
    let isPasswordVisible = false; // Estado del ícono de visibilidad
    const rules = {
        length: document.getElementById('length-rule'),
        uppercase: document.getElementById('uppercase-rule'),
        lowercase: document.getElementById('lowercase-rule'),
        special: document.getElementById('special-rule')
    };

    // Mostrar temporalmente el último carácter ingresado
    passwordInput.addEventListener('input', (event) => {
        const value = passwordInput.value;
        validatePassword(value);
    });

    // Alternar visibilidad completa de la contraseña
    togglePassword.addEventListener('click', () => {
        isPasswordVisible = !isPasswordVisible;
        passwordInput.type = isPasswordVisible ? 'text' : 'password';
        confirmPasswordInput.type = isPasswordVisible ? 'text' : 'password';  // Mostrar también la confirmación de contraseña
    });

    // Validar las reglas de la contraseña
    function validatePassword(value) {
        rules.length.style.color = value.length >= 8 ? 'green' : 'red';
        rules.uppercase.style.color = /[A-Z]/.test(value) ? 'green' : 'red';
        rules.lowercase.style.color = /[a-z]/.test(value) ? 'green' : 'red';
        rules.special.style.color = /[!@#$%^&*(),.?":{}|<>]/.test(value) ? 'green' : 'red';
    }

    // Manejar el envío del formulario
    passwordForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Evita que el formulario se envíe de forma tradicional

        // Verificar que las contraseñas coincidan
        if (passwordInput.value !== confirmPasswordInput.value) {
            responseMessage.style.display = 'block';
            responseMessage.style.backgroundColor = 'red';
            responseMessage.style.color = 'white';
            responseMessage.textContent = 'Las contraseñas no coinciden';
            return;
        }

        // Verificar que la contraseña cumpla con los requisitos
        if (passwordInput.value.length < 8) {
            responseMessage.style.display = 'block';
            responseMessage.style.backgroundColor = 'red';
            responseMessage.style.color = 'white';
            responseMessage.textContent = 'La contraseña debe tener al menos 8 caracteres';
            return;
        }

        // Obtener los datos del formulario
        const formData = new FormData(passwordForm);

        try {
            // Enviar los datos al servidor usando fetch
            const response = await fetch(passwordForm.action, {
                method: 'POST',
                body: formData
            });

            // Si la respuesta no es exitosa, manejar error
            if (!response.ok) {
                const errorMessage = await response.text();
                responseMessage.style.display = 'block';
                responseMessage.style.backgroundColor = 'red';
                responseMessage.style.color = 'white';
                responseMessage.textContent = errorMessage || 'Error al procesar la solicitud.';
            } else {
                // Si la respuesta es exitosa, mostrar mensaje y redirigir
                const result = await response.text();  // Obtener respuesta en formato texto
                responseMessage.style.display = 'block';
                responseMessage.style.backgroundColor = 'green';
                responseMessage.style.color = 'white';
                responseMessage.textContent = result || 'Contraseña actualizada con éxito';

                setTimeout(() => {
                    window.location.href = '/';  // Redirigir después de 2 segundos
                }, 2000);
            }

        } catch (error) {
            responseMessage.style.display = 'block';
            responseMessage.style.backgroundColor = 'red';
            responseMessage.style.color = 'white';
            responseMessage.textContent = 'Error al procesar la solicitud.';
        }
    });
});
