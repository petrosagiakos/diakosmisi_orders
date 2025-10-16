from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory
from flask_session import Session
import psycopg2
import db
from datetime import datetime
import os
app = Flask(__name__)

def add_customer():
    conn = db.connect_db()
    cur = conn.cursor()
    name = request.form.get("name")
    email = request.form.get("email")
    phone1 = request.form.get("phone1")
    phone2 = request.form.get("phone2")
    address = request.form.get("address")
    afm = request.form.get("afm")

    cur.execute("INSERT INTO Customers (name, email, phone1, phone2, address, afm) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, email, phone1, phone2, address, afm))
    conn.commit()   
    cur.close()
    conn.close()
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/customers/add",methods=["GET", "POST"])
def add_customers():
    if request.method == "POST":
        add_customer()

        # Redirect to customers list after adding
        return redirect(url_for("customers"))
@app.route("/customers",methods=["GET", "POST"])
def customers():
    query = "SELECT * FROM Customers WHERE 1=1"
    params = []

    if request.method == "POST":
        nm = request.form.get("nm", "").strip()
        if nm:
            query += " AND name LIKE %s"
            params.append(f"%{nm}%")

        ph = request.form.get("ph", "").strip()
        if ph:
            query += " AND phone1 LIKE %s"
            params.append(f"%{ph}%")

    query += " ORDER BY id"

    conn = db.connect_db()
    cur = conn.cursor()
    cur.execute(query, params) 
    customers = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("customers.html", customers=customers)

@app.route("/customers/edit/<int:id>", methods=["POST"])
def edit_customers(id):
    if request.method == "POST":
        conn = db.connect_db()
        cur = conn.cursor()

        name = request.form.get("name")
        email = request.form.get("email")
        phone1 = request.form.get("phone1")
        phone2 = request.form.get("phone2")
        address = request.form.get("address")
        afm = request.form.get("afm")

        cur.execute("UPDATE Customers SET name=%s, email=%s, phone1=%s, phone2=%s, address=%s, afm=%s WHERE id=%s",
            (name, email, phone1, phone2, address, afm,id))
        conn.commit()   
        cur.close()
        conn.close()

        # Redirect to customers list after editing
        return redirect(url_for("customers"))
@app.route("/customers/delete/<int:id>", methods=["POST"])
def delete_customers(id):
    if request.method == "POST":
        conn = db.connect_db()
        cur = conn.cursor()

        

        cur.execute(" DELETE FROM Customers WHERE id=%s",
            (id,))
        conn.commit()   
        cur.close()
        conn.close()

        # Redirect to customers list after deleting
        return redirect(url_for("customers"))  
@app.route("/orders", methods=["GET","POST"])
def orders():
    query = """
    SELECT 
        o.id,
        o.dt,
        c.name,
        COALESCE(SUM(r.quantity * r.value), 0) AS total_value,
        COALESCE(SUM(r.quantity * r.value), 0) - o.paid AS balance,
        after_sale
    FROM Orders o
    JOIN Customers c ON o.cust_id = c.id
    LEFT JOIN OrderRows r ON o.id = r.order_id
    WHERE 1=1
    """
    gb="""
    GROUP BY o.id, o.dt, c.name, o.paid
    """
    if request.method=="POST":
        id=request.form.get('id')
        name=request.form.get('name')
        if id:
            query+=" AND o.id="+str(id)
        if name:
            query+=" AND c.name like '%"+str(name)+"%' "
    conn = db.connect_db()
    cur = conn.cursor()
    query+=gb
    cur.execute(query)
    orders = cur.fetchall()
    cur.execute("SELECT order_id, is_ordered ,id FROM Orderrows")
    order_rows=cur.fetchall()
    ordered_list=dict()
    
    for o in orders:
        ordered_list[o[0]]=1 #initializing the dictionary
    for r in order_rows:
        if r[1]==0:
            ordered_list[r[0]]=0
    
    row_ord=[]
    for x in ordered_list:
        row_ord.append(ordered_list[x])
    final_orders=[]
    for o in range(len(orders)):
        temp=list(orders[o])
        temp.append(row_ord[o])
        final_orders.append(tuple(temp))
    cur.close()
    conn.close()
    return render_template("orders.html", orders=final_orders)

@app.route("/add_order",methods=["GET", "POST"])
def add_orders():
    if request.method == "POST":
        conn = db.connect_db()
        cur = conn.cursor()
        cid = request.form.get("customer")
        notes = request.form.get("notes")
        date = request.form.get("date")
        if not date:
            date=datetime.today().strftime('%d/%m/%Y')
        paid = request.form.get("paid")
        
        if not paid:
            paid=0
        afterSales=request.form.get("afterSales")
        if not afterSales:
            afterSales=0
        visa_cash = request.form.get("visa_cash")

        cur.execute("INSERT INTO orders (dt, paid, visa_cash, notes, cust_id, after_sale) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (date,paid,visa_cash,notes,cid,afterSales))
        order_id = cur.fetchone()[0] 
        descr_list = request.form.getlist("descr[]")
        qty_list = request.form.getlist("qty[]")
        value_list = request.form.getlist("value[]")
        is_ordered= request.form.getlist("is_ordered[]")
      
        for descr, qty, value, io in zip(descr_list, qty_list, value_list, is_ordered):
            if descr:
                cur.execute(
                    "INSERT INTO OrderRows (descr, quantity, is_ordered, value, order_id) VALUES (%s, %s, %s,%s, %s)",
                    (descr, float(qty), int(io), float(value), order_id)
                )
        conn.commit()
        cur.close()
        conn.close()

        # Redirect to customers list after adding
        return redirect(url_for("orders"))
    conn = db.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Customers ORDER BY name")
    customers = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("add_order.html", customers=customers)
@app.route("/add_order/add",methods=["GET", "POST"])
def add_order_customers():
    if request.method == "POST":
        add_customer()

        # Redirect to customers list after adding
        return redirect(url_for("add_orders"))
@app.route("/edit_order/<int:id>", methods=["GET","POST"])
def edit_order(id):
    print("Received form:", request.form, flush=True)
    if request.method == "POST":
        conn = db.connect_db()
        cur = conn.cursor()
        cid = request.form.get("customer")
        notes = request.form.get("notes")
        date = request.form.get("date")
        paid = request.form.get("paid")
        if not paid:
            paid=0
        afterSales=request.form.get("afterSales")
        if not afterSales:
            afterSales=0
        visa_cash = request.form.get("visa_cash")

        cur.execute("UPDATE orders SET dt=%s, paid=%s, visa_cash=%s, notes=%s, cust_id=%s, after_sale=%s WHERE id=%s RETURNING id",
            (date,paid,visa_cash,notes,cid,afterSales,id))
        order_id = cur.fetchone()[0] 
        row_ids = request.form.getlist("row_id[]")
        descr_list = request.form.getlist("descr[]")
        print(len(descr_list))
        qty_list = request.form.getlist("qty[]")
        value_list = request.form.getlist("value[]")
        is_ordered = request.form.getlist("is_ordered[]")
        print(len(is_ordered))
        cur.execute("SELECT id FROM OrderRows WHERE order_id=%s", (order_id,))
        existing_ids = {str(r[0]) for r in cur.fetchall()}
        for row_id, descr, qty, value, io in zip(row_ids, descr_list, qty_list, value_list, is_ordered):
            if not descr:
                continue
            if row_id:  
                print("Row to DB:", descr, qty, value, io, row_id, flush=True)
                cur.execute(
                    "UPDATE OrderRows SET descr=%s, quantity=%s, is_ordered=%s, value=%s WHERE id=%s",
                    (descr, float(qty), int(io), float(value), row_id)
                )
                existing_ids.discard(row_id)
            else:
                cur.execute(
                    "INSERT INTO OrderRows (descr, quantity, is_ordered, value, order_id) VALUES (%s, %s, %s, %s, %s)",
                    (descr, float(qty), int(io), float(value), order_id)
                )
        for row_id in existing_ids:
            cur.execute("DELETE FROM OrderRows WHERE id=%s", (row_id,))
        conn.commit()
        cur.close()
        conn.close()

        # Redirect to customers list after adding
        return redirect(url_for("orders"))
    conn = db.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Customers ORDER BY name")
    customers = cur.fetchall()
    cur.execute("SELECT * FROM orders WHERE id=%s",(id,))
    order=cur.fetchone()
    cur.execute("SELECT * FROM OrderRows WHERE order_id=%s",(id,))
    rows=cur.fetchall()
    cur.execute("SELECT * FROM customers c JOIN orders o ON o.cust_id=c.id WHERE o.id=%s",(id,))
    cust=cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_order.html", customers=customers,cust=cust,order=order,rows=rows)
@app.route("/delete_order/<int:id>", methods=["POST"])
def delete_order(id):
    if request.method == "POST":
        conn = db.connect_db()
        cur = conn.cursor()

        cur.execute(" DELETE FROM OrderRows WHERE order_id=%s",
            (id,))

        cur.execute(" DELETE FROM Orders WHERE id=%s",
            (id,))
        conn.commit()   
        cur.close()
        conn.close()

        # Redirect to customers list after deleting
        return redirect(url_for("orders"))  
@app.route("/print_order/<int:id>")
def print_order(id):
    conn = db.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=%s", (id,))
    order = cur.fetchone()
    cur.execute("SELECT * FROM customers c JOIN orders o ON c.id=o.cust_id WHERE o.id=%s", (id,))
    customer = cur.fetchone()
    cur.execute("SELECT * FROM OrderRows WHERE order_id=%s", (id,))
    rows = cur.fetchall()
    total = sum(r[1] * r[4] for r in rows)
    balance = total - order[3]
    cur.close()
    conn.close()
    return render_template("print_order.html", order=order, rows=rows, customer=customer,balance=balance,total=total)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)