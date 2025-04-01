-- Create accounts table
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Insert data into accounts table
INSERT INTO accounts (account_id, name)
VALUES (1, 'HBL');

-- Alter accounts table to add new columns
ALTER TABLE accounts
ADD COLUMN email VARCHAR(255),
ADD COLUMN phone VARCHAR(20),
ADD COLUMN balance DECIMAL(10, 2);

-- Update accounts table with new data
UPDATE accounts
SET email = 'abcd@gef.com',
    phone = '9876543210',
    balance = 99034.50;

-- Insert additional data into accounts table
INSERT INTO accounts (account_id, name, email, phone, balance)
VALUES (2, 'Vikas', 'abcd@gef.com', '9876543210', 123456.0);

-- Create CustomerData table
CREATE TABLE CustomerData (
    customer_id INTEGER PRIMARY KEY,
    card_blocked BOOLEAN NOT NULL,
    payment_due BOOLEAN NOT NULL,
    card_type VARCHAR(50) NOT NULL
);

-- Insert data into CustomerData table
INSERT INTO CustomerData (customer_id, card_blocked, payment_due, card_type)
VALUES (123456, TRUE, TRUE, 'Visa'),
       (136743, FALSE, FALSE, 'MasterCard'),
       (3, FALSE, FALSE, 'American Express'),
       (4, TRUE, FALSE, 'Discover');

-- Select all data from CustomerData table
SELECT * FROM CustomerData;

-- Create credit_card_transactions table
CREATE TABLE credit_card_transactions (
    credit_card_no VARCHAR(16),
    date TIMESTAMP,
    amount DECIMAL(10, 2),
    authentication_passed BOOLEAN,
    location VARCHAR(255)
);

-- Insert data into credit_card_transactions table
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4077106283143420', '2024-10-02 16:14:17', 349.48, True, 'Houston');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4774162118839779', '2024-04-06 16:14:17', 974.28, True, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4004158658075362', '2024-05-30 16:14:17', 256.17, False, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4778795403198778', '2025-03-10 16:14:17', 123.72, False, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4688716436990935', '2024-09-30 16:14:17', 939.14, False, 'Houston');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4822882507099932', '2024-04-18 16:14:17', 351.54, False, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4565637046732939', '2024-05-27 16:14:17', 571.24, False, 'Chicago');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4892152187353061', '2025-02-03 16:14:17', 341.99, True, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4303087961690568', '2025-03-15 16:14:17', 476.19, True, 'Los Angeles');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4824006637226271', '2024-09-08 16:14:17', 648.91, False, 'Chicago');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4349162177055178', '2025-02-09 16:14:17', 672.31, True, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4704137608622458', '2025-03-10 16:14:17', 583.52, True, 'Chicago');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4876785281249134', '2025-03-15 16:14:17', 171.28, False, 'Seattle');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4453346966317011', '2025-01-14 16:14:17', 789.57, False, 'Los Angeles');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4619804500999573', '2025-01-04 16:14:17', 735.21, True, 'Seattle');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4291670506071576', '2025-01-02 16:14:17', 139.76, False, 'Houston');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4377548740418179', '2024-08-02 16:14:17', 366.83, False, 'Seattle');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4297455967211179', '2024-07-22 16:14:17', 291.19, True, 'Chicago');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4850572536070264', '2024-07-19 16:14:17', 204.38, True, 'Seattle');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4586648403677834', '2025-03-11 16:14:17', 472.34, False, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4531012078934103', '2025-03-15 16:14:17', 979.03, True, 'Houston');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4368681593785338', '2025-03-20 16:14:17', 876.07, False, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4609460822264423', '2025-03-11 16:14:17', 965.89, False, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4894802703081846', '2024-11-24 16:14:17', 232.05, False, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4496943973329124', '2024-06-17 16:14:17', 501.86, True, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4883459785144073', '2024-07-28 16:14:17', 156.56, False, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4165056728900246', '2024-09-07 16:14:17', 65.43, False, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4785264483878320', '2024-08-17 16:14:17', 41.14, False, 'Los Angeles');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4798835049786550', '2024-12-27 16:14:17', 139.66, False, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4718851605080107', '2024-08-17 16:14:17', 398.85, False, 'Los Angeles');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4772996264221675', '2024-05-12 16:14:17', 242.34, True, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4742858481248372', '2025-01-17 16:14:17', 494.44, False, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4185924396770530', '2024-10-24 16:14:17', 748.06, True, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4058809618620144', '2025-03-14 16:14:17', 626.07, True, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4647522608256310', '2024-09-16 16:14:17', 730.43, False, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4557375285771860', '2024-08-12 16:14:17', 461.49, True, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4625179665372774', '2025-01-05 16:14:17', 214.47, True, 'Los Angeles');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4977547714431848', '2024-09-29 16:14:17', 508.21, True, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4246780030907609', '2024-10-15 16:14:17', 380.79, False, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4032398861142807', '2024-07-21 16:14:17', 427.58, False, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4907786547501846', '2024-05-14 16:14:17', 69.27, True, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4781677525423118', '2024-11-14 16:14:17', 160.33, False, 'Houston');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4210026238531169', '2025-01-14 16:14:17', 356.61, True, 'New York');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4811253172282038', '2024-04-11 16:14:17', 214.38, False, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4048817299402043', '2024-10-24 16:14:17', 921.9, False, 'Houston');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4732133515818437', '2024-10-21 16:14:17', 162.19, True, 'Seattle');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4845786167161730', '2024-10-17 16:14:17', 980.27, False, 'Los Angeles');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4344405338518683', '2024-12-02 16:14:17', 580.58, True, 'Phoenix');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4868817265652558', '2024-08-01 16:14:17', 87.1, True, 'San Francisco');
INSERT INTO credit_card_transactions (credit_card_no, date, amount, authentication_passed, location) VALUES ('4763789031888323', '2024-04-03 16:14:17', 819.99, True, 'Seattle');

-- Alter credit_card_transactions table to change column type
ALTER TABLE credit_card_transactions
ALTER COLUMN credit_card_no TYPE BIGINT USING credit_card_no::BIGINT;

-- Update credit_card_transactions table
UPDATE credit_card_transactions
SET credit_card_no = 4004158658075362,
    date = NOW()
WHERE authentication_passed = FALSE
  AND location = 'San Francisco';


-- Alter CustomerData table to add a new column
ALTER TABLE CustomerData
ADD COLUMN credit_card_no BIGINT NOT NULL DEFAULT '1234567812345678'::BIGINT;

update CustomerData
SET credit_card_no = 4004158658075362
WHERE customer_id = 123456;
