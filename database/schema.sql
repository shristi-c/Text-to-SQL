-- ============================================================
-- TEXT-TO-SQL DATABASE SCHEMA
-- PostgreSQL
-- Domains: IT, Retail, Airline
-- ============================================================


-- ============================================================
-- IT DOMAIN
-- ============================================================

CREATE TABLE IF NOT EXISTS it.it_tickets (
    ticket_id BIGINT PRIMARY KEY,
    subject TEXT,
    body TEXT,
    answer TEXT,
    type TEXT,
    queue TEXT,
    priority TEXT,
    language TEXT,
    version INTEGER,
    business_type TEXT
);

CREATE TABLE IF NOT EXISTS it.it_tags (
    ticket_id BIGINT NOT NULL,
    tag TEXT NOT NULL,

    PRIMARY KEY (ticket_id, tag),

    CONSTRAINT fk_it_tags_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES it.it_tickets(ticket_id)
        ON DELETE CASCADE
);


-- ============================================================
-- RETAIL DOMAIN
-- ============================================================

CREATE TABLE IF NOT EXISTS retail.customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
    segment TEXT
);

CREATE TABLE IF NOT EXISTS retail.products (
    product_key BIGINT PRIMARY KEY,
    product_id TEXT NOT NULL,
    product_name TEXT,
    category TEXT,
    sub_category TEXT,

    CONSTRAINT uq_product_id_name
        UNIQUE (product_id, product_name)
);

CREATE TABLE IF NOT EXISTS retail.orders (
    order_id TEXT PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    ship_mode TEXT,
    customer_id TEXT,
    country TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    region TEXT,
    retail_sales_person TEXT,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES retail.customers(customer_id)
);

CREATE TABLE IF NOT EXISTS retail.order_items (
    row_id BIGINT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_key BIGINT NOT NULL,
    returned TEXT,
    sales NUMERIC(14,4),
    quantity INTEGER,
    discount NUMERIC(8,4),
    profit NUMERIC(14,4),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES retail.orders(order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_key)
        REFERENCES retail.products(product_key)
);


-- ============================================================
-- AIRLINE DOMAIN
-- ============================================================

CREATE TABLE IF NOT EXISTS airline.aircrafts (
    aircraft_code TEXT PRIMARY KEY,
    model TEXT,
    range INTEGER
);

CREATE TABLE IF NOT EXISTS airline.airports (
    airport_code TEXT PRIMARY KEY,
    airport_name TEXT,
    city TEXT,
    coordinates TEXT,
    timezone TEXT
);

CREATE TABLE IF NOT EXISTS airline.seats (
    aircraft_code TEXT NOT NULL,
    seat_no TEXT NOT NULL,
    fare_conditions TEXT,

    PRIMARY KEY (aircraft_code, seat_no),

    CONSTRAINT fk_seats_aircraft
        FOREIGN KEY (aircraft_code)
        REFERENCES airline.aircrafts(aircraft_code)
);

CREATE TABLE IF NOT EXISTS airline.bookings (
    book_ref TEXT PRIMARY KEY,
    book_date TIMESTAMPTZ,
    total_amount NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS airline.tickets (
    ticket_no TEXT PRIMARY KEY,
    book_ref TEXT NOT NULL,
    passenger_id TEXT,

    CONSTRAINT fk_tickets_booking
        FOREIGN KEY (book_ref)
        REFERENCES airline.bookings(book_ref)
);

CREATE TABLE IF NOT EXISTS airline.flights (
    flight_id INTEGER PRIMARY KEY,
    flight_no TEXT,
    scheduled_departure TIMESTAMPTZ,
    scheduled_arrival TIMESTAMPTZ,
    departure_airport TEXT,
    arrival_airport TEXT,
    status TEXT,
    aircraft_code TEXT,
    actual_departure TIMESTAMPTZ,
    actual_arrival TIMESTAMPTZ,

    CONSTRAINT fk_flights_departure_airport
        FOREIGN KEY (departure_airport)
        REFERENCES airline.airports(airport_code),

    CONSTRAINT fk_flights_arrival_airport
        FOREIGN KEY (arrival_airport)
        REFERENCES airline.airports(airport_code),

    CONSTRAINT fk_flights_aircraft
        FOREIGN KEY (aircraft_code)
        REFERENCES airline.aircrafts(aircraft_code)
);

CREATE TABLE IF NOT EXISTS airline.ticket_flights (
    ticket_no TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    fare_conditions TEXT,
    amount NUMERIC(14,2),

    PRIMARY KEY (ticket_no, flight_id),

    CONSTRAINT fk_ticket_flights_ticket
        FOREIGN KEY (ticket_no)
        REFERENCES airline.tickets(ticket_no),

    CONSTRAINT fk_ticket_flights_flight
        FOREIGN KEY (flight_id)
        REFERENCES airline.flights(flight_id)
);

CREATE TABLE IF NOT EXISTS airline.boarding_passes (
    ticket_no TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    boarding_no INTEGER,
    seat_no TEXT,

    PRIMARY KEY (ticket_no, flight_id),

    CONSTRAINT fk_boarding_pass_ticket_flight
        FOREIGN KEY (ticket_no, flight_id)
        REFERENCES airline.ticket_flights(ticket_no, flight_id)
);


-- ============================================================
-- INDEXES
-- ============================================================

-- IT
CREATE INDEX IF NOT EXISTS idx_it_tickets_priority
    ON it.it_tickets(priority);

CREATE INDEX IF NOT EXISTS idx_it_tickets_queue
    ON it.it_tickets(queue);

CREATE INDEX IF NOT EXISTS idx_it_tags_tag
    ON it.it_tags(tag);


-- Retail
CREATE INDEX IF NOT EXISTS idx_orders_customer
    ON retail.orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON retail.order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product
    ON retail.order_items(product_key);

CREATE INDEX IF NOT EXISTS idx_products_product_id
    ON retail.products(product_id);


-- Airline
CREATE INDEX IF NOT EXISTS idx_tickets_book_ref
    ON airline.tickets(book_ref);

CREATE INDEX IF NOT EXISTS idx_flights_departure_airport
    ON airline.flights(departure_airport);

CREATE INDEX IF NOT EXISTS idx_flights_arrival_airport
    ON airline.flights(arrival_airport);

CREATE INDEX IF NOT EXISTS idx_flights_aircraft
    ON airline.flights(aircraft_code);

CREATE INDEX IF NOT EXISTS idx_ticket_flights_flight
    ON airline.ticket_flights(flight_id);

CREATE INDEX IF NOT EXISTS idx_boarding_passes_seat
    ON airline.boarding_passes(seat_no);