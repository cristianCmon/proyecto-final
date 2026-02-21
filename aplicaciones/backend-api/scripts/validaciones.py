import zon

# Esquema para registro de usuario
validacionRegistro = zon.record({
    "nombre_usuario": zon.string().min(4).max(10),
    "contraseña": zon.string().min(8),
    "nombre": zon.string().max(12),
    "apellidos": zon.string().max(22),
    "email": zon.string().email(),
    "dni": zon.string().regex(r'^[0-9]{8}[A-Z]$'),
    "telefono": zon.string().regex(r'^[0-9]{9}$').optional()
})

# Esquema para login de usuario
validacionLogin = zon.record({
    "nombre_usuario": zon.string().min(4).max(10),
    "contraseña": zon.string().min(8)
})

