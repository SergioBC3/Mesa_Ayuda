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

const aJson = (d) => ({
  id: d._id,
  titulo: d.titulo || '',
  descripcion: d.descripcion || '',
  estado: d.estado || 'abierto',
  tecnico: d.tecnico || null,
});

const app = express();

app.get('/', (req, res) => res.redirect('/api-docs'));
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(spec));

app.get('/health', (req, res) => res.json({ estado: 'ok', servicio: 'lectura-respaldo-node' }));

app.get('/tickets', async (req, res) => {
  try {
    const docs = await tickets().find().sort({ _id: 1 }).toArray();
    res.json(docs.map(aJson));
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Error consultando la base de datos' });
  }
});

app.get('/tickets/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) return res.status(400).json({ error: 'id inválido' });
  try {
    const d = await tickets().findOne({ _id: id });
    if (!d) return res.status(404).json({ error: 'Ticket no encontrado' });
    res.json(aJson(d));
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Error consultando la base de datos' });
  }
});

cliente
  .connect()
  .then(() => app.listen(PORT, () => console.log(`Lectura (Node respaldo) en puerto ${PORT}`)))
  .catch((e) => {
    console.error('No se pudo conectar a MongoDB', e);
    process.exit(1);
  });
