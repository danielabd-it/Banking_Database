from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__, template_folder="templates")

# ── Database path ─────────────────────────────────────────────
# The .db file lives next to app.py. On PythonAnywhere or Railway
# this file persists across restarts; on Render free tier it resets
# on each deploy (data is lost, but the schema re-seeds itself).
DB_PATH = os.path.join(os.path.dirname(__file__), "bank.db")


# ── Schema + seed (runs once on startup) ─────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Enable foreign-key enforcement (off by default in SQLite)
    cur.execute("PRAGMA foreign_keys = ON")

    cur.executescript("""
    -- ── PERSON ───────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS Person (
        SIN         TEXT PRIMARY KEY,
        FullName    TEXT NOT NULL,
        DateOfBirth TEXT NOT NULL,
        PhoneNumber TEXT,
        Address     TEXT
    );

    -- ── ACCOUNT ──────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS Account (
        SIN TEXT PRIMARY KEY,
        FOREIGN KEY (SIN) REFERENCES Person(SIN) ON DELETE CASCADE
    );

    -- ── CHEQUING ─────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS Chequing (
        AccountID TEXT    PRIMARY KEY,
        Pin       TEXT    NOT NULL,
        SIN       TEXT    NOT NULL,
        Balance   REAL    NOT NULL DEFAULT 0.00,
        FOREIGN KEY (SIN) REFERENCES Account(SIN) ON DELETE CASCADE
    );

    -- ── SAVINGS ──────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS Savings (
        AccountID    TEXT PRIMARY KEY,
        Pin          TEXT NOT NULL,
        InterestRate REAL NOT NULL DEFAULT 3.00,
        SIN          TEXT NOT NULL,
        Balance      REAL NOT NULL DEFAULT 0.00,
        FOREIGN KEY (SIN) REFERENCES Account(SIN) ON DELETE CASCADE
    );

    -- ── DEPOSIT ──────────────────────────────────────────────
    -- SQLite uses INTEGER PRIMARY KEY for auto-increment
    CREATE TABLE IF NOT EXISTS Deposit (
        DepositID   INTEGER PRIMARY KEY AUTOINCREMENT,
        Amount      REAL    NOT NULL,
        SIN         TEXT    NOT NULL,
        AccountID   TEXT    NOT NULL,
        AccountType TEXT    NOT NULL CHECK(AccountType IN ('chequing','savings')),
        CreatedAt   TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY (SIN) REFERENCES Account(SIN)
    );

    -- ── TRANSFER ─────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS Transfer (
        TransferID      INTEGER PRIMARY KEY AUTOINCREMENT,
        Amount          REAL NOT NULL,
        SIN             TEXT NOT NULL,
        FromAccountID   TEXT NOT NULL,
        FromAccountType TEXT NOT NULL CHECK(FromAccountType IN ('chequing','savings')),
        ToAccountID     TEXT NOT NULL,
        ToAccountType   TEXT NOT NULL CHECK(ToAccountType IN ('chequing','savings')),
        CreatedAt       TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (SIN) REFERENCES Account(SIN)
    );

    -- ── PAYBILLS ─────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS PayBills (
        PayBillID   INTEGER PRIMARY KEY AUTOINCREMENT,
        Amount      REAL NOT NULL,
        SIN         TEXT NOT NULL,
        AccountID   TEXT NOT NULL,
        AccountType TEXT NOT NULL CHECK(AccountType IN ('chequing','savings')),
        PayeeName   TEXT,
        CreatedAt   TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (SIN) REFERENCES Account(SIN)
    );

    -- ── CLOSEACCOUNT ─────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS CloseAccount (
        CloseID     INTEGER PRIMARY KEY AUTOINCREMENT,
        SIN         TEXT NOT NULL,
        AccountID   TEXT NOT NULL,
        AccountType TEXT NOT NULL CHECK(AccountType IN ('chequing','savings')),
        ClosedAt    TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (SIN) REFERENCES Account(SIN)
    );

    -- ── PAYEE ────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS Payee (
        PayeeID     INTEGER PRIMARY KEY AUTOINCREMENT,
        SIN         TEXT NOT NULL,
        AccountID   TEXT NOT NULL,
        AccountType TEXT NOT NULL CHECK(AccountType IN ('chequing','savings')),
        PayeeName   TEXT NOT NULL,
        PayeeNumber TEXT,
        PayeeEmail  TEXT,
        FOREIGN KEY (SIN) REFERENCES Account(SIN)
    );
    """)

    # ── Seed only when tables are empty ──────────────────────
    if cur.execute("SELECT COUNT(*) FROM Person").fetchone()[0] == 0:
        cur.executescript("""
        INSERT INTO Person VALUES
          ('123456789','Alice Johnson',  '1990-04-15','416-555-0101','10 Maple Ave, Toronto ON'),
          ('987654321','Bob Martinez',   '1985-11-22','647-555-0202','55 Oak St, Mississauga ON'),
          ('111222333','Carol White',    '2000-07-08','905-555-0303','88 Pine Rd, Brampton ON'),
          ('444555666','David Chen',     '1978-03-30','416-555-0404','22 Birch Blvd, Toronto ON'),
          ('777888999','Emma Patel',     '1995-09-14','647-555-0505','301 Queen St W, Toronto ON'),
          ('222333444','Frank Okafor',   '1982-06-25','905-555-0606','14 Cedar Lane, Oakville ON'),
          ('555666777','Grace Kim',      '1998-12-01','416-555-0707','9 Elm Dr, North York ON'),
          ('888999000','Henry Tremblay', '1970-08-17','514-555-0808','77 Rue St-Denis, Montreal QC'),
          ('333444555','Isabella Rossi', '1993-02-28','604-555-0909','200 Granville St, Vancouver BC'),
          ('666777888','James Nguyen',   '1988-11-05','780-555-1010','45 Jasper Ave, Edmonton AB');

        INSERT INTO Account VALUES
          ('123456789'),('987654321'),('111222333'),('444555666'),('777888999'),
          ('222333444'),('555666777'),('888999000'),('333444555'),('666777888');

        INSERT INTO Chequing VALUES
          ('100000000001','1234','123456789', 2500.00),
          ('100000000002','5678','987654321', 1800.50),
          ('100000000003','2222','444555666', 4750.25),
          ('100000000004','3333','777888999',  950.00),
          ('100000000005','4444','222333444', 6200.75),
          ('100000000006','5555','555666777', 3100.00),
          ('100000000007','6666','888999000',11400.90),
          ('100000000008','7777','333444555', 2200.40),
          ('100000000009','8888','666777888', 7800.60);

        INSERT INTO Savings VALUES
          ('200000000001','4321',3.00,'123456789',10000.00),
          ('200000000002','8765',3.00,'111222333', 5400.75),
          ('200000000003','1111',3.00,'444555666',22000.00),
          ('200000000004','2222',3.00,'777888999', 1250.50),
          ('200000000005','3333',3.00,'222333444', 8900.00),
          ('200000000006','4444',3.00,'555666777', 3350.25),
          ('200000000007','5555',3.00,'888999000',45000.00),
          ('200000000008','6666',3.00,'333444555', 6780.00),
          ('200000000009','7777',3.00,'666777888',15200.75);

        INSERT INTO Deposit(Amount,SIN,AccountID,AccountType) VALUES
          (1000.00,'123456789','100000000001','chequing'),
          ( 500.00,'987654321','100000000002','chequing'),
          (2500.00,'444555666','200000000003','savings'),
          ( 750.00,'777888999','100000000004','chequing'),
          (3000.00,'222333444','200000000005','savings'),
          ( 200.00,'555666777','100000000006','chequing'),
          (5000.00,'888999000','200000000007','savings'),
          ( 400.00,'333444555','100000000008','chequing'),
          (1200.00,'666777888','200000000009','savings');

        INSERT INTO Transfer(Amount,SIN,FromAccountID,FromAccountType,ToAccountID,ToAccountType) VALUES
          ( 300.00,'123456789','100000000001','chequing','200000000001','savings'),
          ( 150.00,'444555666','200000000003','savings', '100000000003','chequing'),
          (1000.00,'888999000','200000000007','savings', '100000000007','chequing'),
          ( 250.00,'222333444','100000000005','chequing','200000000005','savings');

        INSERT INTO PayBills(Amount,SIN,AccountID,AccountType,PayeeName) VALUES
          ( 120.50,'123456789','100000000001','chequing','Hydro One'),
          (  85.00,'987654321','100000000002','chequing','Rogers Cable'),
          ( 200.00,'444555666','100000000003','chequing','Bell Canada'),
          (  65.00,'777888999','100000000004','chequing','Enbridge Gas'),
          ( 310.00,'222333444','200000000005','savings', 'Toronto Water'),
          (  99.99,'555666777','100000000006','chequing','Netflix'),
          ( 450.00,'888999000','100000000007','chequing','Property Tax'),
          (  55.00,'333444555','100000000008','chequing','Spotify'),
          ( 175.00,'666777888','200000000009','savings', 'Cogeco Internet');

        INSERT INTO Payee(SIN,AccountID,AccountType,PayeeName,PayeeNumber,PayeeEmail) VALUES
          ('123456789','100000000001','chequing','Hydro One',      '800-123-4567','billing@hydroone.ca'),
          ('987654321','100000000002','chequing','Rogers Cable',   '888-764-3771','pay@rogers.com'),
          ('444555666','100000000003','chequing','Bell Canada',    '800-667-2355','billing@bell.ca'),
          ('777888999','100000000004','chequing','Enbridge Gas',   '877-362-7434','service@enbridge.com'),
          ('222333444','200000000005','savings', 'Toronto Water',  '416-338-8888','water@toronto.ca'),
          ('555666777','100000000006','chequing','Netflix',        '800-585-7265','support@netflix.com'),
          ('888999000','100000000007','chequing','Property Tax',   '416-397-5311','tax@toronto.ca'),
          ('333444555','100000000008','chequing','Spotify',        '800-123-9999','billing@spotify.com'),
          ('666777888','200000000009','savings', 'Cogeco Internet','855-701-4881','billing@cogeco.ca');
        """)

    con.commit()
    con.close()


