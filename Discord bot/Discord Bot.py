import discord
from discord.ext import commands
import surprise as spr
from surprise import Dataset, Reader, SVD
import pandas as pd
import numpy as np
from google import genai
import os
from dotenv import load_dotenv

from datetime import timezone, datetime

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client once when the bot starts
client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Load MovieLens dataset
data = Dataset.load_builtin('ml-100k')

df = pd.DataFrame(
    data.raw_ratings,
    columns=['user_id', 'item_id', 'rating', 'timestamp']
)

# Ensure correct data types
df["user_id"] = df["user_id"].astype(int)
df["item_id"] = df["item_id"].astype(int)
df["rating"] = df["rating"].astype(float)

now_utc = datetime.now(timezone.utc)
now = int(now_utc.timestamp())


df_users = pd.read_csv('u.user', sep='|')

df_movie = pd.read_csv(
    'u_movies.tsv',
    sep='|',
    encoding='utf-8'
)

df_movie = df_movie.drop(columns='unknown')


reader = Reader(rating_scale=(1, 5))


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents
)


STARTER_MOVIES = {
    1: "Toy Story (1995)",
    50: "Star Wars (1977)",
    82: "Jurassic Park (1993)",
    89: "Blade Runner (1982)",
    94: "Home Alone (1990)",

    7: "Twelve Monkeys (1995)",
    98: "Silence of the Lambs (1991)",
    121: "Independence Day (1996)",
    127: "Godfather (1972)",
    172: "Empire Strikes Back (1980)",

    174: "Raiders of the Lost Ark (1981)",
    181: "Return of the Jedi (1983)",
    210: "Indiana Jones and the Last Crusade (1989)",
    222: "Star Trek: First Contact (1996)",
    257: "Men in Black (1997)",

    288: "Scream (1996)",
    300: "Air Force One (1997)",
    313: "Titanic (1997)",
    318: "Schindler's List (1993)",
    483: "Casablanca (1942)"
}


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} server')

    channel = bot.get_channel(1528787719604539415)

    if channel: 
        await channel.send(# pyright: ignore[reportAttributeAccessIssue]
            """ 
Rate these movies from 1-5:

1. Toy Story
2. Star Wars
3. Jurassic Park
4. Blade Runner
5. Home Alone
6. Twelve Monkeys
7. Silence of the Lambs
8. Independence Day
9. The Godfather
10. The Empire Strikes Back
11. Raiders of the Lost Ark
12. Return of the Jedi
13. Indiana Jones and the Last Crusade
14. Star Trek: First Contact
15. Men in Black
16. Scream
17. Air Force One
18. Titanic
19. Schindler's List
20. Casablanca

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
    global df

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
        "item_id": list(STARTER_MOVIES.keys()),
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
async def recommend(ctx, uid=1000, want_movie=0, raw=0):

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


    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
Write a friendly Discord message explaining why these are good recommendations.

Recommended movies:

{movie_list}

The user wants to know if this movie fits them:
{wanted}

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