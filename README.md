# Maison Élite · Ontology Explorer

---

## What is the Semantic Web?

The regular web is built for humans — we read pages, look at images, and understand what things mean. The **Semantic Web** is an extension of that idea, but built for machines. Instead of just storing text, it stores **meaning**.

Think of it like this: a normal database knows that a restaurant has a "rating" of 4.8. The Semantic Web knows that 4.8 is a *rating*, that ratings belong to *restaurants*, that restaurants *employ* chefs, and that chefs *prepare* dishes. It understands the **relationships between things**, not just the values.

The building block of the Semantic Web is the **ontology** — a structured vocabulary that defines what things exist in a domain and how they relate to each other.

---

## What is an Ontology?

An ontology is like a map of knowledge. It answers three questions:

- **What kinds of things exist?** *(Classes — e.g. Chef, Dish, Restaurant)*
- **What do we know about them?** *(Properties — e.g. a dish has a price and a rating)*
- **How are they connected?** *(Relations — e.g. a chef prepares a dish, a restaurant employs a chef)*

Ontologies are written in a language called **OWL** (Web Ontology Language), which is a W3C standard for the Semantic Web.

---

## About This Project

This project models a **fine-dining restaurant** called *Maison Élite* as a Semantic Web ontology.

The ontology covers the entire restaurant domain:

| Class | What it represents |
|---|---|
| Restaurant | The venue, its location, cuisine, and rating |
| Chef | Head chefs, sous chefs, and pastry chefs with their specialties |
| Dish | Starters, mains, and desserts with prices, ratings, and allergens |
| Menu | Degustation, à la carte, and seasonal menus |
| Ingredient | Raw ingredients with their origin and seasonal availability |
| Customer | VIP and regular customers with visit history |
| Reservation | Bookings with date, party size, and confirmation status |
| Award | Industry awards earned by the restaurant and its chefs |

The ontology is stored as an `.owl` file and loaded into a Python desktop application that lets you browse and query every entity and relationship visually.

---

## Screenshot

<!-- Add your screenshot here -->

---

## How to Run

1. Make sure Python 3.8+ is installed
2. Place `maison_elite.owl` and `ontology_explorer.py` in the same folder
3. Run:

```bash
python ontology_explorer.py
```

No additional libraries needed — everything uses Python's built-in modules.

---

## Built With

- **OWL / RDF** — ontology language and data model
- **Python** — application logic and OWL parsing
- **Tkinter** — graphical user interface