# ── Database helper ───────────────────────────────────────────
def get_db():
    """Return a connection with row_factory so rows behave like dicts."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row          # rows accessible as row["ColumnName"]
    con.execute("PRAGMA foreign_keys = ON")
    return con


# ── Row → dict conversion (so Jinja templates work identically) ──
def rows(cur):
    return [dict(r) for r in cur.fetchall()]

def row(cur):
    r = cur.fetchone()
    return dict(r) if r else None


# ── Database class (mirrors original API exactly) ─────────────
class Database:

    def __init__(self):
        self.con = get_db()
        self.cur = self.con.cursor()

    def close(self):
        self.con.close()

    def commit_close(self):
        self.con.commit()
        self.con.close()

    # ── PERSON ──────────────────────────────────────────────
    def get_all_persons(self):
        self.cur.execute("""
            SELECT SIN, FullName, DateOfBirth, PhoneNumber, Address
            FROM Person ORDER BY FullName
        """)
        r = rows(self.cur); self.close(); return r

    def get_person(self, sin):
        self.cur.execute("""
            SELECT SIN, FullName, DateOfBirth, PhoneNumber, Address
            FROM Person WHERE SIN=?
        """, (sin,))
        r = row(self.cur); self.close(); return r

    def insert_person(self, sin, name, dob, phone, address):
        try:
            self.cur.execute(
                "INSERT INTO Person(SIN,FullName,DateOfBirth,PhoneNumber,Address) VALUES(?,?,?,?,?)",
                (sin, name, dob, phone, address))
            self.cur.execute("INSERT INTO Account(SIN) VALUES(?)", (sin,))
            self.commit_close()
            return "✓ Person registered successfully."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_person(self, sin, name, dob, phone, address):
        try:
            self.cur.execute(
                "UPDATE Person SET FullName=?,DateOfBirth=?,PhoneNumber=?,Address=? WHERE SIN=?",
                (name, dob, phone, address, sin))
            self.commit_close(); return "✓ Person updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_person(self, sin):
        try:
            self.cur.execute("DELETE FROM Person WHERE SIN=?", (sin,))
            self.commit_close(); return "✓ Person and linked accounts deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── CHEQUING ────────────────────────────────────────────
    def get_all_chequing(self):
        self.cur.execute("""
            SELECT c.AccountID, c.Pin, c.SIN, c.Balance, p.FullName
            FROM Chequing c INNER JOIN Person p ON c.SIN=p.SIN
            ORDER BY c.AccountID
        """)
        r = rows(self.cur); self.close(); return r

    def get_chequing(self, aid):
        self.cur.execute("""
            SELECT AccountID, Pin, SIN, Balance FROM Chequing WHERE AccountID=?
        """, (aid,))
        r = row(self.cur); self.close(); return r

    def insert_chequing(self, account_id, pin, sin):
        try:
            self.cur.execute(
                "INSERT INTO Chequing(AccountID,Pin,SIN,Balance) VALUES(?,?,?,0.00)",
                (account_id, pin, sin))
            self.commit_close(); return "✓ Chequing account created."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_chequing(self, aid, pin, balance):
        try:
            self.cur.execute(
                "UPDATE Chequing SET Pin=?,Balance=? WHERE AccountID=?",
                (pin, balance, aid))
            self.commit_close(); return "✓ Chequing account updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_chequing(self, aid):
        try:
            self.cur.execute("DELETE FROM Chequing WHERE AccountID=?", (aid,))
            self.commit_close(); return "✓ Chequing account deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── SAVINGS ─────────────────────────────────────────────
    def get_all_savings(self):
        self.cur.execute("""
            SELECT s.AccountID, s.Pin, s.SIN, s.Balance, s.InterestRate, p.FullName
            FROM Savings s INNER JOIN Person p ON s.SIN=p.SIN
            ORDER BY s.AccountID
        """)
        r = rows(self.cur); self.close(); return r

    def get_savings(self, aid):
        self.cur.execute("""
            SELECT AccountID, Pin, SIN, Balance, InterestRate
            FROM Savings WHERE AccountID=?
        """, (aid,))
        r = row(self.cur); self.close(); return r

    def insert_savings(self, account_id, pin, sin):
        try:
            self.cur.execute(
                "INSERT INTO Savings(AccountID,Pin,InterestRate,SIN,Balance) VALUES(?,?,3.00,?,0.00)",
                (account_id, pin, sin))
            self.commit_close(); return "✓ Savings account created."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_savings(self, aid, pin, balance):
        try:
            self.cur.execute(
                "UPDATE Savings SET Pin=?,Balance=? WHERE AccountID=?",
                (pin, balance, aid))
            self.commit_close(); return "✓ Savings account updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_savings(self, aid):
        try:
            self.cur.execute("DELETE FROM Savings WHERE AccountID=?", (aid,))
            self.commit_close(); return "✓ Savings account deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── DEPOSIT ─────────────────────────────────────────────
    def get_all_deposits(self):
        self.cur.execute("""
            SELECT d.DepositID, d.Amount, d.SIN, d.AccountID,
                   d.AccountType, d.CreatedAt, p.FullName
            FROM Deposit d INNER JOIN Person p ON d.SIN=p.SIN
            ORDER BY d.CreatedAt DESC
        """)
        r = rows(self.cur); self.close(); return r

    def insert_deposit(self, amount, sin, account_id, account_type):
        try:
            self.cur.execute(
                "INSERT INTO Deposit(Amount,SIN,AccountID,AccountType) VALUES(?,?,?,?)",
                (amount, sin, account_id, account_type))
            tbl = "Chequing" if account_type == "chequing" else "Savings"
            self.cur.execute(f"UPDATE {tbl} SET Balance=Balance+? WHERE AccountID=?", (amount, account_id))
            self.commit_close(); return "✓ Deposit recorded."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_deposit(self, dep_id):
        try:
            self.cur.execute("DELETE FROM Deposit WHERE DepositID=?", (dep_id,))
            self.commit_close(); return "✓ Deposit record deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── TRANSFER ────────────────────────────────────────────
    def get_all_transfers(self):
        self.cur.execute("""
            SELECT t.TransferID, t.Amount, t.SIN,
                   t.FromAccountID, t.FromAccountType,
                   t.ToAccountID,   t.ToAccountType,
                   t.CreatedAt, p.FullName
            FROM Transfer t INNER JOIN Person p ON t.SIN=p.SIN
            ORDER BY t.CreatedAt DESC
        """)
        r = rows(self.cur); self.close(); return r

    def insert_transfer(self, amount, sin, from_id, from_type, to_id, to_type):
        try:
            self.cur.execute(
                """INSERT INTO Transfer
                   (Amount,SIN,FromAccountID,FromAccountType,ToAccountID,ToAccountType)
                   VALUES(?,?,?,?,?,?)""",
                (amount, sin, from_id, from_type, to_id, to_type))
            tbl_from = "Chequing" if from_type == "chequing" else "Savings"
            tbl_to   = "Chequing" if to_type   == "chequing" else "Savings"
            self.cur.execute(f"UPDATE {tbl_from} SET Balance=Balance-? WHERE AccountID=?", (amount, from_id))
            self.cur.execute(f"UPDATE {tbl_to}   SET Balance=Balance+? WHERE AccountID=?", (amount, to_id))
            self.commit_close(); return "✓ Transfer completed."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_transfer(self, tid):
        try:
            self.cur.execute("DELETE FROM Transfer WHERE TransferID=?", (tid,))
            self.commit_close(); return "✓ Transfer record deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── PAY BILLS ───────────────────────────────────────────
    def get_all_paybills(self):
        self.cur.execute("""
            SELECT pb.PayBillID, pb.Amount, pb.SIN, pb.AccountID,
                   pb.AccountType, pb.PayeeName, pb.CreatedAt, p.FullName
            FROM PayBills pb INNER JOIN Person p ON pb.SIN=p.SIN
            ORDER BY pb.CreatedAt DESC
        """)
        r = rows(self.cur); self.close(); return r

    def insert_paybill(self, amount, sin, account_id, account_type, payee_name):
        try:
            self.cur.execute(
                "INSERT INTO PayBills(Amount,SIN,AccountID,AccountType,PayeeName) VALUES(?,?,?,?,?)",
                (amount, sin, account_id, account_type, payee_name))
            tbl = "Chequing" if account_type == "chequing" else "Savings"
            self.cur.execute(f"UPDATE {tbl} SET Balance=Balance-? WHERE AccountID=?", (amount, account_id))
            self.commit_close(); return "✓ Bill payment recorded."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_paybill(self, pbid):
        try:
            self.cur.execute("DELETE FROM PayBills WHERE PayBillID=?", (pbid,))
            self.commit_close(); return "✓ Pay bill record deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── CLOSE ACCOUNT ───────────────────────────────────────
    def get_all_closed(self):
        self.cur.execute("""
            SELECT ca.CloseID, ca.SIN, ca.AccountID, ca.AccountType,
                   ca.ClosedAt, p.FullName
            FROM CloseAccount ca INNER JOIN Person p ON ca.SIN=p.SIN
            ORDER BY ca.ClosedAt DESC
        """)
        r = rows(self.cur); self.close(); return r

    def close_account(self, sin, account_id, account_type):
        try:
            self.cur.execute(
                "INSERT INTO CloseAccount(SIN,AccountID,AccountType) VALUES(?,?,?)",
                (sin, account_id, account_type))
            tbl = "Chequing" if account_type == "chequing" else "Savings"
            self.cur.execute(f"DELETE FROM {tbl} WHERE AccountID=?", (account_id,))
            self.commit_close(); return "✓ Account closed."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── PAYEE ───────────────────────────────────────────────
    def get_all_payees(self):
        self.cur.execute("""
            SELECT py.PayeeID, py.SIN, py.AccountID, py.AccountType,
                   py.PayeeName, py.PayeeNumber, py.PayeeEmail, p.FullName
            FROM Payee py INNER JOIN Person p ON py.SIN=p.SIN
            ORDER BY py.PayeeName
        """)
        r = rows(self.cur); self.close(); return r

    def get_payee(self, pid):
        self.cur.execute("""
            SELECT PayeeID, SIN, AccountID, AccountType,
                   PayeeName, PayeeNumber, PayeeEmail
            FROM Payee WHERE PayeeID=?
        """, (pid,))
        r = row(self.cur); self.close(); return r

    def insert_payee(self, sin, account_id, account_type, name, number, email):
        try:
            self.cur.execute(
                """INSERT INTO Payee(SIN,AccountID,AccountType,PayeeName,PayeeNumber,PayeeEmail)
                   VALUES(?,?,?,?,?,?)""",
                (sin, account_id, account_type, name, number, email))
            self.commit_close(); return "✓ Payee added."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_payee(self, pid, name, number, email):
        try:
            self.cur.execute(
                "UPDATE Payee SET PayeeName=?,PayeeNumber=?,PayeeEmail=? WHERE PayeeID=?",
                (name, number, email, pid))
            self.commit_close(); return "✓ Payee updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_payee(self, pid):
        try:
            self.cur.execute("DELETE FROM Payee WHERE PayeeID=?", (pid,))
            self.commit_close(); return "✓ Payee deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── HELPERS ─────────────────────────────────────────────
    def get_persons_list(self):
        self.cur.execute("SELECT SIN, FullName FROM Person ORDER BY FullName")
        r = rows(self.cur); self.close(); return r

    def get_all_accounts_flat(self):
        self.cur.execute("""
            SELECT AccountID, 'chequing' AS Type, SIN FROM Chequing
            UNION
            SELECT AccountID, 'savings'  AS Type, SIN FROM Savings
        """)
        r = rows(self.cur); self.close(); return r

    # ── DASHBOARD JOIN ──────────────────────────────────────
    def get_join_summary(self):
        self.cur.execute("""
            SELECT
                p.SIN, p.FullName, p.PhoneNumber,
                c.AccountID  AS ChequingID,
                c.Balance    AS ChequingBal,
                s.AccountID  AS SavingsID,
                s.Balance    AS SavingsBal,
                s.InterestRate
            FROM Person p
            LEFT JOIN Chequing c ON p.SIN = c.SIN
            LEFT JOIN Savings  s ON p.SIN = s.SIN
            ORDER BY p.FullName
        """)
        r = rows(self.cur); self.close(); return r


# ── ROUTES (identical to original) ───────────────────────────

@app.route("/")
def home():
    db = Database()
    summary = db.get_join_summary()
    return render_template("index.html", summary=summary)

# ─ PERSONS ────────────────────────────────────────────────────
@app.route("/persons")
def persons():
    db = Database()
    p = db.get_all_persons()
    msg = request.args.get("msg", "")
    return render_template("persons.html", persons=p, msg=msg)

@app.route("/persons/new", methods=["GET", "POST"])
def person_new():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_person(f["sin"], f["name"], f["dob"], f["phone"], f["address"])
        if "✓" in msg:
            return redirect(url_for("persons", msg=msg))
    return render_template("person_form.html", person=None, msg=msg)

@app.route("/persons/edit/<sin>", methods=["GET", "POST"])
def person_edit(sin):
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.update_person(sin, f["name"], f["dob"], f["phone"], f["address"])
        if "✓" in msg:
            return redirect(url_for("persons", msg=msg))
    db = Database()
    person = db.get_person(sin)
    return render_template("person_form.html", person=person, msg=msg)

@app.route("/persons/delete/<sin>")
def person_delete(sin):
    db = Database()
    msg = db.delete_person(sin)
    return redirect(url_for("persons", msg=msg))

# ─ CHEQUING ───────────────────────────────────────────────────
@app.route("/chequing")
def chequing():
    db = Database()
    accounts = db.get_all_chequing()
    msg = request.args.get("msg", "")
    return render_template("chequing.html", accounts=accounts, msg=msg)

@app.route("/chequing/new", methods=["GET", "POST"])
def chequing_new():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_chequing(f["account_id"], f["pin"], f["sin"])
        if "✓" in msg:
            return redirect(url_for("chequing", msg=msg))
    db = Database()
    persons = db.get_persons_list()
    return render_template("account_form.html", account=None, account_type="chequing", persons=persons, msg=msg)

@app.route("/chequing/edit/<aid>", methods=["GET", "POST"])
def chequing_edit(aid):
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.update_chequing(aid, f["pin"], f["balance"])
        if "✓" in msg:
            return redirect(url_for("chequing", msg=msg))
    db = Database()
    account = db.get_chequing(aid)
    return render_template("account_form.html", account=account, account_type="chequing", persons=[], msg=msg)

@app.route("/chequing/delete/<aid>")
def chequing_delete(aid):
    db = Database()
    msg = db.delete_chequing(aid)
    return redirect(url_for("chequing", msg=msg))

# ─ SAVINGS ────────────────────────────────────────────────────
@app.route("/savings")
def savings():
    db = Database()
    accounts = db.get_all_savings()
    msg = request.args.get("msg", "")
    return render_template("savings.html", accounts=accounts, msg=msg)

@app.route("/savings/new", methods=["GET", "POST"])
def savings_new():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_savings(f["account_id"], f["pin"], f["sin"])
        if "✓" in msg:
            return redirect(url_for("savings", msg=msg))
    db = Database()
    persons = db.get_persons_list()
    return render_template("account_form.html", account=None, account_type="savings", persons=persons, msg=msg)

@app.route("/savings/edit/<aid>", methods=["GET", "POST"])
def savings_edit(aid):
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.update_savings(aid, f["pin"], f["balance"])
        if "✓" in msg:
            return redirect(url_for("savings", msg=msg))
    db = Database()
    account = db.get_savings(aid)
    return render_template("account_form.html", account=account, account_type="savings", persons=[], msg=msg)

@app.route("/savings/delete/<aid>")
def savings_delete(aid):
    db = Database()
    msg = db.delete_savings(aid)
    return redirect(url_for("savings", msg=msg))

# ─ DEPOSIT ────────────────────────────────────────────────────
@app.route("/deposits", methods=["GET", "POST"])
def deposits():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_deposit(f["amount"], f["sin"], f["account_id"], f["account_type"])
    db = Database()
    all_dep = db.get_all_deposits()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("deposits.html", deposits=all_dep, persons=persons, accounts=accounts, msg=msg)

@app.route("/deposits/delete/<int:did>")
def deposit_delete(did):
    db = Database()
    msg = db.delete_deposit(did)
    return redirect(url_for("deposits", msg=msg))

# ─ TRANSFER ───────────────────────────────────────────────────
@app.route("/transfers", methods=["GET", "POST"])
def transfers():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_transfer(f["amount"], f["sin"], f["from_id"], f["from_type"], f["to_id"], f["to_type"])
    db = Database()
    all_tr = db.get_all_transfers()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("transfers.html", transfers=all_tr, persons=persons, accounts=accounts, msg=msg)

@app.route("/transfers/delete/<int:tid>")
def transfer_delete(tid):
    db = Database()
    msg = db.delete_transfer(tid)
    return redirect(url_for("transfers"))

# ─ PAY BILLS ──────────────────────────────────────────────────
@app.route("/paybills", methods=["GET", "POST"])
def paybills():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_paybill(f["amount"], f["sin"], f["account_id"], f["account_type"], f["payee_name"])
    db = Database()
    all_pb = db.get_all_paybills()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("paybills.html", paybills=all_pb, persons=persons, accounts=accounts, msg=msg)

@app.route("/paybills/delete/<int:pbid>")
def paybill_delete(pbid):
    db = Database()
    msg = db.delete_paybill(pbid)
    return redirect(url_for("paybills"))

# ─ CLOSE ACCOUNT ──────────────────────────────────────────────
@app.route("/close", methods=["GET", "POST"])
def close_account():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.close_account(f["sin"], f["account_id"], f["account_type"])
    db = Database()
    closed = db.get_all_closed()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("close.html", closed=closed, persons=persons, accounts=accounts, msg=msg)

# ─ PAYEES ─────────────────────────────────────────────────────
@app.route("/payees")
def payees():
    db = Database()
    p = db.get_all_payees()
    msg = request.args.get("msg", "")
    return render_template("payees.html", payees=p, msg=msg)

@app.route("/payees/new", methods=["GET", "POST"])
def payee_new():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_payee(f["sin"], f["account_id"], f["account_type"],
                               f["payee_name"], f["payee_number"], f["payee_email"])
        if "✓" in msg:
            return redirect(url_for("payees", msg=msg))
    db = Database()
    persons = db.get_persons_list()
    db2 = Database()
    accounts = db2.get_all_accounts_flat()
    return render_template("payee_form.html", payee=None, persons=persons, accounts=accounts, msg=msg)

@app.route("/payees/edit/<int:pid>", methods=["GET", "POST"])
def payee_edit(pid):
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.update_payee(pid, f["payee_name"], f["payee_number"], f["payee_email"])
        if "✓" in msg:
            return redirect(url_for("payees", msg=msg))
    db = Database()
    payee = db.get_payee(pid)
    return render_template("payee_form.html", payee=payee, persons=[], accounts=[], msg=msg)

@app.route("/payees/delete/<int:pid>")
def payee_delete(pid):
    db = Database()
    msg = db.delete_payee(pid)
    return redirect(url_for("payees", msg=msg))


# ── Init + run ────────────────────────────────────────────────
init_db()   # create tables & seed data on every startup (idempotent)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
