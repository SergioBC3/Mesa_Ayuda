const ticket = {
  type: 'object',
  properties: {
    id: { type: 'integer', example: 1 },
    titulo: { type: 'string', example: 'Impresora sin conexión' },
    descripcion: { type: 'string', example: 'La impresora del piso 2 no imprime' },
    estado: { type: 'string', enum: ['abierto', 'cerrado'], example: 'abierto' },
    tecnico: { type: 'string', nullable: true, example: 'Carlos Pérez' },
  },
};

module.exports = {
  openapi: '3.0.3',
  info: {
    title: 'Microservicio de Lectura de RESPALDO (Node.js) - Mesa de Ayuda',
    version: '1.0.0',
    description:
      'Servicio de lectura escrito en Node.js. Django lo llama automáticamente cuando el ' +
      'servicio principal de lectura (Python) falla.',
  },
  paths: {
    '/health': {
      get: { tags: ['Estado'], summary: 'Estado del servicio', responses: { 200: { description: 'OK' } } },
    },
    '/tickets': {
      get: {
        tags: ['Tickets'],
        summary: 'Listar todos los tickets',
        responses: {
          200: { description: 'Lista de tickets', content: { 'application/json': { schema: { type: 'array', items: ticket } } } },
        },
      },
    },
    '/tickets/{id}': {
      get: {
        tags: ['Tickets'],
        summary: 'Consultar un ticket por id',
        parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }],
        responses: {
          200: { description: 'Ticket', content: { 'application/json': { schema: ticket } } },
          404: { description: 'Ticket no encontrado' },
        },
      },
    },
  },
};
