# Airport API

A REST API for an airport booking system.
It allows users to browse flights and create orders with multiple tickets.
Authentication is implemented with JWT, so each user can access only their own orders and tickets.

## Features
- User registration and JWT authentication (access/refresh)
- Flights listing
- Create an order with multiple tickets in one request
- Validation:
  - order cannot be created without tickets
  - seat/row must be within airplane capacity
  - prevents double-booking: unique constraint on (`flight`, `row`, `seat`)

## Permissions
- **Unauthenticated users:** read-only access to public resources (e.g. flights/routes/airplanes).
- **Authenticated users:** read-only access to public resources + can create and view **only their own** orders/tickets.
- **Admin/Staff:** full CRUD for public resources; **orders/tickets remain owner-scoped** (cannot view other users’ orders/tickets).

## Usage

### Auth
1. **Register**
   - `POST /api/user/register/`
2. **Get token**
   - `POST /api/user/token/`
3. Use access token in requests:
   - `Authorization: Bearer <access>`

### Main endpoints
- **Flights**
  - `GET /api/airport/flights/`
- **Orders**
  - `GET /api/airport/orders/` (only current user)
  - `POST /api/airport/orders/` (create order with tickets)
- **Tickets**
  - `GET /api/airport/tickets/` (only current user)
  - `GET /api/airport/tickets/{id}/`

### Run locally

```bash
git clone https://github.com/anastasiiaoshega513/airport-api.git
cd airport-api

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Get token
`POST /api/user/token/`
```json
{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

## Run with Docker

This project can be run locally using Docker (Django + PostgreSQL).

```bash
docker compose up --build
```

## Postman

This repository includes ready-to-use Postman files:

- [Postman Collection](postman/Airport_API.postman_collection.json)
- [Postman Environment (Local)](postman/local.environment.json)
