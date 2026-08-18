const IMAGE_FILES = {

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
    "ME+YOU": "me_you.jpg"

};


const SONG_NAMES =
    Object.keys(IMAGE_FILES);


/* =========================================
   ELO SETTINGS
========================================= */

const K_FACTOR = 32;


/* =========================================
   STOPPING SETTINGS
========================================= */

/*
 * The game cannot finish before this.
 *
 * 90 gives the game enough information
 * before it is allowed to stop.
 */
const MIN_COMPARISONS = 90;


/*
 * Hard maximum.
 *
 * 22 songs = 231 unique pairs.
 */
const MAX_COMPARISONS =
    SONG_NAMES.length *
    (SONG_NAMES.length - 1) /
    2;


/*
 * Every song must be compared at least
 * this many times before finishing.
 */
const MIN_SONG_COMPARISONS = 4;


/*
 * We check the ranking every 5 comparisons.
 */
const STABILITY_INTERVAL = 5;


/*
 * How much the ranking can move between
 * stability checks.
 *
 * This is intentionally much more relaxed
 * than the old value of 6.
 */
const MAX_POSITION_CHANGE = 14;


/*
 * Number of consecutive stable checks
 * needed before the ranking can finish.
 */
const STABILITY_CHECKS = 2;


/*
 * Probability adjustment.
 *
 * After the minimum is reached, a stable
 * ranking has a chance to finish.
 *
 * This prevents every game from ending
 * at exactly the same number.
 */
const EARLY_FINISH_CHANCE = 0.65;


/*
 * Additional safety threshold.
 *
 * Once the game reaches this many
 * comparisons, it becomes increasingly
 * willing to finish.
 */
const SOFT_FINISH_POINT = 135;


/*
 * After this point, if the ranking is
 * reasonably stable, finish automatically.
 */
const STRONG_FINISH_POINT = 165;


/* =========================================
   GAME STATE
========================================= */

let songs = [];

let comparisonNumber = 0;

let comparedPairs = new Set();

let songA = null;

let songB = null;

let finished = false;


/*
 * Stores previous rankings for the
 * stability system.
 */
let previousRanking = null;

let stableChecks = 0;


/* =========================================
   CREATE SONGS
========================================= */

function makeSongs() {

    return SONG_NAMES.map(
        name => ({

            name,

            rating: 1500,

            comparisons: 0,

            wins: 0,

            losses: 0

        })
    );

}


/* =========================================
   ELO
========================================= */

function expectedScore(
    ratingA,
    ratingB
) {

    return 1 /
        (
            1 +
            Math.pow(
                10,
                (
                    ratingB -
                    ratingA
                ) / 400
            )
        );

}


function updateRatings(
    winner,
    loser
) {

    const expectedWinner =
        expectedScore(
            winner.rating,
            loser.rating
        );


    const expectedLoser =
        expectedScore(
            loser.rating,
            winner.rating
        );


    winner.rating +=
        K_FACTOR *
        (
            1 -
            expectedWinner
        );


    loser.rating +=
        K_FACTOR *
        (
            0 -
            expectedLoser
        );


    winner.comparisons++;

    loser.comparisons++;

    winner.wins++;

    loser.losses++;

}


/* =========================================
   RANKING
========================================= */

function getRanking() {

    return [...songs].sort(
        (a, b) =>
            b.rating -
            a.rating
    );

}


/* =========================================
   PAIR KEY
========================================= */

function pairKey(
    a,
    b
) {

    return [
        a.name,
        b.name
    ]
    .sort()
    .join("|||");

}


/* =========================================
   CHOOSE MATCHUP
========================================= */

