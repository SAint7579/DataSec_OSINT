import streamlit as st
import time
import tweepy
import re
import altair as alt
from textblob import TextBlob
from collections import defaultdict, namedtuple
import pandas as pd
from datetime import datetime, timedelta

def generate_recent_dates(num_dates):
    today = datetime.today()
    recent_dates = [today - timedelta(days=i) for i in range(num_dates)]
    return recent_dates


COLOR_BLUE = "#1C83E1"
COLOR_CYAN = "#00C0F2"

st.set_page_config(page_icon="🐤", page_title="Twitter Sentiment Analyzer")

prev_time = [time.time()]

a, b = st.columns([1, 10])

st.title("Tweet Analyzer")

st.write("Type in a term to view the analysis on the tweets pertaining to the topic.")

with st.expander("ℹ️ How to interpret the results", expanded=False):
    st.write(
        """
        **Polarity**: Polarity is a float which lies in the range of [-1,1] where 1 means positive statement and -1 means a negative statement
        **Subjectivity**: Subjective sentences generally refer to personal opinion, emotion or judgment whereas objective refers to factual information. Subjectivity is also a float which lies in the range of [0,1].
        And make sure to 👆 click on datapoints above to see the actual tweet!
        """
    )
    st.write("")

TWEET_CRAP_RE = re.compile(r"\bRT\b", re.IGNORECASE)
URL_RE = re.compile(r"(^|\W)https?://[\w./&%]+\b", re.IGNORECASE)
PURE_NUMBERS_RE = re.compile(r"(^|\W)\$?[0-9]+\%?", re.IGNORECASE)
EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002500-\U00002BEF"  # chinese char
    "\U00002702-\U000027B0"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"  # dingbats
    "\u3030"
    "]+",
    re.UNICODE,
)
OTHER_REMOVALS_RE = re.compile("[" "\u2026" "]+", re.UNICODE)  # Ellipsis
SHORTHAND_STOPWORDS_RE = re.compile(
    r"(?:^|\b)("
    "w|w/|"  # Short for "with"
    "bc|b/c|"  # Short for "because"
    "wo|w/o"  # Short for "without"
    r")(?:\b|$)",
    re.IGNORECASE,
)
AT_MENTION_RE = re.compile(r"(^|\W)@\w+\b", re.IGNORECASE)
HASH_TAG_RE = re.compile(r"(^|\W)#\w+\b", re.IGNORECASE)
PREFIX_CHAR_RE = re.compile(r"(^|\W)[#@]", re.IGNORECASE)

def clean_tweet_text(text):
    regexes = [
        EMOJI_RE,
        PREFIX_CHAR_RE,
        PURE_NUMBERS_RE,
        TWEET_CRAP_RE,
        OTHER_REMOVALS_RE,
        SHORTHAND_STOPWORDS_RE,
        URL_RE,
    ]

    for regex in regexes:
        text = regex.sub("", text)
    return text

tweets = ["Just going to cry myself to sleep after watching Marley and Me.", 
          "I hate when I have to call and wake people up",
          "this week is not going as i had hoped",
          "I just re-pierced my ears",
          "Emily will be glad when Mommy is done training at her new job."
        ]

st.write("")

def get_tweet_analysis(tweet): 
        analysis = TextBlob(clean_tweet_text(tweet)) 
        return analysis.sentiment.polarity, analysis.sentiment.subjectivity, analysis.word_counts, analysis.ngrams(2), analysis.ngrams(3)


