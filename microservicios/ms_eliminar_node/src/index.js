const express = require('express');
const { MongoClient } = require('mongodb');
const swaggerUi = require('swagger-ui-express');
const spec = require('./openapi');

const MONGODB_URI = process.env.MONGODB_URI;
const MONGODB_DB = process.env.MONGODB_DB || 'mesa_ayuda';
const PORT = process.env.PORT || 3000;

if (!MONGODB_URI) {
  console.error('Falta la variable de entorno MONGODB_URI');
  process.exit(1);
}

const cliente = new MongoClient(MONGODB_URI);
const tickets = () => cliente.db(MONGODB_DB).collection('tickets');

const app = express();

app.get('/', (req, res) => res.redirect('/api-docs'));
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(spec));

app.get('/health', (req, res) => res.json({ estado: 'ok', servicio: 'eliminar-node' }));

app.delete('/tickets/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) return res.status(400).json({ error: 'id inválido' });
  try {
    const r = await tickets().deleteOne({ _id: id });
    if (r.deletedCount === 0) return res.status(404).json({ error: 'Ticket no encontrado' });
    res.json({ mensaje: 'Ticket eliminado', id });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Error eliminando en la base de datos' });
  }
});

cliente
  .connect()
  .then(() => app.listen(PORT, () => console.log(`Eliminar (Node) en puerto ${PORT}`)))
  .catch((e) => {
    console.error('No se pudo conectar a MongoDB', e);
    process.exit(1);
  });
