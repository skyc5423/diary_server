from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db_classes import Base

DATABASE_URL = "mysql+mysqlconnector://root:t7835423@localhost/diary"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_DATABASE_URL = "mysql+mysqlconnector://root:t7835423@localhost/diary_test"

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=test_engine)
