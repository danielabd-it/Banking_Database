
-- ── PERSON ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Person (
    SIN         CHAR(9)       PRIMARY KEY,
    FullName    VARCHAR(100)  NOT NULL,
    DateOfBirth DATE          NOT NULL,
    PhoneNumber VARCHAR(20),
    Address     VARCHAR(200)
);

-- ── ACCOUNT ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS Account (
    SIN CHAR(9) PRIMARY KEY,
    FOREIGN KEY (SIN) REFERENCES Person(SIN) ON DELETE CASCADE
);

-- ── CHEQUING ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Chequing (
    AccountID CHAR(12)        PRIMARY KEY,
    Pin       CHAR(4)         NOT NULL,
    SIN       CHAR(9)         NOT NULL,
    Balance   DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    FOREIGN KEY (SIN) REFERENCES Account(SIN) ON DELETE CASCADE
);

-- ── SAVINGS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Savings (
    AccountID    CHAR(12)      PRIMARY KEY,
    Pin          CHAR(4)       NOT NULL,
    InterestRate DECIMAL(5,2)  NOT NULL DEFAULT 3.00,
    SIN          CHAR(9)       NOT NULL,
    Balance      DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (SIN) REFERENCES Account(SIN) ON DELETE CASCADE
);

-- ── DEPOSIT ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Deposit (
    DepositID   INT AUTO_INCREMENT PRIMARY KEY,
    Amount      DECIMAL(12,2) NOT NULL,
    SIN         CHAR(9)       NOT NULL,
    AccountID   CHAR(12)      NOT NULL,
    AccountType ENUM('chequing','savings') NOT NULL,
    CreatedAt   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SIN) REFERENCES Account(SIN)
);

-- ── TRANSFER ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Transfer (
    TransferID      INT AUTO_INCREMENT PRIMARY KEY,
    Amount          DECIMAL(12,2) NOT NULL,
    SIN             CHAR(9)       NOT NULL,
    FromAccountID   CHAR(12)      NOT NULL,
    FromAccountType ENUM('chequing','savings') NOT NULL,
    ToAccountID     CHAR(12)      NOT NULL,
    ToAccountType   ENUM('chequing','savings') NOT NULL,
    CreatedAt       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SIN) REFERENCES Account(SIN)
);

-- ── PAYBILLS ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS PayBills (
    PayBillID   INT AUTO_INCREMENT PRIMARY KEY,
    Amount      DECIMAL(12,2) NOT NULL,
    SIN         CHAR(9)       NOT NULL,
    AccountID   CHAR(12)      NOT NULL,
    AccountType ENUM('chequing','savings') NOT NULL,
    PayeeName   VARCHAR(100),
    CreatedAt   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SIN) REFERENCES Account(SIN)
);

-- ── CLOSEACCOUNT ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS CloseAccount (
    CloseID     INT AUTO_INCREMENT PRIMARY KEY,
    SIN         CHAR(9)  NOT NULL,
    AccountID   CHAR(12) NOT NULL,
    AccountType ENUM('chequing','savings') NOT NULL,
    ClosedAt    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SIN) REFERENCES Account(SIN)
);

-- ── PAYEE ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Payee (
    PayeeID     INT AUTO_INCREMENT PRIMARY KEY,
    SIN         CHAR(9)      NOT NULL,
    AccountID   CHAR(12)     NOT NULL,
    AccountType ENUM('chequing','savings') NOT NULL,
    PayeeName   VARCHAR(100) NOT NULL,
    PayeeNumber VARCHAR(30),
    PayeeEmail  VARCHAR(100),
    FOREIGN KEY (SIN) REFERENCES Account(SIN)
);

-- ============================================================
--  SAMPLE DATA
-- ============================================================

INSERT IGNORE INTO Person (SIN, FullName, DateOfBirth, PhoneNumber, Address) VALUES
  ('123456789', 'Alice Johnson',   '1990-04-15', '416-555-0101', '10 Maple Ave, Toronto ON'),
  ('987654321', 'Bob Martinez',    '1985-11-22', '647-555-0202', '55 Oak St, Mississauga ON'),
  ('111222333', 'Carol White',     '2000-07-08', '905-555-0303', '88 Pine Rd, Brampton ON'),
  ('444555666', 'David Chen',      '1978-03-30', '416-555-0404', '22 Birch Blvd, Toronto ON'),
  ('777888999', 'Emma Patel',      '1995-09-14', '647-555-0505', '301 Queen St W, Toronto ON'),
  ('222333444', 'Frank Okafor',    '1982-06-25', '905-555-0606', '14 Cedar Lane, Oakville ON'),
  ('555666777', 'Grace Kim',       '1998-12-01', '416-555-0707', '9 Elm Dr, North York ON'),
  ('888999000', 'Henry Tremblay',  '1970-08-17', '514-555-0808', '77 Rue St-Denis, Montreal QC'),
  ('333444555', 'Isabella Rossi',  '1993-02-28', '604-555-0909', '200 Granville St, Vancouver BC'),
  ('666777888', 'James Nguyen',    '1988-11-05', '780-555-1010', '45 Jasper Ave, Edmonton AB');

