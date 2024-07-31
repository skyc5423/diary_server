from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db_classes import Base

# TODO: Network error resolving.
DATABASE_URL = "mysql+mysqlconnector://root:t7835423@0.0.0.0/diary"

engine = create_engine(DATABASE_URL, pool_recycle=14400, pool_size=5, max_overflow=20, echo=False, echo_pool=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

TEST_DATABASE_URL = "mysql+mysqlconnector://root:t7835423@0.0.0.0/diary_test"

test_engine = create_engine(TEST_DATABASE_URL, pool_recycle=14400, pool_size=1, max_overflow=4, echo=False,
                            echo_pool=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=test_engine)

Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=test_engine)


def get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
