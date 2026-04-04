from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import credentials

app = Flask(__name__, template_folder="templates")

# ── Database ──────────────────────────────────────────────────
class Database:
    def __init__(self):
        self.con = psycopg2.connect(credentials.DB_URL)
        self.cur = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def close(self):
        self.con.close()

    def commit_close(self):
        self.con.commit()
        self.con.close()

    # ── PERSON ──────────────────────────────────────────────
    def get_all_persons(self):
        self.cur.execute('SELECT * FROM person ORDER BY fullname')
        r = self.cur.fetchall(); self.close(); return r

    def get_person(self, sin):
        self.cur.execute('SELECT * FROM person WHERE sin=%s', (sin,))
        r = self.cur.fetchone(); self.close(); return r

    def insert_person(self, sin, name, dob, phone, address):
        try:
            self.cur.execute(
                'INSERT INTO person (sin,fullname,dateofbirth,phonenumber,address) VALUES (%s,%s,%s,%s,%s)',
                (sin, name, dob, phone, address))
            self.cur.execute('INSERT INTO account (sin) VALUES (%s)', (sin,))
            self.commit_close()
            return "✓ Person registered successfully."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_person(self, sin, name, dob, phone, address):
        try:
            self.cur.execute(
                'UPDATE person SET fullname=%s,dateofbirth=%s,phonenumber=%s,address=%s WHERE sin=%s',
                (name, dob, phone, address, sin))
            self.commit_close()
            return "✓ Person updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_person(self, sin):
        try:
            self.cur.execute('DELETE FROM person WHERE sin=%s', (sin,))
            self.commit_close()
            return "✓ Person and linked accounts deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── CHEQUING ────────────────────────────────────────────
    def get_all_chequing(self):
        self.cur.execute("""
            SELECT c.*, p.fullname
            FROM chequing c
            INNER JOIN person p ON c.sin = p.sin
            ORDER BY c.accountid""")
        r = self.cur.fetchall(); self.close(); return r

    def get_chequing(self, aid):
        self.cur.execute('SELECT * FROM chequing WHERE accountid=%s', (aid,))
        r = self.cur.fetchone(); self.close(); return r

    def insert_chequing(self, account_id, pin, sin):
        try:
            self.cur.execute(
                'INSERT INTO chequing (accountid,pin,sin,balance) VALUES (%s,%s,%s,0.00)',
                (account_id, pin, sin))
            self.commit_close()
            return "✓ Chequing account created."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_chequing(self, aid, pin, balance):
        try:
            self.cur.execute(
                'UPDATE chequing SET pin=%s, balance=%s WHERE accountid=%s',
                (pin, balance, aid))
            self.commit_close(); return "✓ Chequing account updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_chequing(self, aid):
        try:
            self.cur.execute('DELETE FROM chequing WHERE accountid=%s', (aid,))
            self.commit_close(); return "✓ Chequing account deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── SAVINGS ─────────────────────────────────────────────
    def get_all_savings(self):
        self.cur.execute("""
            SELECT s.*, p.fullname
            FROM savings s
            INNER JOIN person p ON s.sin = p.sin
            ORDER BY s.accountid""")
        r = self.cur.fetchall(); self.close(); return r

    def get_savings(self, aid):
        self.cur.execute('SELECT * FROM savings WHERE accountid=%s', (aid,))
        r = self.cur.fetchone(); self.close(); return r

    def insert_savings(self, account_id, pin, sin):
        try:
            self.cur.execute(
                'INSERT INTO savings (accountid,pin,interestrate,sin,balance) VALUES (%s,%s,3.00,%s,0.00)',
                (account_id, pin, sin))
            self.commit_close(); return "✓ Savings account created."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_savings(self, aid, pin, balance):
        try:
            self.cur.execute(
                'UPDATE savings SET pin=%s, balance=%s WHERE accountid=%s',
                (pin, balance, aid))
            self.commit_close(); return "✓ Savings account updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_savings(self, aid):
        try:
            self.cur.execute('DELETE FROM savings WHERE accountid=%s', (aid,))
            self.commit_close(); return "✓ Savings account deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── DEPOSIT ─────────────────────────────────────────────
    def get_all_deposits(self):
        self.cur.execute("""
            SELECT d.*, p.fullname
            FROM deposit d
            INNER JOIN person p ON d.sin = p.sin
            ORDER BY d.createdat DESC""")
        r = self.cur.fetchall(); self.close(); return r

    def insert_deposit(self, amount, sin, account_id, account_type):
        try:
            self.cur.execute(
                'INSERT INTO deposit (amount,sin,accountid,accounttype) VALUES (%s,%s,%s,%s)',
                (amount, sin, account_id, account_type))
            if account_type == 'chequing':
                self.cur.execute('UPDATE chequing SET balance=balance+%s WHERE accountid=%s', (amount, account_id))
            else:
                self.cur.execute('UPDATE savings SET balance=balance+%s WHERE accountid=%s', (amount, account_id))
            self.commit_close(); return "✓ Deposit recorded."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_deposit(self, dep_id):
        try:
            self.cur.execute('DELETE FROM deposit WHERE depositid=%s', (dep_id,))
            self.commit_close(); return "✓ Deposit record deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── TRANSFER ────────────────────────────────────────────
    def get_all_transfers(self):
        self.cur.execute("""
            SELECT t.*, p.fullname
            FROM transfer t
            INNER JOIN person p ON t.sin = p.sin
            ORDER BY t.createdat DESC""")
        r = self.cur.fetchall(); self.close(); return r

    def insert_transfer(self, amount, sin, from_id, from_type, to_id, to_type):
        try:
            self.cur.execute(
                """INSERT INTO transfer (amount,sin,fromaccountid,fromaccounttype,toaccountid,toaccounttype)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (amount, sin, from_id, from_type, to_id, to_type))
            tbl_from = 'chequing' if from_type == 'chequing' else 'savings'
            tbl_to   = 'chequing' if to_type   == 'chequing' else 'savings'
            self.cur.execute(f'UPDATE {tbl_from} SET balance=balance-%s WHERE accountid=%s', (amount, from_id))
            self.cur.execute(f'UPDATE {tbl_to}   SET balance=balance+%s WHERE accountid=%s', (amount, to_id))
            self.commit_close(); return "✓ Transfer completed."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_transfer(self, tid):
        try:
            self.cur.execute('DELETE FROM transfer WHERE transferid=%s', (tid,))
            self.commit_close(); return "✓ Transfer record deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── PAY BILLS ───────────────────────────────────────────
    def get_all_paybills(self):
        self.cur.execute("""
            SELECT pb.*, p.fullname
            FROM paybills pb
            INNER JOIN person p ON pb.sin = p.sin
            ORDER BY pb.createdat DESC""")
        r = self.cur.fetchall(); self.close(); return r

    def insert_paybill(self, amount, sin, account_id, account_type, payee_name):
        try:
            self.cur.execute(
                'INSERT INTO paybills (amount,sin,accountid,accounttype,payeename) VALUES (%s,%s,%s,%s,%s)',
                (amount, sin, account_id, account_type, payee_name))
            tbl = 'chequing' if account_type == 'chequing' else 'savings'
            self.cur.execute(f'UPDATE {tbl} SET balance=balance-%s WHERE accountid=%s', (amount, account_id))
            self.commit_close(); return "✓ Bill payment recorded."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_paybill(self, pbid):
        try:
            self.cur.execute('DELETE FROM paybills WHERE paybillid=%s', (pbid,))
            self.commit_close(); return "✓ Pay bill record deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── CLOSE ACCOUNT ───────────────────────────────────────
    def get_all_closed(self):
        self.cur.execute("""
            SELECT ca.*, p.fullname
            FROM closeaccount ca
            INNER JOIN person p ON ca.sin = p.sin
            ORDER BY ca.closedat DESC""")
        r = self.cur.fetchall(); self.close(); return r

    def close_account(self, sin, account_id, account_type):
        try:
            self.cur.execute(
                'INSERT INTO closeaccount (sin,accountid,accounttype) VALUES (%s,%s,%s)',
                (sin, account_id, account_type))
            tbl = 'chequing' if account_type == 'chequing' else 'savings'
            self.cur.execute(f'DELETE FROM {tbl} WHERE accountid=%s', (account_id,))
            self.commit_close(); return "✓ Account closed."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── PAYEE ───────────────────────────────────────────────
    def get_all_payees(self):
        self.cur.execute("""
            SELECT py.*, p.fullname
            FROM payee py
            INNER JOIN person p ON py.sin = p.sin
            ORDER BY py.payeename""")
        r = self.cur.fetchall(); self.close(); return r

    def get_payee(self, pid):
        self.cur.execute('SELECT * FROM payee WHERE payeeid=%s', (pid,))
        r = self.cur.fetchone(); self.close(); return r

    def insert_payee(self, sin, account_id, account_type, name, number, email):
        try:
            self.cur.execute(
                """INSERT INTO payee (sin,accountid,accounttype,payeename,payeenumber,payeeemail)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (sin, account_id, account_type, name, number, email))
            self.commit_close(); return "✓ Payee added."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def update_payee(self, pid, name, number, email):
        try:
            self.cur.execute(
                'UPDATE payee SET payeename=%s,payeenumber=%s,payeeemail=%s WHERE payeeid=%s',
                (name, number, email, pid))
            self.commit_close(); return "✓ Payee updated."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    def delete_payee(self, pid):
        try:
            self.cur.execute('DELETE FROM payee WHERE payeeid=%s', (pid,))
            self.commit_close(); return "✓ Payee deleted."
        except Exception as e:
            self.close(); return f"✗ Error: {e}"

    # ── HELPERS ─────────────────────────────────────────────
    def get_persons_list(self):
        self.cur.execute('SELECT sin, fullname FROM person ORDER BY fullname')
        r = self.cur.fetchall(); self.close(); return r

    def get_all_accounts_flat(self):
        self.cur.execute(
            "SELECT accountid, 'chequing' AS type, sin FROM chequing "
            "UNION SELECT accountid, 'savings' AS type, sin FROM savings")
        r = self.cur.fetchall(); self.close(); return r

    # ── JOIN DASHBOARD ──────────────────────────────────────
    def get_join_summary(self):
        self.cur.execute("""
            SELECT
                p.sin,
                p.fullname,
                p.phonenumber,
                c.accountid   AS chequingid,
                c.balance     AS chequingbal,
                s.accountid   AS savingsid,
                s.balance     AS savingsbal,
                s.interestrate
            FROM person p
            LEFT JOIN chequing c ON p.sin = c.sin
            LEFT JOIN savings  s ON p.sin = s.sin
            ORDER BY p.fullname
        """)
        r = self.cur.fetchall(); self.close(); return r


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
    msg = request.args.get('msg', '')
    return render_template("persons.html", persons=persons, msg=msg)

