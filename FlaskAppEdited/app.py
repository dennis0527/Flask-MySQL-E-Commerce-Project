from flask import Flask, render_template, request, session
from flaskext.mysql import MySQL
app = Flask(__name__)
app.secret_key = b'u34n_uq3#!N=13hg14hg'	
mysql = MySQL()
 
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Password305!'
app.config['MYSQL_DATABASE_DB'] = '305database'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

conn = mysql.connect()



@app.route("/", methods=['GET', 'POST'])
def main():
    if 'username' in session:		
        print ("signed in as ", session['username'])		
    else:		
        session['username'] = 'Guest'		
        session['customerID'] = 0		
        session['cartID'] = 0

    if request.method == 'GET':
        cursor = conn.cursor()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID AND I.Quantity > 0"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('index.html', items = result, customerid = 0, username = session['username'])

@app.route("/buy", methods=['POST'])
def buy():
    if request.method == 'POST':
        if session['cartID'] == 0:
            return render_template('buy.html', notSignedIn = True)
        _articleid = request.form['inputAID']
        _customerid = session['customerID']
        if _articleid and _customerid:
            print("values received: " + _articleid)
        cursor = conn.cursor()
        sql = "SELECT A.ArticleName FROM ARTICLE A WHERE A.ArticleID = " + _articleid
        cursor.execute(sql)
        bought = cursor.fetchall()
        sqlMax = "SELECT MAX(ShoppingCartID) FROM ShoppingCart"
        cursor.execute(sqlMax)
        maxShoppingCartId = cursor.fetchall()[0][0]
        #print(maxShoppingCartId)
        sqlFetchSC = "SELECT ShoppingCartID FROM SHOPPINGCART WHERE CustomerId = " + str(_customerid) + " AND Ordered = 0"
        cursor.execute(sqlFetchSC)
        result = cursor.fetchall()
        if len(result) == 0:
            maxShoppingCartId+=1
            sqlPrice = "SELECT PRICE FROM Article WHERE ArticleId = " + _articleid
            cursor.execute(sqlPrice)
            price = cursor.fetchall()[0][0]
            print(str(price) + '\n')
            sqlInsert = "INSERT INTO ShoppingCart(ShoppingCartID, Ordered, TotalPrice, PricePerItem, QuantityOfItems, ItemsPurchased, CustomerId) VALUES (" + str(maxShoppingCartId) + ',' + '0' +',' + str(price) + ',' + '0' + ',' + '1' + ',' + '0' + ',' + str(_customerid) + ")"
            cursor.execute(sqlInsert)
            sqlGetQuantSCI = "SELECT Quantity FROM ShoppingCartItem WHERE ShoppingCartId = " + str(maxShoppingCartId) + " AND ArticleId = " + _articleid
            cursor.execute(sqlGetQuantSCI)
            if len(cursor.fetchall()) == 0:
                sqlInsertShoppingCartItem = "INSERT INTO ShoppingCartItem(ShoppingCartId, ArticleId, Quantity) VALUES (" + str(maxShoppingCartId) + ', ' + _articleid + ", 1)"
                cursor.execute(sqlInsertShoppingCartItem)
            else:
                quantSCI = cursor.fetchall()[0][0]
                sqlUpdateShoppingCartItem = "UPDATE ShoppingCartItem SET Quantity = " +quantSCI
                cursor.execute(sqlUpdateShoppingCartItem) 

            sqlInvGet = "SELECT Quantity FROM Inventory WHERE ArticleID = " + _articleid
            cursor.execute(sqlInvGet)
            quant = cursor.fetchall()
            quantValue = quant[0][0] - 1
            sqlInv = "UPDATE Inventory SET Quantity = " + str(quantValue) + " WHERE ArticleID = " + str(_articleid)
            cursor.execute(sqlInv)

            conn.commit()
        else:
            sqlShoppingCartId = "SELECT ShoppingCartID FROM ShoppingCart WHERE CustomerId = " + str(_customerid) +  " AND Ordered = 0"
            cursor.execute(sqlShoppingCartId)
            shoppingCartId = cursor.fetchall()[0][0]
            print(shoppingCartId)
            print('Shopping cart id^\n\n\n')
            sqlPrice = "SELECT PRICE FROM Article WHERE ArticleId = " + _articleid
            cursor.execute(sqlPrice)
            price = cursor.fetchall()[0][0]
            sqlQuantityofItems = "SELECT QuantityOfItems FROM ShoppingCart WHERE Ordered = 0 AND CustomerId = " + str(_customerid)
            cursor.execute(sqlQuantityofItems)
            quantity = cursor.fetchall()[0][0]
            quantity += 1
            sqlPriceofItems = "SELECT TotalPrice FROM ShoppingCart WHERE Ordered = 0 AND CustomerId = " + str(_customerid)
            cursor.execute(sqlPriceofItems)
            totalPrice = cursor.fetchall()[0][0]
            totalPrice += price
            sqlUpdate ="UPDATE ShoppingCart SET QuantityOfItems= " + str(quantity) + ", TotalPrice=" + str(totalPrice) + " WHERE (CustomerId =" + str(_customerid) + " AND Ordered = 0)"
            cursor.execute(sqlUpdate)
            print('SHOPPING CART ID ' + str(shoppingCartId) + "AND ARTICLE ID " + str(_articleid) + '\n\n\n')
            sqlGetQuantSCI = "SELECT Quantity FROM ShoppingCartItem WHERE ShoppingCartId = " + str(shoppingCartId) + " AND ArticleId = " + _articleid
            cursor.execute(sqlGetQuantSCI)
            quantSCI = cursor.fetchall()
            if len(quantSCI) == 0:
                sqlInsertShoppingCartItem = "INSERT INTO ShoppingCartItem(ShoppingCartId, ArticleId, Quantity) VALUES (" + str(shoppingCartId) + ', ' + _articleid + ", 1)"
                cursor.execute(sqlInsertShoppingCartItem)
            else:
                newQuant = quantSCI[0][0] + 1
                sqlUpdateShoppingCartItem = "UPDATE ShoppingCartItem SET Quantity = " +str(newQuant) + " WHERE ArticleID = " + str(_articleid) + " AND ShoppingCartID = " + str(shoppingCartId)
                cursor.execute(sqlUpdateShoppingCartItem)
            sqlInvGet = "SELECT Quantity FROM Inventory WHERE ArticleID = " + _articleid
            cursor.execute(sqlInvGet)
            quant = cursor.fetchall()
            quantValue = quant[0][0] - 1
            sqlInv = "UPDATE Inventory SET Quantity = " + str(quantValue) + " WHERE ArticleID = " + str(_articleid)
            cursor.execute(sqlInv)
            conn.commit()
        return render_template('buy.html', items = bought, customerid = str(_customerid), username = session['username'])

