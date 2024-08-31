from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)
from config import Config


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    fullname: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    passhash: Mapped[str] = mapped_column(String(255), nullable=True)
    pswd_create: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=func.now()
    )
    change_pswd: Mapped[bool] = mapped_column(Boolean(), default=True)
    blocked: Mapped[bool] = mapped_column(Boolean(), default=False)
    deleted: Mapped[bool] = mapped_column(Boolean(), default=False)
    attempt: Mapped[int] = mapped_column(Integer(), default=0, nullable=True)
    role: Mapped[str] = mapped_column(String(), nullable=False)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    region: Mapped[str] = mapped_column(String(255), nullable=True)
    persons: Mapped[List["Persons"]] = relationship(back_populates="users")
    staffs: Mapped[List["Staffs"]] = relationship(back_populates="users")
    previous: Mapped[List["Previous"]] = relationship(back_populates="users")
    educations: Mapped[List["Educations"]] = relationship(back_populates="users")
    documents: Mapped[List["Documents"]] = relationship(back_populates="users")
    addresses: Mapped[List["Addresses"]] = relationship(back_populates="users")
    contacts: Mapped[List["Contacts"]] = relationship(back_populates="users")
    workplaces: Mapped[List["Workplaces"]] = relationship(back_populates="users")
    affilations: Mapped[List["Affilations"]] = relationship(back_populates="users")
    relations: Mapped[List["Relations"]] = relationship(back_populates="users")
    checks: Mapped[List["Checks"]] = relationship(back_populates="users")
    poligrafs: Mapped[List["Poligrafs"]] = relationship(back_populates="users")
    investigations: Mapped[List["Investigations"]] = relationship(
        back_populates="users"
    )
    inquiries: Mapped[List["Inquiries"]] = relationship(back_populates="users")


