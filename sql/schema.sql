CREATE TABLE IF NOT EXISTS sales (
    sale_date DATE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    state VARCHAR(2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    product VARCHAR(150) NOT NULL,
    seller VARCHAR(100) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(14, 2) NOT NULL CHECK (unit_price >= 0),
    unit_cost NUMERIC(14, 2) NOT NULL CHECK (unit_cost >= 0)
);

CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales (sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_seller ON sales (seller);
CREATE INDEX IF NOT EXISTS idx_sales_category ON sales (category);