@app.route("/persons/new", methods=['GET','POST'])
def person_new():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_person(f['sin'], f['name'], f['dob'], f['phone'], f['address'])
        if '✓' in msg:
            return redirect(url_for('persons', msg=msg))
    return render_template("person_form.html", person=None, msg=msg)

@app.route("/persons/edit/<sin>", methods=['GET','POST'])
def person_edit(sin):
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.update_person(sin, f['name'], f['dob'], f['phone'], f['address'])
        if '✓' in msg:
            return redirect(url_for('persons', msg=msg))
    db     = Database()
    person = db.get_person(sin)
    return render_template("person_form.html", person=person, msg=msg)

@app.route("/persons/delete/<sin>")
def person_delete(sin):
    db  = Database()
    msg = db.delete_person(sin)
    return redirect(url_for('persons', msg=msg))

# ─ CHEQUING ───────────────────────────────────────────────────
@app.route("/chequing")
def chequing():
    db       = Database()
    accounts = db.get_all_chequing()
    msg      = request.args.get('msg', '')
    return render_template("chequing.html", accounts=accounts, msg=msg)

@app.route("/chequing/new", methods=['GET','POST'])
def chequing_new():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_chequing(f['account_id'], f['pin'], f['sin'])
        if '✓' in msg:
            return redirect(url_for('chequing', msg=msg))
    db      = Database()
    persons = db.get_persons_list()
    return render_template("account_form.html", account=None, account_type='chequing', persons=persons, msg=msg)

