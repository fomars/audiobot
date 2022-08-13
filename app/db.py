from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
from sqlalchemy.orm import sessionmaker

from app.settings import db_settings, DEBUG

db_engine = create_engine(db_settings.connection_str, echo=DEBUG)

Base = declarative_base()


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


Session = sessionmaker(db_engine)
