CREATE TABLE Customers(
    id SERIAL PRIMARY KEY, 
    name VARCHAR(255) NOT NULL,
    afm VARCHAR(20),
    phone1 VARCHAR(15),
    phone2 VARCHAR(15),
    email VARCHAR(255),
    address VARCHAR(255)
);
CREATE TABLE orders(
    id SERIAL PRIMARY KEY,
    notes VARCHAR(1000),
    dt DATE DEFAULT CURRENT_DATE,
    paid REAL,
    visa_cash INT,
    cust_id INT NOT NULL,
    after_sale REAL,
    CONSTRAINT customer FOREIGN KEY (cust_id) REFERENCES customers(id) ON DELETE CASCADE
);
CREATE TABLE OrderRows(
    id SERIAL PRIMARY KEY,
    quantity REAL,
    descr VARCHAR(1000),
    is_ordered INT,
    value REAL,
    order_id INT NOT NULL,
    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
CREATE TABLE Users(
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);