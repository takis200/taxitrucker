BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "airlines" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	"entrance"	INTEGER CHECK("entrance" IS NULL OR ("entrance" >= 1 AND "entrance" <= 4)),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "app_earnings" (
	"date"	TEXT,
	"freenow"	REAL DEFAULT 0,
	"uber"	REAL DEFAULT 0,
	"bolt"	REAL DEFAULT 0,
	"extras"	REAL DEFAULT 0,
	PRIMARY KEY("date")
);
CREATE TABLE IF NOT EXISTS "credit_check" (
	"id"	INTEGER,
	"date"	TEXT NOT NULL UNIQUE,
	"start_balance"	INTEGER DEFAULT 0,
	"end_balance"	INTEGER DEFAULT 0,
	"added_credits"	INTEGER DEFAULT 0,
	"correction"	INTEGER DEFAULT 0,
	"debt_source"	TEXT,
	"is_paid"	INTEGER DEFAULT 1,
	"notes"	TEXT,
	"paid_date"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "credit_transactions" (
	"id"	INTEGER,
	"credit_check_id"	INTEGER NOT NULL,
	"transaction_type"	TEXT NOT NULL,
	"transaction_date"	TEXT NOT NULL,
	"amount"	INTEGER NOT NULL,
	"debt_source"	TEXT,
	"notes"	TEXT,
	"created_at"	TEXT NOT NULL DEFAULT (datetime('now')),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("credit_check_id") REFERENCES "credit_check"("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "destinations" (
	"id"	INTEGER,
	"name"	TEXT,
	"sort_order"	INTEGER DEFAULT 0,
	"is_active"	INTEGER DEFAULT 1,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "drivers" (
	"id"	INTEGER,
	"col_new"	TEXT,
	"col_old"	TEXT,
	"name"	TEXT NOT NULL,
	"phone"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "expenses" (
	"date"	TEXT,
	"fuel"	REAL DEFAULT 0,
	"misc"	REAL DEFAULT 0,
	PRIMARY KEY("date")
);
CREATE TABLE IF NOT EXISTS "hotels" (
	"id"	INTEGER,
	"name"	TEXT,
	"sort_order"	INTEGER DEFAULT 0,
	"is_active"	INTEGER DEFAULT 1,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "rates" (
	"hotel_id"	INTEGER,
	"dest_id"	INTEGER,
	"credits"	REAL,
	FOREIGN KEY("dest_id") REFERENCES "destinations"("id"),
	FOREIGN KEY("hotel_id") REFERENCES "hotels"("id")
);
CREATE TABLE IF NOT EXISTS "rides" (
	"id"	INTEGER,
	"date"	TEXT,
	"hotel_name"	TEXT,
	"dest_name"	TEXT,
	"price"	REAL,
	"tolls"	REAL,
	"credits_charged"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "service_lines" (
	"id"	INTEGER,
	"service_id"	INTEGER NOT NULL,
	"part_code"	TEXT,
	"part_description"	TEXT NOT NULL,
	"qty"	REAL NOT NULL DEFAULT 1,
	"unit_price"	REAL NOT NULL DEFAULT 0,
	"line_total"	REAL NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("service_id") REFERENCES "services"("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "services" (
	"id"	INTEGER,
	"service_date"	TEXT NOT NULL,
	"odometer_km"	INTEGER NOT NULL,
	"workshop_name"	TEXT NOT NULL,
	"labor_cost"	REAL NOT NULL DEFAULT 0,
	"note"	TEXT,
	"created_at"	TEXT NOT NULL DEFAULT (datetime('now')),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "settings" (
	"key"	TEXT,
	"value"	TEXT,
	PRIMARY KEY("key")
);
CREATE TABLE IF NOT EXISTS "spare_parts" (
	"id"	INTEGER,
	"code"	TEXT,
	"description"	TEXT NOT NULL,
	"notes"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "workshop_types" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "workshops" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	"phone"	TEXT,
	"address"	TEXT,
	"type_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("type_id") REFERENCES "workshop_types"("id")
);
CREATE INDEX IF NOT EXISTS "idx_lines_description" ON "service_lines" (
	"part_description"
);
CREATE INDEX IF NOT EXISTS "idx_lines_service_id" ON "service_lines" (
	"service_id"
);
CREATE INDEX IF NOT EXISTS "idx_services_date" ON "services" (
	"service_date"
);
CREATE INDEX IF NOT EXISTS "idx_transactions_credit_check" ON "credit_transactions" (
	"credit_check_id"
);
CREATE INDEX IF NOT EXISTS "idx_transactions_date" ON "credit_transactions" (
	"transaction_date"
);
CREATE INDEX IF NOT EXISTS "idx_transactions_type" ON "credit_transactions" (
	"transaction_type"
);
CREATE UNIQUE INDEX IF NOT EXISTS "ux_hotels_name" ON "hotels" (
	"name"
);
COMMIT;