@app.route("/signup", methods=['GET', 'POST'])
def signup():
        if request.method == 'POST':
            _customerid = request.form['cidsignup']
            _firstname = request.form['firstname']
            _phonenumber = request.form['phonenumber']
            _lastname = request.form['lastname']
            _emailaddress = request.form['emailaddress']
            _address = request.form['address']
            cursor = conn.cursor()
           
            string = "\'" + _firstname + "\',\'" + _lastname + '\',\'' + _phonenumber + "\'," + _customerid  + ",\'" + _emailaddress + '\',\'' + _address + "\'"
            sql = "INSERT INTO CUSTOMER(FirstName, LastName, PhoneNumber, CustomerID, EmailID, Address) VALUES(" + string + ")"
            try:
                cursor.execute(sql)
            except Exception as err:
                print("error happened")
            if cursor.rowcount == 0:
                print("row count zero")
                return render_template('signup.html', existingCustomer=True, nonexistingCustomer=False, username = session['username'])
            conn.commit()
            return render_template('signup.html', existingCustomer=False, nonexistingCustomer=True, username = session['username'])
        elif request.method == 'GET':
            return render_template('signup.html', existingCustomer=False, nonexistingCustomer=False, username = session['username'])

    #Added a guest sign in and log out		
@app.route("/signin", methods=['GET', 'POST'])		
def signin():		
    if request.method == 'POST':		
        _customerid = request.form['cidsignin']		
        _emailaddress = request.form['emailaddress']		
        cursor = conn.cursor()		
        print(_customerid)
        print(_emailaddress)
        sql = "SELECT * FROM CUSTOMER C WHERE C.CustomerID = " + str(_customerid) + " AND C.EmailID	= '" + str(_emailaddress) + "'"
        try:		
            cursor.execute(sql)		
            user = cursor.fetchone()		
        except Exception as err:		
            print("Customer ID Doesnt Exist")
            print(err)
        try :
            session['username'] = user[0]		
            session['customerID'] = user[3]		
        except Exception as err:
            print("Customer ID Doesnt Exist")
            return render_template("signin.html", username = "nouser", failed = True, succeeded = False)
        session['loggedIn'] = 'true'	
        sqlFetchSC = "SELECT ShoppingCartID FROM SHOPPINGCART WHERE CustomerId = " + str(_customerid) + " AND Ordered = 0"
        cursor.execute(sqlFetchSC)
        result = cursor.fetchall()
        if len(result) == 0:
            session['cartID'] =	-1
            #if negative, display empty cart, customer does not have cart
        else:
            session['cartID'] = result[0][0]
        print("New cart ID is : ", session['cartID'])		
        return render_template('signin.html', user = user, username = session['username'], failed = False, succeeded = True)		
    return render_template('signin.html', failed = False, succeeded=False)		
