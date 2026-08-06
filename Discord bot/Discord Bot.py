import discord
from discord.ext import commands
import surprise as spr
from surprise import Dataset, Reader, SVD
import pandas as pd
import numpy as np
from google import genai
import os
from dotenv import load_dotenv
import random
from datetime import timezone, datetime

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client once when the bot starts
client = genai.Client(
    api_key=GEMINI_API_KEY
)

df = pd.read_csv("ratings.csv")

df = df.rename(columns={
    "userId": "user_id",
    "movieId": "item_id"
})

# Ensure correct data types
df["user_id"] = df["user_id"].astype(int)
df["item_id"] = df["item_id"].astype(int)
df["rating"] = df["rating"].astype(float)

now_utc = datetime.now(timezone.utc)
now = int(now_utc.timestamp())


df_movie = pd.read_csv("movies.csv")

df_movie = df_movie.rename(columns={
    "movieId": "movie_id"
})




reader = Reader(rating_scale=(1, 5))


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents
)
STARTER_MOVIES = {
    1: "Toy Story (1995)",
    2: "Jumanji (1995)",
    3: "Grumpier Old Men (1995)",
    6: "Heat (1995)",
    10: "GoldenEye (1995)",
    11: "American President, The (1995)",
    16: "Casino (1995)",
    17: "Sense and Sensibility (1995)",
    21: "Get Shorty (1995)",
    32: "Twelve Monkeys (1995)",
    34: "Babe (1995)",
    47: "Seven (Se7en) (1995)",
    50: "Usual Suspects, The (1995)",
    62: "Mr. Holland's Opus (1995)",
    65: "Bio-Dome (1996)",
    95: "Broken Arrow (1996)",
    110: "Braveheart (1995)",
    150: "Apollo 13 (1995)",
    260: "Star Wars: Episode IV - A New Hope (1977)",
    296: "Pulp Fiction (1994)",
    318: "Shawshank Redemption, The (1994)",
    356: "Forrest Gump (1994)",
    364: "Lion King, The (1994)",
    480: "Jurassic Park (1993)",
    527: "Schindler's List (1993)",
    541: "Blade Runner (1982)",
    589: "Terminator 2: Judgment Day (1991)",
    593: "Silence of the Lambs, The (1991)",
    608: "Fargo (1996)",
    858: "Godfather, The (1972)",
    904: "Rear Window (1954)",
    912: "Casablanca (1942)",
    919: "Wizard of Oz, The (1939)",
    923: "Citizen Kane (1941)",
    1089: "Reservoir Dogs (1992)",
    1196: "Star Wars: Episode V - The Empire Strikes Back (1980)",
    1198: "Raiders of the Lost Ark (1981)",
    1210: "Star Wars: Episode VI - Return of the Jedi (1983)",
    1213: "Goodfellas (1990)",
    1221: "Godfather: Part II, The (1974)",
    1222: "Full Metal Jacket (1987)",
    1240: "Terminator, The (1984)",
    1270: "Back to the Future (1985)",
    1356: "Star Trek: First Contact (1996)",
    1580: "Men in Black (1997)",
    1721: "Titanic (1997)",
    2028: "Saving Private Ryan (1998)",
    2571: "Matrix, The (1999)",
    2858: "American Beauty (1999)",
    2959: "Fight Club (1999)",
    4993: "Lord of the Rings: The Fellowship of the Ring (2001)",
    5952: "Lord of the Rings: The Two Towers (2002)",
    7153: "Lord of the Rings: The Return of the King (2003)"
}
keys = random.sample(list(STARTER_MOVIES.keys()), 20)
current_selection={}
@bot.event
async def on_ready():
    global keys
    print(f'Logged in as {bot.user} server')
    
    current_selection = {k: STARTER_MOVIES[k] for k in keys}
    channel = bot.get_channel(1528787719604539415)

    message = "\n".join(
        f"⭐ {title}"
        for title in current_selection.values()
    )
    if channel: 
        await channel.send(# pyright: ignore[reportAttributeAccessIssue]
            f""" 
Rate these movies from 1-5:
{message}

Example:
!give 5 4 3 5 2 4 5 3 5 4 5 5 4 3 4 2 5 5 5 4
""")


@bot.command()
async def give(
    ctx,
    r1: float, r2: float, r3: float, r4: float, r5: float,
    r6: float, r7: float, r8: float, r9: float, r10: float,
    r11: float, r12: float, r13: float, r14: float, r15: float,
    r16: float, r17: float, r18: float, r19: float, r20: float
):
    global df, STARTER_MOVIES,keys
    current_selection = {k: STARTER_MOVIES[k] for k in keys}
    uid = 1000

    # Remove previous ratings
    df = df[df["user_id"] != uid]

    ratings = [
        r1, r2, r3, r4, r5,
        r6, r7, r8, r9, r10,
        r11, r12, r13, r14, r15,
        r16, r17, r18, r19, r20
    ]

    temp_df = pd.DataFrame({
        "item_id": list(keys),
        "rating": ratings
    })

    temp_df["user_id"] = uid
    temp_df["timestamp"] = now

    temp_df["item_id"] = temp_df["item_id"].astype(int)
    temp_df["rating"] = temp_df["rating"].astype(float)
    temp_df["user_id"] = int(uid)

    df = pd.concat(
        [df, temp_df],
        ignore_index=True
    )

    await ctx.send("✅ Ratings saved!")


@bot.command()
async def recommend(ctx, raw=0, uid=1000, want_movie=0):

    # Train recommendation model
    data = Dataset.load_from_df(
        df[['user_id', 'item_id', 'rating']],
        reader
    )

    trainset = data.build_full_trainset()

    algo = SVD()
    algo.fit(trainset)


    rated_movies = set(
        df[df["user_id"] == uid]["item_id"]
    )

    recommendations = []


    # Predict every movie
    for _, row in df_movie.iterrows():

        movie_id = int(row["movie_id"])

        if movie_id in rated_movies:
            continue

        pred = algo.predict(
            uid,
            movie_id
        )

        recommendations.append(
            (pred.est, row["title"])
        )


    recommendations.sort(
        key=lambda x: x[0],
        reverse=True
    )

    recommendations = recommendations[:10]


    movie_list = "\n".join(
        f"⭐ {title}"
        for score, title in recommendations
    )


    if want_movie in df_movie["movie_id"].values:

        wanted = df_movie.loc[
            df_movie["movie_id"] == want_movie,
            "title"
        ].iloc[0]

    else:
        wanted = "No specific movie requested."

    if not raw:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
    Write a friendly Discord message explaining why these are good recommendations.

    Recommended movies:

    {recommendations}

    Keep the response below 1500 characters.

    Highlight the most relevant movies but specifically those rear the top of the list.

    Only discuss movies in the provided list.
    Do not add extra movies.
    Use the movie titles exactly as provided.
    Do not change release years.
    """
        )


        await ctx.send(response.text)
        



    if raw:
        await ctx.send(
            "\n".join(
                f"{score:.3f} - {title}"
                for score, title in recommendations

            )
        )


bot.run(DISCORD_TOKEN) # type: ignore