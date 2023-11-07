## Run the following command when connecting with the server in AWS
1. cd /var/www/onenairapay
2. source env/bin/activate
3. sudo service apache2 restart


<!-- getting to the server -->
<!-- to see hidden files -->
ls -a

cd /var/www


<!-- server user name and password for pulling from gits -->
## username: afripoint
## password: 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

## SCOPE OF THIS PROJECT
- The use of QRcode - phone to phone
This will be the only mode of payment for stage 1 of development and launch phase.


<!-- SCOPE and work flow -->

______payment flow______

1. load from your phone
2. has a qrcode and make payment through qrcode
3. load from your bank

_____payment gateway_____
- When a user wants to fund his/her wallet from their bank acccount
- When a user wants to withdraw from their wallet into their bank account


_____payment device - tablet_____
the application will be installed in a device which could be a tablet or a small device



<!-- CREATING DATABASE IN THE SAVER - STEPS -->

sudo -u postgres psql

CREATE DATABASE one_naira_db;

CREATE USER onenairadatabaseuser WITH PASSWORD 'WX3ab3Xnfus4k9ab3Xnfab3Xnf';
ALTER ROLE onenairadatabaseuser SET client_encoding TO 'utf8';
ALTER ROLE onenairadatabaseuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE onenairadatabaseuser SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE one_naira_db TO onenairadatabaseuser;

\q to quite the saver


CREATING TOKEN MANUALLY
python manage.py drf_create_token +2347038320362
http http://127.0.0.1:8000/dashboard/users/ 'Authorization: Token 54204909640b7815a556967286fa92b4ab55d2b81'

NB: ensure you have hhtpie installed


POST REQUEST USING HTTPIE
http POST http://localhost:8000/transactions/ \
    payee_wallet_address="7038320362" \
    description="paid for transport to owerri" \
    amount=150 \
    Authorization:"Token <your_token>"


payment 
http POST https://onenairapay.com/transactions/ \
    Content-Type:application/json \
    payee_wallet_address="8122821939" \
    description="paid for data" \
    amount=1000 \
    Authorization:"Token 756de0c1003013755f41a129dcffd142f18c4771"


https://onenairapay.com/deposit/

http POST https://onenairapay.com/deposits/ \
    amount=20000 \
    Authorization:"Token 756de0c1003013755f41a129dcffd142f18c4771"

http POST https://onenairapay.com/auth/change_password/ \
    current_password="flower123456" \
    Authorization:"Token 756de0c1003013755f41a129dcffd142f18c4771"


work:
optimization and error handling and testing. 
- Currently I have optimize and handled the necessary errors that might occure when a user is trying to register and log in and maybe there is a problem with the server/network.

- so basically what I am doing is optimizing the app and where there are necessary refactoring, I will make neccessary refactoring.

- from the registration and login journey, I will move to payments pending when we start the mobile implementation.




<!-- Weekly review meeting meeeting -->

1. I worked on one naira app: I added a field: the gender of the user that's on the design but not on the endpoints
2. With the help of Kelly, the application database was reset
3. I rounded of the authentication for kinetic application after adding some other fields as instructed by Abigail and now currently working prrofile management where user can view that profile, so partial updating on their profile.

4. As at yesterday Toby called my attention to something with respect to user profile on OneNaira which I am also currently working on. 

Once I am done with this, then I will start consuming the Chinese API those specifically tailored to our MVP and create an endpoint from there. 

