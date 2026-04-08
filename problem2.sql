-- companies table to store all companies using the system
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- warehouses belong to a company (one company can have many warehouses)
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    location TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- products table (each product belongs to a company)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL, -- keeping SKU unique across system
    price DECIMAL(10,2) NOT NULL,
    is_bundle BOOLEAN DEFAULT FALSE, -- to identify bundle products
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- inventory table to track product quantity in each warehouse
-- this handles many-to-many relation between product and warehouse
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (product_id, warehouse_id), -- avoid duplicate entries
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

-- inventory_logs table to track changes in stock over time
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    change_type VARCHAR(50), -- ADD / REMOVE / UPDATE
    quantity_changed INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

-- suppliers table to store supplier details
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info TEXT
);

-- mapping table for supplier and products (many-to-many relation)
CREATE TABLE supplier_products (
    id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL,
    product_id INT NOT NULL,
    cost_price DECIMAL(10,2),

    UNIQUE (supplier_id, product_id), -- same supplier should not repeat for same product
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- product bundles table (one product can contain other products)
-- used when product is a bundle of multiple items
CREATE TABLE product_bundles (
    id SERIAL PRIMARY KEY,
    bundle_id INT NOT NULL, -- parent product (bundle)
    component_product_id INT NOT NULL, -- child product
    quantity INT NOT NULL,

    FOREIGN KEY (bundle_id) REFERENCES products(id),
    FOREIGN KEY (component_product_id) REFERENCES products(id)
);