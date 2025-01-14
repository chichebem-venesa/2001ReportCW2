import pathlib
import connexion
import pyodbc
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import logging
logging.basicConfig(level=logging.DEBUG)


basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.App(__name__, specification_dir=basedir)

app = connex_app.app
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc:///?odbc_connect="
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=dist-6-505.uopnet.plymouth.ac.uk;"
    "DATABASE=COMP2001_COnyenezi;"
    "UID=COnyenezi;"
    "PWD=KcfP142*;"
     "TrustServerCertificate=yes;"
     "Encrypt=yes;"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)