INSERT IGNORE INTO Account (SIN) VALUES
  ('123456789'), ('987654321'), ('111222333'), ('444555666'), ('777888999'),
  ('222333444'), ('555666777'), ('888999000'), ('333444555'), ('666777888');

INSERT IGNORE INTO Chequing (AccountID, Pin, SIN, Balance) VALUES
  ('100000000001', '1234', '123456789',  2500.00),
  ('100000000002', '5678', '987654321',  1800.50),
  ('100000000003', '2222', '444555666',  4750.25),
  ('100000000004', '3333', '777888999',   950.00),
  ('100000000005', '4444', '222333444',  6200.75),
  ('100000000006', '5555', '555666777',  3100.00),
  ('100000000007', '6666', '888999000', 11400.90),
  ('100000000008', '7777', '333444555',  2200.40),
  ('100000000009', '8888', '666777888',  7800.60);

INSERT IGNORE INTO Savings (AccountID, Pin, InterestRate, SIN, Balance) VALUES
  ('200000000001', '4321', 3.00, '123456789', 10000.00),
  ('200000000002', '8765', 3.00, '111222333',  5400.75),
  ('200000000003', '1111', 3.00, '444555666', 22000.00),
  ('200000000004', '2222', 3.00, '777888999',  1250.50),
  ('200000000005', '3333', 3.00, '222333444',  8900.00),
  ('200000000006', '4444', 3.00, '555666777',  3350.25),
  ('200000000007', '5555', 3.00, '888999000', 45000.00),
  ('200000000008', '6666', 3.00, '333444555',  6780.00),
  ('200000000009', '7777', 3.00, '666777888', 15200.75);

INSERT IGNORE INTO Deposit (Amount, SIN, AccountID, AccountType) VALUES
  (1000.00, '123456789', '100000000001', 'chequing'),
  ( 500.00, '987654321', '100000000002', 'chequing'),
  (2500.00, '444555666', '200000000003', 'savings'),
  ( 750.00, '777888999', '100000000004', 'chequing'),
  (3000.00, '222333444', '200000000005', 'savings'),
  ( 200.00, '555666777', '100000000006', 'chequing'),
  (5000.00, '888999000', '200000000007', 'savings'),
  ( 400.00, '333444555', '100000000008', 'chequing'),
  (1200.00, '666777888', '200000000009', 'savings');

INSERT IGNORE INTO Transfer (Amount, SIN, FromAccountID, FromAccountType, ToAccountID, ToAccountType) VALUES
  ( 300.00, '123456789', '100000000001', 'chequing', '200000000001', 'savings'),
  ( 150.00, '444555666', '200000000003', 'savings',  '100000000003', 'chequing'),
  (1000.00, '888999000', '200000000007', 'savings',  '100000000007', 'chequing'),
  ( 250.00, '222333444', '100000000005', 'chequing', '200000000005', 'savings');

INSERT IGNORE INTO PayBills (Amount, SIN, AccountID, AccountType, PayeeName) VALUES
  ( 120.50, '123456789', '100000000001', 'chequing', 'Hydro One'),
  (  85.00, '987654321', '100000000002', 'chequing', 'Rogers Cable'),
  ( 200.00, '444555666', '100000000003', 'chequing', 'Bell Canada'),
  (  65.00, '777888999', '100000000004', 'chequing', 'Enbridge Gas'),
  ( 310.00, '222333444', '200000000005', 'savings',  'Toronto Water'),
  (  99.99, '555666777', '100000000006', 'chequing', 'Netflix'),
  ( 450.00, '888999000', '100000000007', 'chequing', 'Property Tax'),
  (  55.00, '333444555', '100000000008', 'chequing', 'Spotify'),
  ( 175.00, '666777888', '200000000009', 'savings',  'Cogeco Internet');

INSERT IGNORE INTO Payee (SIN, AccountID, AccountType, PayeeName, PayeeNumber, PayeeEmail) VALUES
  ('123456789', '100000000001', 'chequing', 'Hydro One',       '800-123-4567', 'billing@hydroone.ca'),
  ('987654321', '100000000002', 'chequing', 'Rogers Cable',    '888-764-3771', 'pay@rogers.com'),
  ('444555666', '100000000003', 'chequing', 'Bell Canada',     '800-667-2355', 'billing@bell.ca'),
  ('777888999', '100000000004', 'chequing', 'Enbridge Gas',    '877-362-7434', 'service@enbridge.com'),
  ('222333444', '200000000005', 'savings',  'Toronto Water',   '416-338-8888', 'water@toronto.ca'),
  ('555666777', '100000000006', 'chequing', 'Netflix',         '800-585-7265', 'support@netflix.com'),
  ('888999000', '100000000007', 'chequing', 'Property Tax',    '416-397-5311', 'tax@toronto.ca'),
  ('333444555', '100000000008', 'chequing', 'Spotify',         '800-123-9999', 'billing@spotify.com'),
  ('666777888', '200000000009', 'savings',  'Cogeco Internet', '855-701-4881', 'billing@cogeco.ca');
