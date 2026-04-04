from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os

app = Flask(__name__, template_folder="templates")


# ── Database ──────────────────────────────────────────────────
class Database:

    def __init__(self):
        self.con = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PWD"),
            db=os.environ.get("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cur = self.con.cursor()

    def close(self):
        self.con.close()

    def commit_close(self):
        self.con.commit()
        self.con.close()

    # ── PERSON ──────────────────────────────────────────────
    def get_all_persons(self):
        self.cur.execute("SELECT * FROM Person ORDER BY FullName")
        r = self.cur.fetchall()
        self.close()
        return r

    def get_person(self, sin):
        self.cur.execute("SELECT * FROM Person WHERE SIN=%s", (sin,))
        r = self.cur.fetchone()
        self.close()
        return r

    def insert_person(self, sin, name, dob, phone, address):
        try:
            self.cur.execute(
                "INSERT INTO Person (SIN,FullName,DateOfBirth,PhoneNumber,Address) VALUES (%s,%s,%s,%s,%s)",
                (sin, name, dob, phone, address),
            )
            # Also create Account record (supertype)
            self.cur.execute("INSERT INTO Account (SIN) VALUES (%s)", (sin,))
            self.commit_close()
            return "✓ Person registered successfully."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def update_person(self, sin, name, dob, phone, address):
        try:
            self.cur.execute(
                "UPDATE Person SET FullName=%s,DateOfBirth=%s,PhoneNumber=%s,Address=%s WHERE SIN=%s",
                (name, dob, phone, address, sin),
            )
            self.commit_close()
            return "✓ Person updated."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_person(self, sin):
        try:
            self.cur.execute("DELETE FROM Person WHERE SIN=%s", (sin,))
            self.commit_close()
            return "✓ Person and linked accounts deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── CHEQUING ────────────────────────────────────────────
    def get_all_chequing(self):
        self.cur.execute(
            """
            SELECT c.*, p.FullName
            FROM Chequing c
            INNER JOIN Person p ON c.SIN = p.SIN
            ORDER BY c.AccountID"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def get_chequing(self, aid):
        self.cur.execute("SELECT * FROM Chequing WHERE AccountID=%s", (aid,))
        r = self.cur.fetchone()
        self.close()
        return r

    def insert_chequing(self, account_id, pin, sin):
        try:
            self.cur.execute(
                "INSERT INTO Chequing (AccountID,Pin,SIN,Balance) VALUES (%s,%s,%s,0.00)",
                (account_id, pin, sin),
            )
            self.commit_close()
            return "✓ Chequing account created."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def update_chequing(self, aid, pin, balance):
        try:
            self.cur.execute(
                "UPDATE Chequing SET Pin=%s, Balance=%s WHERE AccountID=%s",
                (pin, balance, aid),
            )
            self.commit_close()
            return "✓ Chequing account updated."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_chequing(self, aid):
        try:
            self.cur.execute("DELETE FROM Chequing WHERE AccountID=%s", (aid,))
            self.commit_close()
            return "✓ Chequing account deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── SAVINGS ─────────────────────────────────────────────
    def get_all_savings(self):
        self.cur.execute(
            """
            SELECT s.*, p.FullName
            FROM Savings s
            INNER JOIN Person p ON s.SIN = p.SIN
            ORDER BY s.AccountID"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def get_savings(self, aid):
        self.cur.execute("SELECT * FROM Savings WHERE AccountID=%s", (aid,))
        r = self.cur.fetchone()
        self.close()
        return r

    def insert_savings(self, account_id, pin, sin):
        try:
            self.cur.execute(
                "INSERT INTO Savings (AccountID,Pin,InterestRate,SIN,Balance) VALUES (%s,%s,3.00,%s,0.00)",
                (account_id, pin, sin),
            )
            self.commit_close()
            return "✓ Savings account created."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def update_savings(self, aid, pin, balance):
        try:
            self.cur.execute(
                "UPDATE Savings SET Pin=%s, Balance=%s WHERE AccountID=%s",
                (pin, balance, aid),
            )
            self.commit_close()
            return "✓ Savings account updated."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_savings(self, aid):
        try:
            self.cur.execute("DELETE FROM Savings WHERE AccountID=%s", (aid,))
            self.commit_close()
            return "✓ Savings account deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── DEPOSIT ─────────────────────────────────────────────
    def get_all_deposits(self):
        self.cur.execute(
            """
            SELECT d.*, p.FullName
            FROM Deposit d
            INNER JOIN Person p ON d.SIN = p.SIN
            ORDER BY d.CreatedAt DESC"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def insert_deposit(self, amount, sin, account_id, account_type):
        try:
            self.cur.execute(
                "INSERT INTO Deposit (Amount,SIN,AccountID,AccountType) VALUES (%s,%s,%s,%s)",
                (amount, sin, account_id, account_type),
            )
            # Update balance
            if account_type == "chequing":
                self.cur.execute(
                    "UPDATE Chequing SET Balance=Balance+%s WHERE AccountID=%s",
                    (amount, account_id),
                )
            else:
                self.cur.execute(
                    "UPDATE Savings  SET Balance=Balance+%s WHERE AccountID=%s",
                    (amount, account_id),
                )
            self.commit_close()
            return "✓ Deposit recorded."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_deposit(self, dep_id):
        try:
            self.cur.execute("DELETE FROM Deposit WHERE DepositID=%s", (dep_id,))
            self.commit_close()
            return "✓ Deposit record deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── TRANSFER ────────────────────────────────────────────
    def get_all_transfers(self):
        self.cur.execute(
            """
            SELECT t.*, p.FullName
            FROM Transfer t
            INNER JOIN Person p ON t.SIN = p.SIN
            ORDER BY t.CreatedAt DESC"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def insert_transfer(self, amount, sin, from_id, from_type, to_id, to_type):
        try:
            self.cur.execute(
                """INSERT INTO Transfer (Amount,SIN,FromAccountID,FromAccountType,ToAccountID,ToAccountType)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (amount, sin, from_id, from_type, to_id, to_type),
            )
            # Debit source
            tbl_from = "Chequing" if from_type == "chequing" else "Savings"
            tbl_to = "Chequing" if to_type == "chequing" else "Savings"
            self.cur.execute(
                f"UPDATE {tbl_from} SET Balance=Balance-%s WHERE AccountID=%s",
                (amount, from_id),
            )
            self.cur.execute(
                f"UPDATE {tbl_to}   SET Balance=Balance+%s WHERE AccountID=%s",
                (amount, to_id),
            )
            self.commit_close()
            return "✓ Transfer completed."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_transfer(self, tid):
        try:
            self.cur.execute("DELETE FROM Transfer WHERE TransferID=%s", (tid,))
            self.commit_close()
            return "✓ Transfer record deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── PAY BILLS ───────────────────────────────────────────
    def get_all_paybills(self):
        self.cur.execute(
            """
            SELECT pb.*, p.FullName
            FROM PayBills pb
            INNER JOIN Person p ON pb.SIN = p.SIN
            ORDER BY pb.CreatedAt DESC"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def insert_paybill(self, amount, sin, account_id, account_type, payee_name):
        try:
            self.cur.execute(
                "INSERT INTO PayBills (Amount,SIN,AccountID,AccountType,PayeeName) VALUES (%s,%s,%s,%s,%s)",
                (amount, sin, account_id, account_type, payee_name),
            )
            tbl = "Chequing" if account_type == "chequing" else "Savings"
            self.cur.execute(
                f"UPDATE {tbl} SET Balance=Balance-%s WHERE AccountID=%s",
                (amount, account_id),
            )
            self.commit_close()
            return "✓ Bill payment recorded."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_paybill(self, pbid):
        try:
            self.cur.execute("DELETE FROM PayBills WHERE PayBillID=%s", (pbid,))
            self.commit_close()
            return "✓ Pay bill record deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── CLOSE ACCOUNT ───────────────────────────────────────
    def get_all_closed(self):
        self.cur.execute(
            """
            SELECT ca.*, p.FullName
            FROM CloseAccount ca
            INNER JOIN Person p ON ca.SIN = p.SIN
            ORDER BY ca.ClosedAt DESC"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def close_account(self, sin, account_id, account_type):
        try:
            self.cur.execute(
                "INSERT INTO CloseAccount (SIN,AccountID,AccountType) VALUES (%s,%s,%s)",
                (sin, account_id, account_type),
            )
            tbl = "Chequing" if account_type == "chequing" else "Savings"
            self.cur.execute(f"DELETE FROM {tbl} WHERE AccountID=%s", (account_id,))
            self.commit_close()
            return "✓ Account closed."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── PAYEE ───────────────────────────────────────────────
    def get_all_payees(self):
        self.cur.execute(
            """
            SELECT py.*, p.FullName
            FROM Payee py
            INNER JOIN Person p ON py.SIN = p.SIN
            ORDER BY py.PayeeName"""
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def get_payee(self, pid):
        self.cur.execute("SELECT * FROM Payee WHERE PayeeID=%s", (pid,))
        r = self.cur.fetchone()
        self.close()
        return r

    def insert_payee(self, sin, account_id, account_type, name, number, email):
        try:
            self.cur.execute(
                """INSERT INTO Payee (SIN,AccountID,AccountType,PayeeName,PayeeNumber,PayeeEmail)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (sin, account_id, account_type, name, number, email),
            )
            self.commit_close()
            return "✓ Payee added."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def update_payee(self, pid, name, number, email):
        try:
            self.cur.execute(
                "UPDATE Payee SET PayeeName=%s,PayeeNumber=%s,PayeeEmail=%s WHERE PayeeID=%s",
                (name, number, email, pid),
            )
            self.commit_close()
            return "✓ Payee updated."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    def delete_payee(self, pid):
        try:
            self.cur.execute("DELETE FROM Payee WHERE PayeeID=%s", (pid,))
            self.commit_close()
            return "✓ Payee deleted."
        except Exception as e:
            self.close()
            return f"✗ Error: {e}"

    # ── HELPERS ─────────────────────────────────────────────
    def get_persons_list(self):
        self.cur.execute("SELECT SIN, FullName FROM Person ORDER BY FullName")
        r = self.cur.fetchall()
        self.close()
        return r

    def get_accounts_for_sin(self, sin):
        """Returns all chequing + savings for a given SIN."""
        self.cur.execute(
            "SELECT AccountID,'chequing' AS Type FROM Chequing WHERE SIN=%s "
            "UNION SELECT AccountID,'savings' AS Type FROM Savings WHERE SIN=%s",
            (sin, sin),
        )
        r = self.cur.fetchall()
        self.close()
        return r

    def get_all_accounts_flat(self):
        self.cur.execute(
            "SELECT AccountID,'chequing' AS Type, SIN FROM Chequing "
            "UNION SELECT AccountID,'savings' AS Type, SIN FROM Savings"
        )
        r = self.cur.fetchall()
        self.close()
        return r

    # ── JOIN DASHBOARD ──────────────────────────────────────
    def get_join_summary(self):
        """
        JOIN: Person ⋈ Chequing ⋈ Savings (LEFT JOIN to show all persons)
        Returns each person with their chequing and savings balances.
        """
        self.cur.execute(
            """
            SELECT
                p.SIN,
                p.FullName,
                p.PhoneNumber,
                c.AccountID   AS ChequingID,
                c.Balance     AS ChequingBal,
                s.AccountID   AS SavingsID,
                s.Balance     AS SavingsBal,
                s.InterestRate
            FROM Person p
            LEFT JOIN Chequing c ON p.SIN = c.SIN
            LEFT JOIN Savings  s ON p.SIN = s.SIN
            ORDER BY p.FullName
        """
        )
        r = self.cur.fetchall()
        self.close()
        return r


# ── ROUTES ───────────────────────────────────────────────────


@app.route("/")
def home():
    db = Database()
    summary = db.get_join_summary()
    return render_template("index.html", summary=summary)


# ─ PERSONS ────────────────────────────────────────────────────
@app.route("/persons")
def persons():
    db = Database()
    persons = db.get_all_persons()
    msg = request.args.get("msg", "")
    return render_template("persons.html", persons=persons, msg=msg)


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
    return render_template(
        "account_form.html",
        account=None,
        account_type="chequing",
        persons=persons,
        msg=msg,
    )


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
    return render_template(
        "account_form.html",
        account=account,
        account_type="chequing",
        persons=[],
        msg=msg,
    )


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
    return render_template(
        "account_form.html",
        account=None,
        account_type="savings",
        persons=persons,
        msg=msg,
    )


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
    return render_template(
        "account_form.html",
        account=account,
        account_type="savings",
        persons=[],
        msg=msg,
    )


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
        msg = db.insert_deposit(
            f["amount"], f["sin"], f["account_id"], f["account_type"]
        )
    db = Database()
    all_dep = db.get_all_deposits()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template(
        "deposits.html", deposits=all_dep, persons=persons, accounts=accounts, msg=msg
    )


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
        msg = db.insert_transfer(
            f["amount"],
            f["sin"],
            f["from_id"],
            f["from_type"],
            f["to_id"],
            f["to_type"],
        )
    db = Database()
    all_tr = db.get_all_transfers()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template(
        "transfers.html", transfers=all_tr, persons=persons, accounts=accounts, msg=msg
    )


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
        msg = db.insert_paybill(
            f["amount"], f["sin"], f["account_id"], f["account_type"], f["payee_name"]
        )
    db = Database()
    all_pb = db.get_all_paybills()
    db2 = Database()
    persons = db2.get_persons_list()
    db3 = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template(
        "paybills.html", paybills=all_pb, persons=persons, accounts=accounts, msg=msg
    )


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
    return render_template(
        "close.html", closed=closed, persons=persons, accounts=accounts, msg=msg
    )


# ─ PAYEES ─────────────────────────────────────────────────────
@app.route("/payees")
def payees():
    db = Database()
    payees = db.get_all_payees()
    msg = request.args.get("msg", "")
    return render_template("payees.html", payees=payees, msg=msg)


@app.route("/payees/new", methods=["GET", "POST"])
def payee_new():
    msg = ""
    if request.method == "POST":
        f = request.form
        db = Database()
        msg = db.insert_payee(
            f["sin"],
            f["account_id"],
            f["account_type"],
            f["payee_name"],
            f["payee_number"],
            f["payee_email"],
        )
        if "✓" in msg:
            return redirect(url_for("payees", msg=msg))
    db = Database()
    persons = db.get_persons_list()
    db2 = Database()
    accounts = db2.get_all_accounts_flat()
    return render_template(
        "payee_form.html", payee=None, persons=persons, accounts=accounts, msg=msg
    )


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
    return render_template(
        "payee_form.html", payee=payee, persons=[], accounts=[], msg=msg
    )


@app.route("/payees/delete/<int:pid>")
def payee_delete(pid):
    db = Database()
    msg = db.delete_payee(pid)
    return redirect(url_for("payees", msg=msg))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