@app.route("/logout")		
def logout():		
    session.clear		
    session['username'] = 'Guest'		
    session['customerID'] = 0	
    return main()
    

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'GET':
        cursor = conn.cursor()
        sqlCartID = "SELECT ShoppingCartID FROM ShoppingCart WHERE Ordered = 0 AND CustomerID = " + str(session['customerID'])
        cursor.execute(sqlCartID)
        cartID = cursor.fetchall()
        if len(cartID) != 0:
            session['cartID'] = cartID[0][0]
        sql = "SELECT TotalPrice FROM ShoppingCart WHERE CustomerID = " + str(session['customerID']) + " AND Ordered = 0"
        cursor.execute(sql)
        total = cursor.fetchall()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Price, C.Quantity FROM Article A, ShoppingCartItem C, ShoppingCart S WHERE S.CustomerID = " + str(session['customerID']) + " AND C.ShoppingCartID = S.ShoppingCartID AND C.ArticleID = A.ArticleID AND S.Ordered = 0"
        cursor.execute(sql)
        items = cursor.fetchall()
        if len(items) == 0:
            return render_template("cart.html", exists = False)
        return render_template ('cart.html', exists = True, items = items, total = total, username = session['username'])
    else:
        cursor = conn.cursor()
        _articleid = request.form['inputAID']
        sql = "SELECT Quantity FROM ShoppingCartItem WHERE ArticleID = " + str(_articleid)+ " AND ShoppingCartId = " + str(session['cartID'])
        cursor.execute(sql)
        quantity = cursor.fetchall()
        quantValue = quantity[0][0]
        quantValue = quantValue - 1
        if quantValue == 0:
            sqlDel = 'DELETE FROM ShoppingCartItem WHERE ArticleID = ' +  str(_articleid) + " AND ShoppingCartId = " + str(session['cartID'])
            cursor.execute(sqlDel)
        else: 
            sqlUpdate = "UPDATE ShoppingCartItem SET Quantity = " +  str(quantValue) + " WHERE ArticleID = " +  str(_articleid) + " AND ShoppingCartId = " + str(session['cartID'])
            cursor.execute(sqlUpdate)
        sqlInvGetQuant = "SELECT Quantity FROM Inventory WHERE ArticleID = " + str(_articleid)
        cursor.execute(sqlInvGetQuant)
        quantValueInvCursor = cursor.fetchall()
        quantValueInv = quantValueInvCursor[0][0]
        quantValueInv += 1 
        sqlUpdate = "UPDATE Inventory SET Quantity = " + str(quantValueInv) + " WHERE ArticleID = " +  str(_articleid)
        cursor.execute(sqlUpdate)
        sqlGetPrice = "SELECT Price FROM Article WHERE ArticleID = " + str(_articleid)
        cursor.execute(sqlGetPrice)
        price = cursor.fetchall()
        sqlPriceofItems = "SELECT TotalPrice FROM ShoppingCart WHERE Ordered = 0 AND CustomerId = " + str(session['customerID'])
        cursor.execute(sqlPriceofItems)
        totalPrice = cursor.fetchall()[0][0]
        totalPrice -= price[0][0]
        sqlUpdate ="UPDATE ShoppingCart SET TotalPrice=" + str(totalPrice) + " WHERE (CustomerId =" + str(session['customerID']) + " AND Ordered = 0)"
        cursor.execute(sqlUpdate)

        conn.commit()


        sqlCartID = "SELECT ShoppingCartID FROM ShoppingCart WHERE Ordered = 0 AND CustomerID = " + str(session['customerID'])
        cursor.execute(sqlCartID)
        cartID = cursor.fetchall()
        if len(cartID) != 0:
            session['cartID'] = cartID[0][0]
        sql = "SELECT TotalPrice FROM ShoppingCart WHERE CustomerID = " + str(session['customerID']) + " AND Ordered = 0"
        cursor.execute(sql)
        total = cursor.fetchall()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Price, C.Quantity FROM Article A, ShoppingCartItem C, ShoppingCart S WHERE S.CustomerID = " + str(session['customerID']) + " AND C.ShoppingCartID = S.ShoppingCartID AND C.ArticleID = A.ArticleID AND S.Ordered = 0"
        cursor.execute(sql)
        items = cursor.fetchall()
        if len(items) == 0:
            return render_template("cart.html", exists = False)
        sqlName = "SELECT ArticleName FROM Article WHERE ArticleID = " + str(_articleid)
        cursor.execute(sqlName)
        return render_template ('cart.html', exists = True, items = items, total = total, username = session['username'], removed = True, name = cursor.fetchall()[0][0])


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        cursor = conn.cursor()
        sql = "SELECT CardNumber FROM Payment WHERE CardNumber = " + str(request.form['CardNumber'])
        cursor.execute(sql)
        card = cursor.fetchall()
        if len(card) == 0: 
            sql = "INSERT INTO PAYMENT(PaymentType, CardExpiryDate, CardNumber, CustomerID) VALUES(" + "'" + str(request.form['PaymentType']) + "', '" + str(request.form['CardExpiryDate']) + "', '" + str(request.form['CardNumber']) + "'," + str(session['customerID']) + ")"
            cursor.execute(sql)
        if request.form['ShipmentType'] == "Economy":
            shipmentCost = 2.99
        elif request.form['ShipmentType'] == "Express":
            shipmentCost = 5.99
        else:
            shipmentCost = 14.99
        sql = "INSERT INTO DELIVERY(ShipmentDetails, ShipmentID, ShipmentType, ShipmentCost, CustomerID) VALUES('Shipped by FedEx', " + str(session['cartID']) + ", '" + str(request.form['ShipmentType']) + "', " + str(shipmentCost) + ", " + str(session['customerID']) + ")"
        cursor.execute(sql)
        #after clearing cart, set session['cartID'] to something else (maybe, ordered=1 should take care of it)
        sql = "UPDATE ShoppingCart SET Ordered = 1 WHERE ShoppingCartId = " + str(session['cartID'])
        cursor.execute(sql)
        conn.commit()
        session['cartID'] = -1
        return render_template('checkout.html', checkedOut = True)
    else:
        return render_template('checkout.html', checkedOut = False)

