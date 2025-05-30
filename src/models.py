from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)

    fav_planets: Mapped[List["FavPlanet"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    fav_characters: Mapped[List["FavCharacter"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)

    favorited_by: Mapped[List["FavPlanet"]] = relationship(back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)

    favorited_by: Mapped[List["FavCharacter"]] = relationship(back_populates="character")

    def serialize_basic(self):
        return {
            "id": self.id,
            "name": self.name
        }


class FavPlanet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"))

    user: Mapped["User"] = relationship(back_populates="fav_planets")
    planet: Mapped["Planet"] = relationship(back_populates="favorited_by")


class FavCharacter(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"))

    user: Mapped["User"] = relationship(back_populates="fav_characters")
    character: Mapped["Character"] = relationship(back_populates="favorited_by")