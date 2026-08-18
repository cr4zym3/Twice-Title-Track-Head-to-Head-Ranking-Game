import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random


# ============================================================
#                    APPLICATION SETTINGS
# ============================================================

WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 850

IMAGE_SIZE = 300
SMALL_IMAGE_SIZE = 100

BACKGROUND = "#0d0f14"
CARD_BACKGROUND = "#171a21"
CARD_HOVER = "#252a34"
PANEL_BACKGROUND = "#14171d"

TEXT = "#ffffff"
SECONDARY_TEXT = "#9ca3af"

ACCENT = "#ff4fa3"
ACCENT_HOVER = "#ff6db5"

GREEN = "#34d399"
GOLD = "#fbbf24"

K_FACTOR = 32
RATING_GAP = 40


# ============================================================
#                     IMAGE FILES
# ============================================================
#
# Put your album covers inside:
#
#     SONG RANKER/
#         your_program.py
#         images/
#
# The program will look for the filenames below.
#
# JPG, JPEG, PNG, WEBP, and other common image formats
# are supported by Pillow.
#
# ============================================================

IMAGE_FILES = {

    "Like OOH-AHH": "like_ooh_ahh.jpg",
    "Cheer Up": "cheer_up.jpg",
    "TT": "tt.jpg",
    "Knock Knock": "knock_knock.jpg",
    "Signal": "signal.jpg",
    "Likey": "likey.jpg",
    "Heart Shaker": "heart_shaker.jpg",
    "What Is Love?": "what_is_love.jpg",
    "Dance the Night Away": "dance_the_night_away.jpg",
    "Yes or Yes": "yes_or_yes.jpg",
    "Fancy": "fancy.jpg",
    "Feel Special": "feel_special.jpg",
    "More & More": "more_and_more.jpg",
    "I Can't Stop Me": "i_cant_stop_me.jpg",
    "Alcohol-Free": "alcohol_free.jpg",
    "Scientist": "scientist.jpg",
    "Talk That Talk": "talk_that_talk.jpg",
    "Set Me Free": "set_me_free.jpg",
    "One Spark": "one_spark.jpg",
    "Strategy": "strategy.jpg",
    "This is For": "this_is_for.jpg",
    "ME+YOU": "me_you.jpg",
}


# ============================================================
#                     SONG LIST
# ============================================================

SONG_NAMES = [

    "Like OOH-AHH",
    "Cheer Up",
    "TT",
    "Knock Knock",
    "Signal",
    "Likey",
    "Heart Shaker",
    "What Is Love?",
    "Dance the Night Away",
    "Yes or Yes",
    "Fancy",
    "Feel Special",
    "More & More",
    "I Can't Stop Me",
    "Alcohol-Free",
    "Scientist",
    "Talk That Talk",
    "Set Me Free",
    "One Spark",
    "Strategy",
    "This is For",
    "ME+YOU",

]


# ============================================================
#                     SONG CLASS
# ============================================================

class Song:

    def __init__(self, name):

        self.name = name

        self.rating = 1500.0

        self.comparisons = 0

        self.wins = 0

        self.losses = 0

        self.image_filename = IMAGE_FILES.get(name)


# ============================================================
#                     ELO SYSTEM
# ============================================================

def expected_score(rating_a, rating_b):

    return 1 / (
        1 + 10 ** (
            (rating_b - rating_a) / 400
        )
    )


def update_ratings(winner, loser):

    expected_winner = expected_score(
        winner.rating,
        loser.rating
    )

    expected_loser = expected_score(
        loser.rating,
        winner.rating
    )

    winner.rating += K_FACTOR * (
        1 - expected_winner
    )

    loser.rating += K_FACTOR * (
        0 - expected_loser
    )

    winner.comparisons += 1
    loser.comparisons += 1

    winner.wins += 1
    loser.losses += 1


# ============================================================
#                     GLOBAL SONG LIST
# ============================================================

