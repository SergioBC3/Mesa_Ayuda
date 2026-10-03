module.exports = {
  openapi: '3.0.3',
  info: {
    title: 'Microservicio de Eliminación (Node.js) - Mesa de Ayuda',
    version: '1.0.0',
    description: 'Elimina tickets de la base de datos MongoDB.',
  },
  paths: {
    '/health': {
      get: { tags: ['Estado'], summary: 'Estado del servicio', responses: { 200: { description: 'OK' } } },
    },
    '/tickets/{id}': {
      delete: {
        tags: ['Tickets'],
        summary: 'Eliminar un ticket por id',
        parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' }, example: 1 }],
        responses: {
          200: {
            description: 'Ticket eliminado',
            content: { 'application/json': { schema: { type: 'object', properties: { mensaje: { type: 'string' }, id: { type: 'integer' } } } } },
          },
          400: { description: 'id inválido' },
          404: { description: 'Ticket no encontrado' },
        },
      },
    },
  },
};