function choosePair() {

    const ranking =
        getRanking();


    const possiblePairs = [];


    for (
        let i = 0;
        i < ranking.length;
        i++
    ) {

        for (
            let j = i + 1;
        j < ranking.length;
        j++
        ) {

            const x =
                ranking[i];

            const y =
                ranking[j];


            const pair =
                pairKey(
                    x,
                    y
                );


            /*
             * Never repeat a matchup.
             */
            if (
                comparedPairs.has(
                    pair
                )
            ) {

                continue;

            }


            const ratingDifference =
                Math.abs(
                    x.rating -
                    y.rating
                );


            /*
             * Smaller rating differences
             * are more useful.
             */
            const usefulness =
                1 /
                (
                    1 +
                    ratingDifference
                );


            possiblePairs.push({

                usefulness,

                x,

                y

            });

        }

    }


    if (
        possiblePairs.length === 0
    ) {

        return [
            null,
            null
        ];

    }


    /*
     * Sort from most useful to least useful.
     */
    possiblePairs.sort(
        (a, b) =>
            b.usefulness -
            a.usefulness
    );


    /*
     * Choose randomly from the 20 most
     * useful available matchups.
     *
     * This prevents the same exact sequence
     * every time.
     */
    const topChoices =
        possiblePairs.slice(
            0,
            Math.min(
                20,
                possiblePairs.length
            )
        );


    const chosen =
        topChoices[
            Math.floor(
                Math.random() *
                topChoices.length
            )
        ];


    return [
        chosen.x,
        chosen.y
    ];

}


/* =========================================
   MINIMUM COMPARISON CHECK
========================================= */

function everySongHasEnoughComparisons() {

    for (
        const song of songs
    ) {

        if (
            song.comparisons <
            MIN_SONG_COMPARISONS
        ) {

            return false;

        }

    }


    return true;

}


/* =========================================
   RANKING ORDER
========================================= */

function getRankingOrder() {

    return getRanking().map(
        song => song.name
    );

}


/* =========================================
   RANKING MOVEMENT
========================================= */

function rankingPositionChange(
    oldRanking,
    newRanking
) {

    if (!oldRanking) {

        return Infinity;

    }


    let totalChange = 0;


    for (
        let i = 0;
        i < newRanking.length;
        i++
    ) {

        const song =
            newRanking[i];


        const oldPosition =
            oldRanking.indexOf(
                song
            );


        const newPosition =
            i;


        totalChange +=
            Math.abs(
                oldPosition -
                newPosition
            );

    }


    return totalChange;

}


/* =========================================
   STABILITY CHECK
========================================= */

function rankingIsStable() {

    const currentRanking =
        getRankingOrder();


    /*
     * First check establishes the baseline.
     */
    if (!previousRanking) {

        previousRanking =
            currentRanking;

        stableChecks = 0;

        return false;

    }


    const positionChange =
        rankingPositionChange(
            previousRanking,
            currentRanking
        );


    /*
     * Ranking has moved only a moderate
     * amount.
     */
    if (
        positionChange <=
        MAX_POSITION_CHANGE
    ) {

        stableChecks++;

    }

    else {

        stableChecks = 0;

    }


    previousRanking =
        currentRanking;


    return (
        stableChecks >=
        STABILITY_CHECKS
    );

}


/* =========================================
   STOP CHECK
========================================= */