@app.route("/chequing/edit/<aid>", methods=['GET','POST'])
def chequing_edit(aid):
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.update_chequing(aid, f['pin'], f['balance'])
        if '✓' in msg:
            return redirect(url_for('chequing', msg=msg))
    db      = Database()
    account = db.get_chequing(aid)
    return render_template("account_form.html", account=account, account_type='chequing', persons=[], msg=msg)

@app.route("/chequing/delete/<aid>")
def chequing_delete(aid):
    db  = Database()
    msg = db.delete_chequing(aid)
    return redirect(url_for('chequing', msg=msg))

# ─ SAVINGS ────────────────────────────────────────────────────
@app.route("/savings")
def savings():
    db       = Database()
    accounts = db.get_all_savings()
    msg      = request.args.get('msg', '')
    return render_template("savings.html", accounts=accounts, msg=msg)

@app.route("/savings/new", methods=['GET','POST'])
def savings_new():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_savings(f['account_id'], f['pin'], f['sin'])
        if '✓' in msg:
            return redirect(url_for('savings', msg=msg))
    db      = Database()
    persons = db.get_persons_list()
    return render_template("account_form.html", account=None, account_type='savings', persons=persons, msg=msg)

@app.route("/savings/edit/<aid>", methods=['GET','POST'])
def savings_edit(aid):
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.update_savings(aid, f['pin'], f['balance'])
        if '✓' in msg:
            return redirect(url_for('savings', msg=msg))
    db      = Database()
    account = db.get_savings(aid)
    return render_template("account_form.html", account=account, account_type='savings', persons=[], msg=msg)