#Admin stuff
@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        cursor = conn.cursor()
        logging = request.form['EmployeeID']
        sql = "SELECT EmployeeID FROM Employee WHERE EmployeeID = " + logging
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) == 0:
            return render_template('adminLogin.html', failed = True, username = session['username'])
        else:
            return render_template('adminLogin.html', logged = True, username = session['username'])
    else:
        return render_template('adminLogin.html',  username = session['username'])

@app.route('/admin')
def admin():
    cursor = conn.cursor()
    sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
    cursor.execute(sql)
    result = cursor.fetchall()
    return render_template('admin.html', items = result, username = session['username'])

@app.route('/adminAdd', methods=['GET', 'POST'])
def adminAdd():
    if request.method == 'POST':
        cursor = conn.cursor()
        adding = request.form['ArticleID']
        sql = "SELECT ArticleID FROM Inventory WHERE ArticleID = " + adding
        cursor.execute(sql)
        result = cursor.fetchall()
        
        #if there aren't any existing articles with ID adding
        if len(result) == 0:

            #insert into article table
            sql = "INSERT INTO Article (ArticleID, Seller, Category, Price, ArticleName) VALUES(" + adding + ", '" + request.form['Seller'] + "', '" + request.form['Category'] + "', " + request.form['Price'] + ", '" + request.form['ArticleName'] + "')"
            cursor.execute(sql)
            conn.commit()
            #insert into inventory table
            ## single quotes around string attributes appened, not sure if single quotes in double quotes will be okay
            sql = "INSERT INTO Inventory (ArticleID, Seller, Quantity, Price) VALUES(" + adding + ", '" + request.form['Seller'] + "', " + request.form['Quantity'] + ", " + request.form['Price'] + ")"
            cursor.execute(sql)
            conn.commit()

            

            #insert into category table if necessary
            if request.form['Category'] != '':
                #additional attributes if categorized (will include later in html)
                if request.form['Category'] == 'Clothing':
                    sql = "INSERT INTO Clothing (ArticleID, Color, Size) VALUES(" + adding + ", 'Red', 'Medium')"
                    cursor.execute(sql)
                    conn.commit()
                elif request.form['Category'] == 'Furniture':
                    sql = "INSERT INTO Furniture (ArticleID, Color) VALUES(" + adding + ", 'Black')"
                    cursor.execute(sql)
                    conn.commit()
                elif request.form['Category'] == 'Electronics':
                    sql = "INSERT INTO Electronics (ArticleID, ProductYear) VALUES(" + adding + ", '2018')"
                    cursor.execute(sql)
                    conn.commit()
        else:
            #update article in inventory table
            sql = "UPDATE Inventory SET Seller = '" + request.form['Seller'] + "', Quantity = " + request.form['Quantity'] + ", Price = "+ request.form['Price'] + " WHERE ArticleID = " + adding
            cursor.execute(sql)
            conn.commit()
            
            #update article in article table
            sql = "UPDATE Article SET Seller = '" + request.form['Seller'] + "', Category = '" + request.form['Category'] + "', Price = " + request.form['Price'] + ", ArticleName = '" + request.form['ArticleName'] + "' WHERE ArticleID = " + adding
            cursor.execute(sql)
            conn.commit()
            
            #Update the articles in the category tables?
            
        updater = request.form['ArticleName']
        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('adminAdd.html', items = result, updated = True, updateName = updater, username = session['username'])
    else:
        cursor = conn.cursor()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('adminAdd.html', items = result, username = session['username'])


