from sqlmodel import SQLModel, create_engine

hostname = "fire_db"
port = 3306
username = "root"       # This is a placeholder for development
password = "root"       # This is a placeholder for development
db_name = "portfolio"
engine = create_engine(f"mariadb+mariadbconnector://{username}:{password}@{hostname}:{port}/{db_name}",
                       pool_pre_ping=True,
                       pool_recycle=3600)


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)