with st.form(key="my_form"):
    def process_tweets(tweets):
        word_count_dict = defaultdict(int)
        bigram_count_dict = defaultdict(int)
        trigram_count_dict = defaultdict(int)
        SentimentListItem = namedtuple(
                "SentimentListItem", ("date", "polarity", "subjectivity", "text")
            )
        
        sentiment_list = []

        recent_dates = generate_recent_dates(5)
        
        for date, tweet in zip(recent_dates,tweets):
                
                date = date.strftime("%Y-%m-%d")
                polarity, subjectivity, word_counts, bigrams, trigrams = get_tweet_analysis(tweet)

                add_counts(word_count_dict, word_counts)
                add_counts(bigram_count_dict, get_counts(bigrams, key_sep=" "))
                add_counts(trigram_count_dict, get_counts(trigrams, key_sep=" "))

                sentiment_list.append(
                    SentimentListItem(
                        date,
                        polarity,
                        subjectivity,
                        tweet
                    )
                )

        def to_df(the_dict):
                items = the_dict.items()
                items = ((term, count, len(term.split(" "))) for (term, count) in items)
                return pd.DataFrame(items, columns=("term", "count", "num_words"))

        return {
                "word_counts": to_df(word_count_dict),
                "bigram_counts": to_df(bigram_count_dict),
                "trigram_counts": to_df(trigram_count_dict),
                "sentiment_list": sentiment_list,
            }

    def add_counts(accumulator, ngrams):
            for ngram, count in ngrams.items():
                accumulator[ngram] += count

    def get_counts(blobfield, key_sep):
        return {key_sep.join(x): blobfield.count(x) for x in blobfield}

    relative_dates = {
            "1 day ago": 1,
            "1 week ago": 7,
            "2 weeks ago": 14,
            "1 month ago": 30,
        }

    search_params = {}

    a, b = st.columns([1, 1])
    search_params["query_terms"] = a.text_input("User Id", "streamlit")
    search_params["limit"] = b.slider("Tweet limit", 1, 1000, 100)

    a, b, c, d = st.columns([1, 1, 1, 1])
    search_params["min_replies"] = a.number_input("Minimum replies", 0, None, 0)
    search_params["min_retweets"] = b.number_input("Minimum retweets", 0, None, 0)
    search_params["min_faves"] = c.number_input("Minimum hearts", 0, None, 0)
    selected_rel_date = d.selectbox("Search from date", list(relative_dates.keys()), 3)
    search_params["days_ago"] = relative_dates[selected_rel_date]

    a, b, c  = st.columns([1, 2, 1])
    search_params["exclude_replies"] = a.checkbox("Exclude replies", False)
    search_params["exclude_retweets"] = b.checkbox("Exclude retweets", False)

    if not search_params["query_terms"]:
        st.stop()

    submit_button = st.form_submit_button(label="Submit")


results = process_tweets(tweets)

sentiment_df = pd.DataFrame(results["sentiment_list"])


st.markdown("## Top terms")

terms = pd.concat(
    [
        results["word_counts"],
        results["bigram_counts"],
        results["trigram_counts"],
    ]
)

a, b = st.columns(2)
adjustment_factor = a.slider("Prioritize long expressions", 0.0, 1.0, 0.2, 0.001)
# Default value picked heuristically.

max_threshold = terms["count"].max()
threshold = b.slider("Threshold", 0.0, 1.0, 0.3) * max_threshold
# Default value picked heuristically.

weights = (terms["num_words"] * adjustment_factor * (terms["count"] - 1)) + terms[
    "count"
]

filtered_terms = terms[weights > threshold]

st.altair_chart(
    alt.Chart(filtered_terms)
    .mark_bar(tooltip=True)
    .encode(
        x="count:Q",
        y=alt.Y("term:N", sort="-x"),
        color=alt.Color(value=COLOR_BLUE),
    ),
    use_container_width=True,
)


chart = alt.Chart(sentiment_df, title="Sentiment Subjectivity")

avg_subjectivity = chart.mark_line(interpolate="catmull-rom", tooltip=True,).encode(
    x=alt.X("date:T", timeUnit="yearmonthdate", title="date"),
    y=alt.Y(
        "mean(subjectivity):Q", title="subjectivity", scale=alt.Scale(domain=[0, 1])
    ),
    color=alt.Color(value=COLOR_CYAN),
)

subjectivity_values = chart.mark_point(size=75, filled=True,).encode(
    x=alt.X("date:T", timeUnit="yearmonthdate", title="date"),
    y=alt.Y("subjectivity:Q", title="subjectivity"),
    color=alt.Color(value=COLOR_CYAN + "88"),
    tooltip=alt.Tooltip(["date", "polarity", "text"])
)

st.altair_chart(avg_subjectivity + subjectivity_values, use_container_width=True)

chart = alt.Chart(sentiment_df, title="Sentiment Polarity")

avg_polarity = chart.mark_line(interpolate="catmull-rom", tooltip=True,).encode(
    x=alt.X("date:T", timeUnit="yearmonthdate", title="date"),
    y=alt.Y("mean(polarity):Q", title="polarity", scale=alt.Scale(domain=[-1, 1])),
    color=alt.Color(value=COLOR_CYAN),
)

polarity_values = chart.mark_point(size=75, filled=True,).encode(
    x=alt.X("date:T", timeUnit="yearmonthdate", title="date"),
    y=alt.Y("polarity:Q", title="polarity"),
    color=alt.Color(value=COLOR_BLUE + "88"),
    tooltip=alt.Tooltip(["date", "polarity", "text"])
)

st.altair_chart(avg_polarity + polarity_values, use_container_width=True)