@app.route('/adminRemove', methods=['GET', 'POST'])
def adminRemove():
    if request.method == 'POST':
        cursor = conn.cursor()
        removing = request.form['ArticleID']
        sql = "UPDATE Inventory SET Quantity = 0 WHERE ArticleID = " + removing
        cursor.execute(sql)
        conn.commit()
        
        sql = "SELECT ArticleName FROM Article WHERE ArticleID = " + removing
        cursor.execute(sql)
        removedName = cursor.fetchall()

        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('adminRemove.html', items = result, removed = True, removeName = removedName, username = session['username'])
    else:
        cursor = conn.cursor()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('adminRemove.html', items = result, username = session['username'])
##review below
@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        cursor = conn.cursor()
        sql = "SELECT CustomerID, Seller, Rating, DetailedReview FROM Reviews WHERE ArticleID = " + request.form['ArticleID']
        cursor.execute(sql)
        result = cursor.fetchall()
        
        sql = "SELECT ArticleName FROM Article WHERE ArticleID = " + request.form['ArticleID']
        cursor.execute(sql)
        reviewName = cursor.fetchall()
        return render_template('review.html', items = result, reviewName = reviewName, reviewed = True)
        
    else:
        cursor = conn.cursor()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('review.html', items = result, reviewed = False)

@app.route('/reviewAdd', methods=['GET', 'POST'])
def reviewAdd():
    if request.method == 'POST':
        cursor = conn.cursor()
        sql = "SELECT Seller FROM Article WHERE ArticleID = " + request.form['ArticleID']
        cursor.execute(sql)
        name = cursor.fetchall()
        #NAME MIGHT NEED A SELECTING LIKE name[0][0]
        # DUMMY 0 FOR CUSTOMERID, REPLACE WITH SESSION STUFF LATER
        print(request.form['detailedReview'])
        print(request.form['Rating'])
        sql = "INSERT INTO Reviews (DetailedReview, Rating, Seller, CustomerID, ArticleID) VALUES ('" + (str(request.form['detailedReview'])).replace('"', '').replace("'", '') + "', " + request.form['Rating'] + ", '" + str(name[0][0]) + "', " + str(session["customerID"]) + ", " + request.form['ArticleID'] + ")"
        cursor.execute(sql)
        conn.commit()
        return render_template('reviewAdd.html', reviewName = name, reviewAdded = True)
    
    else:
        cursor = conn.cursor()
        sql = "SELECT A.ArticleID, A.ArticleName, A.Seller, A.Category, A.Price, I.Quantity FROM ARTICLE A, Inventory I WHERE A.ArticleID = I.ArticleID"
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template('reviewAdd.html', items = result, reviewAdded = False)



#keep this at the bottom
if __name__ == "__main__":
    app.run()
