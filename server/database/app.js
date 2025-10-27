const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

// Load JSON seed data
const reviews_data = JSON.parse(fs.readFileSync("reviews.json", 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync("dealerships.json", 'utf8'));

// MongoDB connection
mongoose.connect("mongodb://mongo_db:27017/", { dbName: 'dealershipsDB' });

// Import models
const Reviews = require('./review');
const Dealerships = require('./dealership');

// Seed database on startup
(async () => {
  try {
    await Reviews.deleteMany({});
    await Reviews.insertMany(reviews_data['reviews']);

    await Dealerships.deleteMany({});
    await Dealerships.insertMany(dealerships_data['dealerships']);

    console.log("✅ Seeded Reviews and Dealerships");
  } catch (error) {
    console.error("❌ Error seeding data:", error);
  }
})();

// Home route
app.get('/', async (req, res) => {
  res.send("Welcome to the Mongoose API");
});

// Fetch ALL reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Fetch reviews for a specific dealer id
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Fetch ALL dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const dealers = await Dealerships.find({});
    res.json(dealers);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

// Fetch dealerships in a given state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const stateName = req.params.state;
    const dealersInState = await Dealerships.find({ state: stateName });
    res.json(dealersInState);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

// Fetch ONE dealer by id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const dealerId = req.params.id;
    const dealer = await Dealerships.findOne({ id: parseInt(dealerId) });

    if (!dealer) {
      return res.status(404).json({ error: 'Dealer not found' });
    }

    res.json(dealer);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealer by id' });
  }
});

// Insert new review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  const data = JSON.parse(req.body);
  const documents = await Reviews.find().sort({ id: -1 });
  let new_id = documents[0]['id'] + 1;

  const review = new Reviews({
    "id": new_id,
    "name": data['name'],
    "dealership": data['dealership'],
    "review": data['review'],
    "purchase": data['purchase'],
    "purchase_date": data['purchase_date'],
    "car_make": data['car_make'],
    "car_model": data['car_model'],
    "car_year": data['car_year'],
  });

  try {
    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
