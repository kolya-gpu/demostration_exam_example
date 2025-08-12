CREATE TABLE IF NOT EXISTS material_types (
    material_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_type_name TEXT NOT NULL UNIQUE,
    waste_percentage REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS product_types (
    product_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_type_name TEXT NOT NULL UNIQUE,
    coefficient REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS materials (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_name TEXT NOT NULL,
    material_type_id INTEGER NOT NULL,
    FOREIGN KEY (material_type_id) REFERENCES material_types(material_type_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    product_type_id INTEGER NOT NULL,
    FOREIGN KEY (product_type_id) REFERENCES product_types(product_type_id)
);

CREATE TABLE IF NOT EXISTS partners (
    partner_id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    registration_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS partner_products (
    partner_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES partners(partner_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES partners(partner_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_partners_name ON partners(partner_name);
CREATE INDEX IF NOT EXISTS idx_sales_partner ON sales(partner_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_products_type ON products(product_type_id);
CREATE INDEX IF NOT EXISTS idx_materials_type ON materials(material_type_id);
