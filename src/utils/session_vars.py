from datetime import time

SYDNEY_SESSION_LABEL = "Sydney"
TOKYO_SESSION_LABEL = "Tokyo"
LONDON_SESSION_LABEL = "London"
NEW_YORK_SESSION_LABEL = "New York"

TRADE_SESSION_FORMAT_RULES = {
    SYDNEY_SESSION_LABEL: '<span class="tag-session-syd">SYD</span>',
    TOKYO_SESSION_LABEL: '<span class="tag-session-asia">TOK</span>',
    LONDON_SESSION_LABEL: '<span class="tag-session-ldn">LDN</span>',
    NEW_YORK_SESSION_LABEL: '<span class="tag-session-ny">NY</span>',
}

# TODO automatic check for season time changes
TRADE_SESSION_TIMEZONES = sessions = {
    # actual ? sydney 10 pm to 7 am
    "Sydney": (time(22, 0), time(8, 0)),
    # actual ? tokyo 12 am to 9 am
    "Tokyo": (time(0, 0), time(8, 0)),
    # actual ? london 8 am to 5 pm
    "London": (time(8, 0), time(17, 0)),
    # actual ? new york 1 pm to 10 pm
    "New York": (time(14, 30), time(20, 0)),
}
