const express = require('express');
const app = express();

// Import routes for each microservice
const roomsService = require('./services/rooms_service');
const searchService = require('./services/search_service');
const bookingService = require('./services/booking_service');

// Use routes for each microservice
app.use('/rooms', roomsService);
app.use('/search', searchService);
app.use('/book', bookingService);

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`API Gateway listening at http://localhost:${port}`);
});