class Persons(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    surname: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    firstname: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    patronymic: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    birthplace: Mapped[str] = mapped_column(Text, nullable=True)
    citizenship: Mapped[str] = mapped_column(String(255), nullable=True)
    dual: Mapped[str] = mapped_column(String(255), nullable=True)
    snils: Mapped[str] = mapped_column(String(11), nullable=True)
    inn: Mapped[str] = mapped_column(String(12), nullable=True, index=True)
    marital: Mapped[str] = mapped_column(String(255), nullable=True)
    addition: Mapped[str] = mapped_column(Text, nullable=True)
    destination: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    region: Mapped[str] = mapped_column(String(255), nullable=True)
    isbusy: Mapped[bool] = mapped_column(Boolean(), default=False)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    previous: Mapped[List["Previous"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    educations: Mapped[List["Educations"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    staffs: Mapped[List["Staffs"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    documents: Mapped[List["Documents"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    addresses: Mapped[List["Addresses"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    workplaces: Mapped[List["Workplaces"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    contacts: Mapped[List["Contacts"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    affilations: Mapped[List["Affilations"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    relations: Mapped[List["Relations"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    checks: Mapped[List["Checks"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    inquiries: Mapped[List["Inquiries"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    poligrafs: Mapped[List["Poligrafs"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    investigations: Mapped[List["Investigations"]] = relationship(
        back_populates="persons", cascade="all, delete, delete-orphan"
    )
    users: Mapped[List["Users"]] = relationship(back_populates="persons")


class Previous(Base):
    __tablename__ = "previous"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    surname: Mapped[str] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str] = mapped_column(String(255), nullable=True)
    patronymic: Mapped[str] = mapped_column(String(255), nullable=True)
    changed: Mapped[str] = mapped_column(String(255), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="previous")
    users: Mapped[List["Users"]] = relationship(back_populates="previous")


class Educations(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    view: Mapped[str] = mapped_column(String(255), nullable=True)
    institution: Mapped[str] = mapped_column(Text, nullable=True)
    finished: Mapped[int] = mapped_column(Integer, nullable=True)
    specialty: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="educations")
    users: Mapped[List["Users"]] = relationship(back_populates="educations")


class Staffs(Base):
    __tablename__ = "staffs"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    position: Mapped[str] = mapped_column(Text, nullable=True)
    department: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="staffs")
    users: Mapped[List["Users"]] = relationship(back_populates="staffs")


class Documents(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    view: Mapped[str] = mapped_column(String(255), nullable=True)
    series: Mapped[str] = mapped_column(String(255), nullable=True)
    digits: Mapped[str] = mapped_column(String(255), nullable=True)
    agency: Mapped[str] = mapped_column(Text, nullable=True)
    issue: Mapped[datetime] = mapped_column(Date, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="documents")
    users: Mapped[List["Users"]] = relationship(back_populates="documents")


class Addresses(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    view: Mapped[str] = mapped_column(String(255), nullable=True)
    addresses: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="addresses")
    users: Mapped[List["Users"]] = relationship(back_populates="addresses")


class Contacts(Base):
    """Create model for contacts"""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    view: Mapped[str] = mapped_column(String(255), nullable=True)
    contact: Mapped[str] = mapped_column(String(255), nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="contacts")
    users: Mapped[List["Users"]] = relationship(back_populates="contacts")


class Workplaces(Base):
    __tablename__ = "workplaces"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    now_work: Mapped[bool] = mapped_column(Boolean, nullable=True)
    starts: Mapped[datetime] = mapped_column(Date, nullable=True)
    finished: Mapped[datetime] = mapped_column(Date, nullable=True)
    workplace: Mapped[str] = mapped_column(String(255), nullable=True)
    addresses: Mapped[str] = mapped_column(Text, nullable=True)
    position: Mapped[str] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="workplaces")
    users: Mapped[List["Users"]] = relationship(back_populates="workplaces")


class Affilations(Base):
    __tablename__ = "affilations"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    view: Mapped[str] = mapped_column(String(255), nullable=True)
    organization: Mapped[str] = mapped_column(Text, nullable=True)
    inn: Mapped[str] = mapped_column(String(255), nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="affilations")
    users: Mapped[List["Users"]] = relationship(back_populates="affilations")


class Relations(Base):
    __tablename__ = "relations"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    relation: Mapped[str] = mapped_column(String(255), nullable=True)
    relation_id: Mapped[int] = mapped_column(Integer(), nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persons: Mapped[List["Persons"]] = relationship(back_populates="relations")
    users: Mapped[List["Users"]] = relationship(back_populates="relations")


class Checks(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    workplace: Mapped[str] = mapped_column(Text, nullable=True)
    document: Mapped[str] = mapped_column(Text, nullable=True)
    inn: Mapped[str] = mapped_column(Text, nullable=True)
    debt: Mapped[str] = mapped_column(Text, nullable=True)
    bankruptcy: Mapped[str] = mapped_column(Text, nullable=True)
    bki: Mapped[str] = mapped_column(Text, nullable=True)
    courts: Mapped[str] = mapped_column(Text, nullable=True)
    affilation: Mapped[str] = mapped_column(Text, nullable=True)
    terrorist: Mapped[str] = mapped_column(Text, nullable=True)
    mvd: Mapped[str] = mapped_column(Text, nullable=True)
    internet: Mapped[str] = mapped_column(Text, nullable=True)
    cronos: Mapped[str] = mapped_column(Text, nullable=True)
    cros: Mapped[str] = mapped_column(Text, nullable=True)
    addition: Mapped[str] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    conclusion: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    persons: Mapped[List["Persons"]] = relationship(back_populates="checks")
    users: Mapped[List["Users"]] = relationship(back_populates="checks")


class Poligrafs(Base):
    __tablename__ = "poligrafs"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    theme: Mapped[str] = mapped_column(String(255), nullable=True)
    results: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    persons: Mapped[List["Persons"]] = relationship(back_populates="poligrafs")
    users: Mapped[List["Users"]] = relationship(back_populates="poligrafs")


class Investigations(Base):
    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    theme: Mapped[str] = mapped_column(String(255), nullable=True)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    persons: Mapped[List["Persons"]] = relationship(back_populates="investigations")
    users: Mapped[List["Users"]] = relationship(back_populates="investigations")


class Inquiries(Base):
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(
        nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    info: Mapped[str] = mapped_column(Text, nullable=True)
    initiator: Mapped[str] = mapped_column(String(255), nullable=True)
    origins: Mapped[str] = mapped_column(String(255), nullable=True)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    persons: Mapped[List["Persons"]] = relationship(back_populates="inquiries")
    users: Mapped[List["Users"]] = relationship(back_populates="inquiries")


tables_models = {
    "persons": Persons,
    "previous": Previous,
    "educations": Educations,
    "staffs": Staffs,
    "documents": Documents,
    "addresses": Addresses,
    "contacts": Contacts,
    "relations": Relations,
    "workplaces": Workplaces,
    "affilations": Affilations,
    "checks": Checks,
    "poligrafs": Poligrafs,
    "investigations": Investigations,
    "inquiries": Inquiries,
}

engine = create_engine(Config.DATABASE_URI)
db_session = scoped_session(sessionmaker(autoflush=False, bind=engine))
Base.metadata.create_all(bind=engine)