function shouldStop() {

    /*
     * Never finish before the minimum.
     */
    if (
        comparisonNumber <
        MIN_COMPARISONS
    ) {

        return false;

    }


    /*
     * Always finish at the hard maximum.
     */
    if (
        comparisonNumber >=
        MAX_COMPARISONS
    ) {

        return true;

    }


    /*
     * Every song needs enough exposure.
     */
    if (
        !everySongHasEnoughComparisons()
    ) {

        return false;

    }


    /*
     * Only check stability every
     * STABILITY_INTERVAL comparisons.
     */
    if (
        comparisonNumber %
        STABILITY_INTERVAL !==
        0
    ) {

        return false;

    }


    const stable =
        rankingIsStable();


    /*
     * If the ranking is not reasonably
     * stable, keep going.
     */
    if (!stable) {

        return false;

    }


    /* =====================================
       90-135 RANGE
    ===================================== */

    /*
     * Between 90 and 135 comparisons,
     * stable rankings have a 65% chance
     * of finishing.
     *
     * Otherwise the game continues.
     */
    if (
        comparisonNumber <
        SOFT_FINISH_POINT
    ) {

        return (
            Math.random() <
            EARLY_FINISH_CHANCE
        );

    }


    /* =====================================
       135-165 RANGE
    ===================================== */

    /*
     * After 135 comparisons, make finishing
     * increasingly likely.
     */
    if (
        comparisonNumber <
        STRONG_FINISH_POINT
    ) {

        const progress =
            (
                comparisonNumber -
                SOFT_FINISH_POINT
            ) /
            (
                STRONG_FINISH_POINT -
                SOFT_FINISH_POINT
            );


        /*
         * Probability rises from 75%
         * to 100%.
         */
        const finishChance =
            0.75 +
            (
                progress *
                0.25
            );


        return (
            Math.random() <
            finishChance
        );

    }


    /*
     * At 165+, a stable ranking finishes.
     */
    return true;

}


/* =========================================
   IMAGE
========================================= */

function setCard(
    prefix,
    song
) {

    const image =
        document.getElementById(
            "image" + prefix
        );


    image.src =
        "Images/" +
        IMAGE_FILES[
            song.name
        ];


    image.alt =
        song.name;


    image.onerror =
        function () {

            this.src =
                createPlaceholder(
                    song.name
                );

        };


    document.getElementById(
        "name" + prefix
    ).textContent =
        song.name;


    document.getElementById(
        "rating" + prefix
    ).textContent =
        `⭐ ${Math.round(song.rating)} Rating`;


    document.getElementById(
        "record" + prefix
    ).textContent =

        `${song.wins} wins • ` +
        `${song.losses} losses • ` +
        `${song.comparisons} comparisons`;

}


/* =========================================
   PLACEHOLDER
========================================= */

function createPlaceholder(
    name
) {

    const svg = `

        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="300"
            height="300"
        >

            <rect
                width="100%"
                height="100%"
                fill="#242832"
            />

            <text
                x="50%"
                y="45%"
                fill="white"
                font-family="Arial"
                font-size="18"
                text-anchor="middle"
            >
                NO IMAGE
            </text>

            <text
                x="50%"
                y="57%"
                fill="#9ca3af"
                font-family="Arial"
                font-size="14"
                text-anchor="middle"
            >
                ${name}
            </text>

        </svg>

    `;


    return (
        "data:image/svg+xml;charset=UTF-8," +
        encodeURIComponent(svg)
    );

}


/* =========================================
   UPDATE STATS
========================================= */

function updateStats() {

    document.getElementById(
        "comparison"
    ).textContent =
        `Comparisons: ${comparisonNumber}`;


    document.getElementById(
        "minimum"
    ).textContent =
        `Minimum: ${MIN_COMPARISONS}`;


    document.getElementById(
        "maximum"
    ).textContent =
        `Maximum: ${MAX_COMPARISONS}`;


    const percentage =
        (
            comparisonNumber /
            MAX_COMPARISONS
        ) *
        100;


    document.getElementById(
        "progress"
    ).style.width =
        `${percentage}%`;

}


/* =========================================
   NEXT MATCHUP
========================================= */

function nextMatchup() {

    const [
        x,
        y
    ] =
        choosePair();


    if (
        !x ||
        !y
    ) {

        finishRanking();

        return;

    }


    songA = x;

    songB = y;


    comparedPairs.add(
        pairKey(
            x,
            y
        )
    );


    setCard(
        "A",
        x
    );


    setCard(
        "B",
        y
    );


    document.getElementById(
        "nextLabel"
    ).textContent =
        "Click the song you prefer";


    document.getElementById(
        "status"
    ).textContent =
        `Comparison #${comparisonNumber + 1}`;

}


