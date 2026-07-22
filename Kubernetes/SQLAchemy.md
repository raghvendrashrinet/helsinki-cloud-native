## 🧩 How SQLAlchemy Works
Low‑level toolkit for building SQL statements programmatically.
How it works:
#### 1. Core (SQL Expression Language)
 * You define tables and columns in Python.
 * You construct SQL queries using Python objects (select(), insert(), update()).
 * SQLAlchemy translates these into actual SQL strings and executes them against the database.

eg:
```python
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select

engine = create_engine("postgresql://user:pass@host:5432/db")
metadata = MetaData()
users = Table("users", metadata,
              Column("id", Integer, primary_key=True),
              Column("name", String))

stmt = select(users).where(users.c.id == 1)
with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.fetchall())
```
#### 2. ORM (Object Relational Mapper)
Purpose: Higher‑level abstraction that maps Python classes to database tables.

How it works:
* You define Python classes with attributes corresponding to table columns.
* SQLAlchemy automatically handles translating object changes into SQL (INSERT, UPDATE, DELETE).
* Queries return Python objects instead of raw rows.
```python
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

engine = create_engine("postgresql://user:pass@host:5432/db")
Session = sessionmaker(bind=engine)
session = Session()

# Insert
new_user = User(name="Raghvendra")
session.add(new_user)
session.commit()

# Query
user = session.query(User).filter_by(name="Raghvendra").first()
print(user.id, user.name)
```
