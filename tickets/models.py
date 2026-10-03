# Los tickets ya no se guardan en SQLite: viven en MongoDB y se manejan a
# traves de los microservicios (ver tickets/servicios.py).

ESTADOS = [
    ('abierto', 'Abierto'),
    ('cerrado', 'Cerrado'),
]
