from fastapi import FastAPI, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Movie, Actor
import time

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/movies")
def get_movies(
    response: Response,
    year_min: int | None = None,
    year_max: int | None = None,
    limit: int | None = None,
    offset: int | None = None,
):
    db: Session = SessionLocal()
    start_time = time.time()

    query = (
        select(
            Movie.id,
            Movie.title,
            Movie.year,
            func.count(Actor.id).label("actor_count")
        )
        .join(Actor, Movie.id == Actor.movie_id, isouter=True)
        .group_by(Movie.id)
        .order_by(Movie.year.desc())
    )

    if year_min is not None:
        query = query.where(Movie.year >= year_min)
    if year_max is not None:
        query = query.where(Movie.year <= year_max)
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    results = db.execute(query).all()

    query_time = round(time.time() - start_time, 4)
    response.headers["X-Query-Time"] = str(query_time)

    movies = [
        {"id": r.id, "title": r.title, "year": r.year, "actor_count": r.actor_count}
        for r in results
    ]

    return movies