/* =========================================
   SELECT SONG
========================================= */

function selectSong(
    winner
) {

    if (finished) {

        return;

    }


    const loser =
        winner === songA
            ? songB
            : songA;


    updateRatings(
        winner,
        loser
    );


    comparisonNumber++;


    updateStats();


    if (
        shouldStop()
    ) {

        finishRanking();

        return;

    }


    nextMatchup();

}


/* =========================================
   FINISH
========================================= */

function finishRanking() {

    if (finished) {

        return;

    }


    finished = true;


    document.getElementById(
        "status"
    ).textContent =
        "🏆 Ranking Complete!";


    document.getElementById(
        "status"
    ).style.color =
        "var(--green)";


    document.getElementById(
        "nextLabel"
    ).textContent =
        `Finished after ${comparisonNumber} comparisons`;


    updateStats();


    setTimeout(
        showRanking,
        200
    );

}


/* =========================================
   SHOW RANKINGS
========================================= */

function showRanking() {

    const ranking =
        getRanking();


    document.getElementById(
        "rankingSubtitle"
    ).textContent =
        `${comparisonNumber} comparisons completed`;


    const podium =
        document.getElementById(
            "podium"
        );


    podium.innerHTML = "";


    const medals = [
        "🥇",
        "🥈",
        "🥉"
    ];


    for (
        let i = 0;
        i < 3;
        i++
    ) {

        if (
            !ranking[i]
        ) {

            continue;

        }


        const song =
            ranking[i];


        const card =
            document.createElement(
                "div"
            );


        card.className =
            "podium-card";


        card.innerHTML = `

            <div class="medal">
                ${medals[i]}
            </div>

            <img
                src="Images/${IMAGE_FILES[song.name]}"
                alt="${song.name}"
            >

            <h3>
                ${song.name}
            </h3>

            <div class="rating">
                ${Math.round(song.rating)} rating
            </div>

        `;


        podium.appendChild(
            card
        );

    }


    const table =
        document.getElementById(
            "rankingTable"
        );


    table.innerHTML = "";


    ranking.forEach(
        (song, index) => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${index + 1}
                </td>

                <td>
                    ${song.name}
                </td>

                <td>
                    ${Math.round(song.rating)}
                </td>

                <td>
                    ${song.wins}
                </td>

                <td>
                    ${song.losses}
                </td>

                <td>
                    ${song.comparisons}
                </td>

            `;


            table.appendChild(
                row
            );

        }
    );


    document.getElementById(
        "rankingModal"
    ).classList.remove(
        "hidden"
    );

}


/* =========================================
   RESTART
========================================= */

function restart() {

    songs =
        makeSongs();


    comparisonNumber =
        0;


    comparedPairs =
        new Set();


    songA =
        null;


    songB =
        null;


    finished =
        false;


    previousRanking =
        null;


    stableChecks =
        0;


    document.getElementById(
        "status"
    ).textContent =
        "Ranking in progress";


    document.getElementById(
        "status"
    ).style.color =
        "var(--accent)";


    document.getElementById(
        "nextLabel"
    ).textContent =
        "Choose your favorite";


    updateStats();


    nextMatchup();

}


/* =========================================
   BUTTONS
========================================= */

document.getElementById(
    "cardA"
).addEventListener(
    "click",
    () => selectSong(songA)
);


document.getElementById(
    "cardB"
).addEventListener(
    "click",
    () => selectSong(songB)
);


document.getElementById(
    "restart"
).addEventListener(
    "click",
    restart
);


document.getElementById(
    "rankings"
).addEventListener(
    "click",
    showRanking
);


document.getElementById(
    "closeModal"
).addEventListener(
    "click",
    () => {

        document.getElementById(
            "rankingModal"
        ).classList.add(
            "hidden"
        );

    }
);


/* =========================================
   START
========================================= */

restart();