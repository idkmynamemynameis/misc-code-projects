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
    2: "GoldenEye (1995)",
    3: "Four Rooms (1995)",
    4: "Get Shorty (1995)",
    5: "Copycat (1995)",
    6: "Shanghai Triad (1995)",
    7: "Twelve Monkeys (1995)",
    8: "Babe (1995)",
    9: "Dead Man Walking (1995)",
    10: "Richard III (1995)",
    11: "Seven (Se7en) (1995)",
    12: "Usual Suspects, The (1995)",
    13: "Mighty Aphrodite (1995)",
    14: "Postino, Il (1994)",
    15: "Mr. Holland's Opus (1995)",
    16: "French Twist (1995)",
    17: "From Dusk Till Dawn (1996)",
    18: "White Balloon, The (1995)",
    19: "Antonia's Line (1995)",
    20: "Angels and Insects (1995)",
    21: "Muppet Treasure Island (1996)",
    22: "Braveheart (1995)",
    23: "Taxi Driver (1976)",
    24: "Rumble in the Bronx (1995)",
    25: "Birdcage, The (1996)",
    26: "Brothers McMullen, The (1995)",
    27: "Bad Boys (1995)",
    28: "Apollo 13 (1995)",
    29: "Batman Forever (1995)",
    30: "Belle de Jour (1967)",
    31: "Crimson Tide (1995)",
    32: "Crumb (1994)",
    33: "Desperado (1995)",
    34: "Doom Generation, The (1995)",
    35: "Free Willy 2 (1995)",
    36: "Mad Love (1995)",
    37: "Nadja (1994)",
    38: "Net, The (1995)",
    39: "Strange Days (1995)",
    40: "To Wong Foo, Thanks for Everything! Julie Newmar (1995)",
    41: "Billy Madison (1995)",
    42: "Clerks (1994)",
    43: "Disclosure (1994)",
    44: "Dolores Claiborne (1994)",
    45: "Eat Drink Man Woman (1994)",
    46: "Exotica (1994)",
    47: "Ed Wood (1994)",
    48: "Hoop Dreams (1994)",
    49: "I.Q. (1994)",
    50: "Star Wars (1977)",
    51: "Legends of the Fall (1994)",
    52: "Madness of King George, The (1994)",
    53: "Natural Born Killers (1994)",
    54: "Outbreak (1995)",
    55: "Professional, The / Leon (1994)",
    56: "Pulp Fiction (1994)",
    57: "Priest (1994)",
    58: "Quiz Show (1994)",
    59: "Three Colors: Red (1994)",
    60: "Three Colors: Blue (1993)",
    61: "Three Colors: White (1994)",
    62: "Stargate (1994)",
    63: "Santa Clause, The (1994)",
    64: "Shawshank Redemption, The (1994)",
    65: "What's Eating Gilbert Grape (1993)",
    66: "While You Were Sleeping (1995)",
    67: "Ace Ventura: Pet Detective (1994)",
    68: "Crow, The (1994)",
    69: "Forrest Gump (1994)",
    70: "Four Weddings and a Funeral (1994)",
    71: "Lion King, The (1994)",
    72: "Mask, The (1994)",
    73: "Maverick (1994)",
    74: "Faster Pussycat! Kill! Kill! (1965)",
    76: "Carlito's Way (1993)",
    77: "Firm, The (1993)",
    78: "Free Willy (1993)",
    79: "Fugitive, The (1993)",
    80: "Hot Shots! Part Deux (1993)",
    81: "Hudsucker Proxy, The (1994)",
    82: "Jurassic Park (1993)",
    83: "Much Ado About Nothing (1993)",
    85: "Ref, The (1994)",
    86: "Remains of the Day, The (1993)",
    87: "Searching for Bobby Fischer (1993)",
    88: "Sleepless in Seattle (1993)",
    89: "Blade Runner (1982)",
    90: "So I Married an Axe Murderer (1993)",
    91: "Nightmare Before Christmas, The (1993)",
    92: "True Romance (1993)",
    93: "Welcome to the Dollhouse (1995)",
    94: "Home Alone (1990)",
    95: "Aladdin (1992)",
    96: "Terminator 2: Judgment Day (1991)",
    97: "Dances with Wolves (1990)",
    98: "Silence of the Lambs, The (1991)",
    99: "Snow White and the Seven Dwarfs (1937)",
    100: "Fargo (1996)",
    121: "Independence Day (1996)",
    127: "Godfather, The (1972)",
    172: "Empire Strikes Back, The (1980)",
    174: "Raiders of the Lost Ark (1981)",
    181: "Return of the Jedi (1983)",
    195: "Terminator, The (1984)",
    204: "Back to the Future (1985)",
    210: "Indiana Jones and the Last Crusade (1989)",
    222: "Star Trek: First Contact (1996)",
    234: "Jaws (1975)",
    257: "Men in Black (1997)",
    269: "Full Monty, The (1997)",
    288: "Scream (1996)",
    300: "Air Force One (1997)",
    302: "L.A. Confidential (1997)",
    313: "Titanic (1997)",
    316: "As Good As It Gets (1997)",
    318: "Schindler's List (1993)",
    357: "One Flew Over the Cuckoo's Nest (1975)",
    483: "Casablanca (1942)",
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