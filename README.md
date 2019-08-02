
# CatalogApp
This is a Catalog App with Google authentication.

## Environment

python 2.7

### - Install python requirements

Type `$ pip install -r requirements.txt`

### - Google API

Type `$ export GOOGLE_CLIENT_ID = your client ID`
Type `$ export GOOGLE_CLIENT_SECRET = your client SECRET`

You can use as variables on views.py too.
### Populate DB
To populate database for example.

Type `$ python populate.py`

## Run CatalogApp

Type **`$ python views.py`** to run the Flask web server. In your browser visit **https://127.0.0.1:5000** to view the CatalogApp.  
You should be able to view all categories and itens. 

To add, edit and delete categories and associated itens you need to login with Google authentication.

### API Json

Now type **https://127.0.0.1:5000/categories** on your browser to view all categories in json format.

Now type **https://127.0.0.1:5000/itens** on your browser to view all itens in json format.