songs = [
    Song(name)
    for name in SONG_NAMES
]


def get_ranking():

    return sorted(
        songs,
        key=lambda song: song.rating,
        reverse=True
    )


# ============================================================
#                     CHOOSE MATCHUP
# ============================================================

def choose_pair(compared_pairs):

    ranking = get_ranking()

    possible_pairs = []

    for i in range(len(ranking)):

        for j in range(i + 1, len(ranking)):

            x = ranking[i]
            y = ranking[j]

            pair = frozenset((x, y))

            if pair in compared_pairs:
                continue

            rating_difference = abs(
                x.rating - y.rating
            )

            usefulness = (
                1 /
                (1 + rating_difference)
            )

            possible_pairs.append(
                (
                    usefulness,
                    x,
                    y
                )
            )

    if not possible_pairs:

        return None, None

    possible_pairs.sort(
        key=lambda item: item[0],
        reverse=True
    )

    top_choices = possible_pairs[
        :min(8, len(possible_pairs))
    ]

    _, x, y = random.choice(top_choices)

    return x, y


# ============================================================
#                     RELIABILITY
# ============================================================

def ranking_is_reliable():

    ranking = get_ranking()

    # Every song should have several comparisons.
    for song in songs:

        if song.comparisons < 5:

            return False

    # Make sure adjacent rankings have enough separation.
    for i in range(len(ranking) - 1):

        first = ranking[i]
        second = ranking[i + 1]

        rating_gap = (
            first.rating -
            second.rating
        )

        if rating_gap < RATING_GAP:

            return False

    return True


# ============================================================
#                     MAIN APPLICATION
# ============================================================

class SongRankerApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "TWICE Song Ranker"
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(
            1000,
            700
        )

        self.root.configure(
            bg=BACKGROUND
        )

        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.comparison_number = 0

        self.compared_pairs = set()

        self.song_a = None

        self.song_b = None

        self.finished = False

        # ----------------------------------------------------
        # IMAGE STORAGE
        # ----------------------------------------------------

        self.image_cache = {}

        self.placeholder_cache = {}

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.create_styles()

        self.create_interface()

        self.start_new_ranking()


    # ========================================================
    #                     STYLES
    # ========================================================

    def create_styles(self):

        style = ttk.Style()

        try:

            style.theme_use("clam")

        except Exception:

            pass

        style.configure(
            "Treeview",

            background=CARD_BACKGROUND,

            foreground=TEXT,

            fieldbackground=CARD_BACKGROUND,

            rowheight=42,

            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",

            background="#242832",

            foreground=TEXT,

            font=("Arial", 11, "bold")
        )

        style.map(
            "Treeview",

            background=[
                ("selected", ACCENT)
            ],

            foreground=[
                ("selected", TEXT)
            ]
        )


    # ========================================================
    #                     MAIN UI
    # ========================================================

    def create_interface(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self.root,
            bg=BACKGROUND
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(25, 15)
        )

        title = tk.Label(
            header,

            text="Twice Title Track Ranker 🍭",

            font=(
                "Arial",
                30,
                "bold"
            ),

            fg=TEXT,

            bg=BACKGROUND
        )

        title.pack()

        subtitle = tk.Label(
            header,

            text=(
                "Choose the song you prefer "
                "— every choice changes the rankings"
            ),

            font=(
                "Arial",
                12
            ),

            fg=SECONDARY_TEXT,

            bg=BACKGROUND
        )

        subtitle.pack(
            pady=(5, 0)
        )


        # ----------------------------------------------------
        # STATS PANEL
        # ----------------------------------------------------

        stats = tk.Frame(
            self.root,

            bg=PANEL_BACKGROUND
        )

        stats.pack(
            fill="x",

            padx=35,

            pady=(0, 15)
        )


        self.comparison_label = tk.Label(
            stats,

            text="Comparisons: 0",

            font=(
                "Arial",
                12,
                "bold"
            ),

            fg=TEXT,

            bg=PANEL_BACKGROUND
        )

        self.comparison_label.pack(
            side="left",

            padx=25,

            pady=14
        )


        self.minimum_label = tk.Label(
            stats,

            text="Minimum: 0",

            font=(
                "Arial",
                11
            ),

            fg=SECONDARY_TEXT,

            bg=PANEL_BACKGROUND
        )

        self.minimum_label.pack(
            side="left",

            padx=15
        )


        self.maximum_label = tk.Label(
            stats,

            text="Maximum: 0",

            font=(
                "Arial",
                11
            ),

            fg=SECONDARY_TEXT,

            bg=PANEL_BACKGROUND
        )

        self.maximum_label.pack(
            side="left",

            padx=15
        )


        self.status_label = tk.Label(
            stats,

            text="Ranking in progress",

            font=(
                "Arial",
                11,
                "bold"
            ),

            fg=ACCENT,

            bg=PANEL_BACKGROUND
        )

        self.status_label.pack(
            side="right",

            padx=25
        )


        # ----------------------------------------------------
        # PROGRESS BAR
        # ----------------------------------------------------

        progress_frame = tk.Frame(
            self.root,

            bg=BACKGROUND
        )

        progress_frame.pack(
            fill="x",

            padx=35
        )

        self.progress = ttk.Progressbar(
            progress_frame,

            orient="horizontal",

            mode="determinate",

            maximum=100
        )

        self.progress.pack(
            fill="x"
        )


        # ----------------------------------------------------
        # COMPARISON AREA
        # ----------------------------------------------------

        comparison_area = tk.Frame(
            self.root,

            bg=BACKGROUND
        )

        comparison_area.pack(
            fill="both",

            expand=True,

            padx=35,

            pady=20
        )


        # ----------------------------------------------------
        # SONG A
        # ----------------------------------------------------

        self.song_a_card = self.create_song_card(
            comparison_area
        )

        self.song_a_card.pack(
            side="left",

            fill="both",

            expand=True,

            padx=(0, 10)
        )


        # ----------------------------------------------------
        # VS
        # ----------------------------------------------------

        vs_frame = tk.Frame(
            comparison_area,

            bg=BACKGROUND,

            width=65
        )

        vs_frame.pack(
            side="left",

            fill="y"
        )

        vs_frame.pack_propagate(False)

        vs_label = tk.Label(
            vs_frame,

            text="VS",

            font=(
                "Arial",
                18,
                "bold"
            ),

            fg="#6b7280",

            bg=BACKGROUND
        )

        vs_label.place(
            relx=0.5,

            rely=0.5,

            anchor="center"
        )


        # ----------------------------------------------------
        # SONG B
        # ----------------------------------------------------

        self.song_b_card = self.create_song_card(
            comparison_area
        )

        self.song_b_card.pack(
            side="left",

            fill="both",

            expand=True,

            padx=(10, 0)
        )


        # ----------------------------------------------------
        # BOTTOM CONTROLS
        # ----------------------------------------------------

        bottom = tk.Frame(
            self.root,

            bg=BACKGROUND
        )

        bottom.pack(
            fill="x",

            padx=35,

            pady=(0, 25)
        )


        self.next_label = tk.Label(
            bottom,

            text="Choose your favorite",

            font=(
                "Arial",
                11
            ),

            fg=SECONDARY_TEXT,

            bg=BACKGROUND
        )

        self.next_label.pack(
            side="left"
        )


        restart_button = tk.Button(
            bottom,

            text="↻  Restart",

            command=self.start_new_ranking,

            font=(
                "Arial",
                10,
                "bold"
            ),

            fg=TEXT,

            bg="#292e38",

            activebackground="#3a404d",

            activeforeground=TEXT,

            relief="flat",

            padx=20,

            pady=9,

            cursor="hand2",

            borderwidth=0
        )

        restart_button.pack(
            side="right"
        )


        ranking_button = tk.Button(
            bottom,

            text="🏆  View Rankings",

            command=self.show_ranking,

            font=(
                "Arial",
                10,
                "bold"
            ),

            fg=TEXT,

            bg=ACCENT,

            activebackground=ACCENT_HOVER,

            activeforeground=TEXT,

            relief="flat",

            padx=20,

            pady=9,

            cursor="hand2",

            borderwidth=0
        )

        ranking_button.pack(
            side="right",

            padx=10
        )


    # ========================================================
    #                     SONG CARD
    # ========================================================

    def create_song_card(self, parent):

        card = tk.Frame(
            parent,

            bg=CARD_BACKGROUND,

            cursor="hand2",

            highlightthickness=1,

            highlightbackground="#252a34"
        )


        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_label = tk.Label(
            card,

            bg=CARD_BACKGROUND,

            cursor="hand2"
        )

        image_label.pack(
            pady=(25, 12)
        )


        # ----------------------------------------------------
        # SONG NAME
        # ----------------------------------------------------

        name_label = tk.Label(
            card,

            text="",

            font=(
                "Arial",
                20,
                "bold"
            ),

            fg=TEXT,

            bg=CARD_BACKGROUND,

            wraplength=400,

            cursor="hand2"
        )

        name_label.pack(
            padx=20,

            pady=(0, 8)
        )


        # ----------------------------------------------------
        # RATING
        # ----------------------------------------------------

        rating_label = tk.Label(
            card,

            text="",

            font=(
                "Arial",
                12,
                "bold"
            ),

            fg=GOLD,

            bg=CARD_BACKGROUND,

            cursor="hand2"
        )

        rating_label.pack(
            pady=2
        )


        # ----------------------------------------------------
        # RECORD
        # ----------------------------------------------------

        record_label = tk.Label(
            card,

            text="",

            font=(
                "Arial",
                10
            ),

            fg=SECONDARY_TEXT,

            bg=CARD_BACKGROUND,

            cursor="hand2"
        )

        record_label.pack(
            pady=(2, 20)
        )


        # Store references.

        card.image_label = image_label
        card.name_label = name_label
        card.rating_label = rating_label
        card.record_label = record_label


        # Bind ALL widgets to the card.

        self.bind_card_events(card)

        return card


    # ========================================================
    #                     CARD EVENTS
    # ========================================================

    def bind_card_events(self, card):

        widgets = [
            card,
            card.image_label,
            card.name_label,
            card.rating_label,
            card.record_label
        ]

        for widget in widgets:

            widget.bind(
                "<Enter>",
                lambda event, c=card:
                self.card_hover(c, True)
            )

            widget.bind(
                "<Leave>",
                lambda event, c=card:
                self.card_hover(c, False)
            )

            widget.bind(
                "<Button-1>",
                lambda event, c=card:
                self.card_clicked(c)
            )


    def card_hover(self, card, hovering):

        if self.finished:
            return

        if hovering:

            new_color = CARD_HOVER

        else:

            new_color = CARD_BACKGROUND

        card.configure(
            bg=new_color
        )

        for child in card.winfo_children():

            try:

                child.configure(
                    bg=new_color
                )

            except Exception:

                pass


    def card_clicked(self, card):

        if self.finished:
            return

        if self.song_a is None or self.song_b is None:
            return

        if card == self.song_a_card:

            self.select_song(
                self.song_a
            )

        elif card == self.song_b_card:

            self.select_song(
                self.song_b
            )


    # ========================================================
    #                     FIND IMAGE
    # ========================================================

    def find_image_file(self, song):

        image_folder = (
            Path(__file__).resolve().parent /
            "images"
        )

        if not image_folder.exists():

            return None


        filename = IMAGE_FILES.get(
            song.name
        )


        if filename:

            exact_path = (
                image_folder /
                filename
            )

            if exact_path.exists():

                return exact_path


        # ----------------------------------------------------
        # If exact filename wasn't found, try to intelligently
        # find the image by name.
        # ----------------------------------------------------

        possible_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".bmp",
            ".gif"
        ]


        normalized_song_name = (
            song.name
            .lower()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
            .replace("'", "")
            .replace("?", "")
            .replace("+", "")
        )


        for file in image_folder.iterdir():

            if not file.is_file():
                continue

            if file.suffix.lower() not in possible_extensions:
                continue


            normalized_filename = (
                file.stem
                .lower()
                .replace(" ", "")
                .replace("-", "")
                .replace("_", "")
                .replace("'", "")
                .replace("?", "")
                .replace("+", "")
            )


            if (
                normalized_filename ==
                normalized_song_name
            ):

                return file


        return None


    # ========================================================
    #                     LOAD IMAGE
    # ========================================================

    def load_song_image(self, song):

        if song.name in self.image_cache:

            return self.image_cache[
                song.name
            ]


        image_path = self.find_image_file(
            song
        )


        # ----------------------------------------------------
        # IMAGE FOUND
        # ----------------------------------------------------

        if image_path:

            try:

                image = Image.open(
                    image_path
                )

                image = image.convert(
                    "RGB"
                )

                image.thumbnail(
                    (
                        IMAGE_SIZE,
                        IMAGE_SIZE
                    ),
                    Image.Resampling.LANCZOS
                )


                canvas = Image.new(
                    "RGB",

                    (
                        IMAGE_SIZE,
                        IMAGE_SIZE
                    ),

                    "#111318"
                )


                x = (
                    IMAGE_SIZE -
                    image.width
                ) // 2

                y = (
                    IMAGE_SIZE -
                    image.height
                ) // 2


                canvas.paste(
                    image,

                    (x, y)
                )


                photo = ImageTk.PhotoImage(
                    canvas
                )


                self.image_cache[
                    song.name
                ] = photo


                return photo


            except Exception as error:

                print(
                    f"Could not load image "
                    f"for {song.name}: {error}"
                )


        # ----------------------------------------------------
        # PLACEHOLDER
        # ----------------------------------------------------

        return self.create_placeholder(
            song
        )


    # ========================================================
    #                     PLACEHOLDER
    # ========================================================

    def create_placeholder(self, song):

        if song.name in self.placeholder_cache:

            return self.placeholder_cache[
                song.name
            ]


        image = Image.new(
            "RGB",

            (
                IMAGE_SIZE,
                IMAGE_SIZE
            ),

            "#242832"
        )


        draw = ImageDraw.Draw(
            image
        )


        # Try to create a nicer placeholder.

        try:

            font = ImageFont.truetype(
                "arial.ttf",
                18
            )

        except Exception:

            font = None


        draw.text(
            (
                IMAGE_SIZE // 2,
                IMAGE_SIZE // 2 - 10
            ),

            "NO IMAGE",

            fill="white",

            anchor="mm",

            font=font
        )


        draw.text(
            (
                IMAGE_SIZE // 2,
                IMAGE_SIZE // 2 + 25
            ),

            song.name,

            fill="#9ca3af",

            anchor="mm",

            font=font
        )


        photo = ImageTk.PhotoImage(
            image
        )


        self.placeholder_cache[
            song.name
        ] = photo


        return photo


    # ========================================================
    #                     UPDATE CARD
    # ========================================================

    def update_song_card(self, card, song):

        image = self.load_song_image(
            song
        )


        card.image_label.configure(
            image=image
        )

        card.image_label.image = image


        card.name_label.configure(
            text=song.name
        )


        card.rating_label.configure(
            text=(
                f"⭐ {song.rating:.0f} Rating"
            )
        )


        card.record_label.configure(
            text=(
                f"{song.wins} wins  •  "
                f"{song.losses} losses  •  "
                f"{song.comparisons} comparisons"
            )
        )


    # ========================================================
    #                     START / RESET
    # ========================================================

    def start_new_ranking(self):

        global songs


        # Reset songs.

        songs = [
            Song(name)
            for name in SONG_NAMES
        ]


        # Reset game state.

        self.comparison_number = 0

        self.compared_pairs = set()

        self.song_a = None

        self.song_b = None

        self.finished = False


        # Reset status.

        self.status_label.configure(
            text="Ranking in progress",

            fg=ACCENT
        )


        self.next_label.configure(
            text="Choose your favorite"
        )


        # Reset card colors.

        self.song_a_card.configure(
            bg=CARD_BACKGROUND
        )

        self.song_b_card.configure(
            bg=CARD_BACKGROUND
        )


        for card in [
            self.song_a_card,
            self.song_b_card
        ]:

            for child in card.winfo_children():

                try:

                    child.configure(
                        bg=CARD_BACKGROUND
                    )

                except Exception:

                    pass


        self.update_stats()

        self.next_matchup()


    # ========================================================
    #                     SELECT SONG
    # ========================================================

    def select_song(self, winner):

        if self.finished:
            return

        if winner is None:
            return


        if winner == self.song_a:

            loser = self.song_b

        else:

            loser = self.song_a


        if loser is None:
            return


        # Update ELO.

        update_ratings(
            winner,
            loser
        )


        # Count comparison.

        self.comparison_number += 1


        # Update interface.

        self.update_stats()


        # Check if ranking should end.

        if self.should_stop():

            self.finish_ranking()

            return


        # Continue.

        self.next_matchup()


    # ========================================================
    #                     STOP CHECK
    # ========================================================

    def should_stop(self):

        num_songs = len(songs)


        max_comparisons = (
            num_songs *
            (num_songs - 1)
            // 2
        )


        min_comparisons = max(
            10,

            int(
                max_comparisons *
                0.35
            )
        )


        if (
            self.comparison_number >=
            max_comparisons
        ):

            return True


        if (
            self.comparison_number >=
            min_comparisons
        ):

            if ranking_is_reliable():

                return True


        return False


    # ========================================================
    #                     NEXT MATCHUP
    # ========================================================

    def next_matchup(self):

        x, y = choose_pair(
            self.compared_pairs
        )


        if x is None or y is None:

            self.finish_ranking()

            return


        self.song_a = x

        self.song_b = y


        self.compared_pairs.add(
            frozenset(
                (x, y)
            )
        )


        self.update_song_card(
            self.song_a_card,
            x
        )


        self.update_song_card(
            self.song_b_card,
            y
        )


        self.next_label.configure(
            text="Click the song you prefer"
        )


        self.status_label.configure(
            text=(
                f"Comparison "
                f"#{self.comparison_number + 1}"
            ),

            fg=ACCENT
        )


    # ========================================================
    #                     UPDATE STATS
    # ========================================================

    def update_stats(self):

        num_songs = len(songs)


        max_comparisons = (
            num_songs *
            (num_songs - 1)
            // 2
        )


        min_comparisons = max(
            10,

            int(
                max_comparisons *
                0.35
            )
        )


        self.comparison_label.configure(
            text=(
                f"Comparisons: "
                f"{self.comparison_number}"
            )
        )


        self.minimum_label.configure(
            text=(
                f"Minimum: "
                f"{min_comparisons}"
            )
        )


        self.maximum_label.configure(
            text=(
                f"Maximum: "
                f"{max_comparisons}"
            )
        )


        percentage = (
            self.comparison_number /
            max_comparisons
        ) * 100


        self.progress["value"] = percentage


    # ========================================================
    #                     FINISH
    # ========================================================

    def finish_ranking(self):

        if self.finished:
            return


        self.finished = True


        self.status_label.configure(
            text="🏆 Ranking Complete!",

            fg=GREEN
        )


        self.next_label.configure(
            text=(
                f"Finished after "
                f"{self.comparison_number} "
                f"comparisons"
            )
        )


        self.update_stats()


        # Automatically show results.

        self.root.after(
            150,
            self.show_ranking
        )


    # ========================================================
    #                     RANKING WINDOW
    # ========================================================

    def show_ranking(self):

        ranking_window = tk.Toplevel(
            self.root
        )


        ranking_window.title(
            "TWICE Song Rankings"
        )


        ranking_window.geometry(
            "1000x800"
        )


        ranking_window.minsize(
            850,
            650
        )


        ranking_window.configure(
            bg=BACKGROUND
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            ranking_window,

            text="🏆 TWICE SONG RANKINGS",

            font=(
                "Arial",
                26,
                "bold"
            ),

            fg=TEXT,

            bg=BACKGROUND
        )

        title.pack(
            pady=(25, 5)
        )


        subtitle = tk.Label(
            ranking_window,

            text=(
                f"{self.comparison_number} "
                f"comparisons completed"
            ),

            font=(
                "Arial",
                11
            ),

            fg=SECONDARY_TEXT,

            bg=BACKGROUND
        )

        subtitle.pack(
            pady=(0, 20)
        )


        ranking = get_ranking()


        # ----------------------------------------------------
        # TOP 3
        # ----------------------------------------------------

        podium = tk.Frame(
            ranking_window,

            bg=BACKGROUND
        )

        podium.pack(
            fill="x",

            padx=30,

            pady=10
        )


        # Second

        if len(ranking) >= 2:

            self.create_podium_card(
                podium,

                ranking[1],

                "🥈",

                2
            )


        # First

        if len(ranking) >= 1:

            self.create_podium_card(
                podium,

                ranking[0],

                "🥇",

                1
            )


        # Third

        if len(ranking) >= 3:

            self.create_podium_card(
                podium,

                ranking[2],

                "🥉",

                3
            )


        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        table_frame = tk.Frame(
            ranking_window,

            bg=BACKGROUND
        )

        table_frame.pack(
            fill="both",

            expand=True,

            padx=30,

            pady=15
        )


        columns = (
            "rank",
            "song",
            "rating",
            "wins",
            "losses",
            "comparisons"
        )


        tree = ttk.Treeview(
            table_frame,

            columns=columns,

            show="headings"
        )


        tree.heading(
            "rank",
            text="#"
        )

        tree.heading(
            "song",
            text="Song"
        )

        tree.heading(
            "rating",
            text="Rating"
        )

        tree.heading(
            "wins",
            text="Wins"
        )

        tree.heading(
            "losses",
            text="Losses"
        )

        tree.heading(
            "comparisons",
            text="Comparisons"
        )


        tree.column(
            "rank",
            width=50,

            anchor="center"
        )

        tree.column(
            "song",
            width=300
        )

        tree.column(
            "rating",
            width=100,

            anchor="center"
        )

        tree.column(
            "wins",
            width=80,

            anchor="center"
        )

        tree.column(
            "losses",
            width=80,

            anchor="center"
        )

        tree.column(
            "comparisons",
            width=120,

            anchor="center"
        )


        for i, song in enumerate(
            ranking,
            1
        ):

            tree.insert(
                "",

                "end",

                values=(
                    i,

                    song.name,

                    f"{song.rating:.0f}",

                    song.wins,

                    song.losses,

                    song.comparisons
                )
            )


        scrollbar = ttk.Scrollbar(
            table_frame,

            orient="vertical",

            command=tree.yview
        )


        tree.configure(
            yscrollcommand=scrollbar.set
        )


        tree.pack(
            side="left",

            fill="both",

            expand=True
        )


        scrollbar.pack(
            side="right",

            fill="y"
        )


        # ----------------------------------------------------
        # CLOSE BUTTON
        # ----------------------------------------------------

        close_button = tk.Button(
            ranking_window,

            text="Close",

            command=ranking_window.destroy,

            font=(
                "Arial",
                10,
                "bold"
            ),

            fg=TEXT,

            bg="#292e38",

            activebackground="#3a404d",

            activeforeground=TEXT,

            relief="flat",

            padx=30,

            pady=9,

            cursor="hand2",

            borderwidth=0
        )

        close_button.pack(
            pady=20
        )


    # ========================================================
    #                     PODIUM CARD
    # ========================================================

    def create_podium_card(
        self,
        parent,
        song,
        medal,
        position
    ):

        card = tk.Frame(
            parent,

            bg=CARD_BACKGROUND,

            padx=20,

            pady=15
        )


        card.pack(
            side="left",

            fill="both",

            expand=True,

            padx=8
        )


        medal_label = tk.Label(
            card,

            text=medal,

            font=(
                "Arial",
                28
            ),

            fg=TEXT,

            bg=CARD_BACKGROUND
        )

        medal_label.pack()


        image = self.load_small_image(
            song
        )


        image_label = tk.Label(
            card,

            image=image,

            bg=CARD_BACKGROUND
        )

        image_label.image = image

        image_label.pack(
            pady=5
        )


        name_label = tk.Label(
            card,

            text=song.name,

            font=(
                "Arial",
                12,
                "bold"
            ),

            fg=TEXT,

            bg=CARD_BACKGROUND,

            wraplength=230
        )

        name_label.pack()


        rating_label = tk.Label(
            card,

            text=f"{song.rating:.0f} rating",

            font=(
                "Arial",
                10
            ),

            fg=GOLD,

            bg=CARD_BACKGROUND
        )

        rating_label.pack(
            pady=(4, 0)
        )


    # ========================================================
    #                     SMALL IMAGE
    # ========================================================

    def load_small_image(self, song):

        key = (
            "small_" +
            song.name
        )


        if key in self.image_cache:

            return self.image_cache[
                key
            ]


        image_path = self.find_image_file(
            song
        )


        if image_path:

            try:

                image = Image.open(
                    image_path
                )

                image = image.convert(
                    "RGB"
                )


                image.thumbnail(
                    (
                        SMALL_IMAGE_SIZE,
                        SMALL_IMAGE_SIZE
                    ),
                    Image.Resampling.LANCZOS
                )


                canvas = Image.new(
                    "RGB",

                    (
                        SMALL_IMAGE_SIZE,
                        SMALL_IMAGE_SIZE
                    ),

                    "#111318"
                )


                x = (
                    SMALL_IMAGE_SIZE -
                    image.width
                ) // 2


                y = (
                    SMALL_IMAGE_SIZE -
                    image.height
                ) // 2


                canvas.paste(
                    image,

                    (x, y)
                )


                photo = ImageTk.PhotoImage(
                    canvas
                )


                self.image_cache[
                    key
                ] = photo


                return photo


            except Exception as error:

                print(
                    f"Could not load small image "
                    f"for {song.name}: {error}"
                )


        # ----------------------------------------------------
        # SMALL PLACEHOLDER
        # ----------------------------------------------------

        image = Image.new(
            "RGB",

            (
                SMALL_IMAGE_SIZE,
                SMALL_IMAGE_SIZE
            ),

            "#242832"
        )


        draw = ImageDraw.Draw(
            image
        )


        draw.text(
            (
                SMALL_IMAGE_SIZE // 2,
                SMALL_IMAGE_SIZE // 2
            ),

            "NO IMAGE",

            fill="white",

            anchor="mm"
        )


        photo = ImageTk.PhotoImage(
            image
        )


        self.image_cache[
            key
        ] = photo


        return photo


# ============================================================
#                     START PROGRAM
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SongRankerApp(
        root
    )

    root.mainloop()