@app.route("/savings/delete/<aid>")
def savings_delete(aid):
    db  = Database()
    msg = db.delete_savings(aid)
    return redirect(url_for('savings', msg=msg))

# ─ DEPOSIT ────────────────────────────────────────────────────
@app.route("/deposits", methods=['GET','POST'])
def deposits():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_deposit(f['amount'], f['sin'], f['account_id'], f['account_type'])
    db       = Database()
    all_dep  = db.get_all_deposits()
    db2      = Database()
    persons  = db2.get_persons_list()
    db3      = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("deposits.html", deposits=all_dep, persons=persons, accounts=accounts, msg=msg)

@app.route("/deposits/delete/<int:did>")
def deposit_delete(did):
    db  = Database()
    msg = db.delete_deposit(did)
    return redirect(url_for('deposits', msg=msg))

# ─ TRANSFER ───────────────────────────────────────────────────
@app.route("/transfers", methods=['GET','POST'])
def transfers():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_transfer(f['amount'], f['sin'],
                                  f['from_id'], f['from_type'],
                                  f['to_id'],   f['to_type'])
    db       = Database()
    all_tr   = db.get_all_transfers()
    db2      = Database()
    persons  = db2.get_persons_list()
    db3      = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("transfers.html", transfers=all_tr, persons=persons, accounts=accounts, msg=msg)

@app.route("/transfers/delete/<int:tid>")
def transfer_delete(tid):
    db  = Database()
    msg = db.delete_transfer(tid)
    return redirect(url_for('transfers'))

# ─ PAY BILLS ──────────────────────────────────────────────────
@app.route("/paybills", methods=['GET','POST'])
def paybills():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_paybill(f['amount'], f['sin'], f['account_id'], f['account_type'], f['payee_name'])
    db       = Database()
    all_pb   = db.get_all_paybills()
    db2      = Database()
    persons  = db2.get_persons_list()
    db3      = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("paybills.html", paybills=all_pb, persons=persons, accounts=accounts, msg=msg)

@app.route("/paybills/delete/<int:pbid>")
def paybill_delete(pbid):
    db  = Database()
    msg = db.delete_paybill(pbid)
    return redirect(url_for('paybills'))

# ─ CLOSE ACCOUNT ──────────────────────────────────────────────
@app.route("/close", methods=['GET','POST'])
def close_account():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.close_account(f['sin'], f['account_id'], f['account_type'])
    db       = Database()
    closed   = db.get_all_closed()
    db2      = Database()
    persons  = db2.get_persons_list()
    db3      = Database()
    accounts = db3.get_all_accounts_flat()
    return render_template("close.html", closed=closed, persons=persons, accounts=accounts, msg=msg)

# ─ PAYEES ─────────────────────────────────────────────────────
@app.route("/payees")
def payees():
    db     = Database()
    payees = db.get_all_payees()
    msg    = request.args.get('msg', '')
    return render_template("payees.html", payees=payees, msg=msg)

@app.route("/payees/new", methods=['GET','POST'])
def payee_new():
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.insert_payee(f['sin'], f['account_id'], f['account_type'],
                               f['payee_name'], f['payee_number'], f['payee_email'])
        if '✓' in msg:
            return redirect(url_for('payees', msg=msg))
    db       = Database()
    persons  = db.get_persons_list()
    db2      = Database()
    accounts = db2.get_all_accounts_flat()
    return render_template("payee_form.html", payee=None, persons=persons, accounts=accounts, msg=msg)

@app.route("/payees/edit/<int:pid>", methods=['GET','POST'])
def payee_edit(pid):
    msg = ""
    if request.method == 'POST':
        f   = request.form
        db  = Database()
        msg = db.update_payee(pid, f['payee_name'], f['payee_number'], f['payee_email'])
        if '✓' in msg:
            return redirect(url_for('payees', msg=msg))
    db    = Database()
    payee = db.get_payee(pid)
    return render_template("payee_form.html", payee=payee, persons=[], accounts=[], msg=msg)

@app.route("/payees/delete/<int:pid>")
def payee_delete(pid):
    db  = Database()
    msg = db.delete_payee(pid)
    return redirect(url_for('payees', msg=msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
