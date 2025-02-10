TASK_RUNNING = "task is running"
TASK_COMPLETED = "task completed"
ANALYZE_RESULT_KEY = "analyze result key"
DATE_FORMAT = "%Y-%m-%d"
CURRENCY_TYPES = ['USD', 'NIS', 'EUR']
CURRENCY_SYMBOLS = ['$', '₪', '€']
CURRENCY_COLORS = ['green', 'blue', 'orange']
CURRENCY_NAMES = ['dollar', 'shekel', 'euro']
CURRENCY = "currency"
FINANCE = "finance"
INVESTED = "invested"
INVESTED_NUM = "invested_num"
ACTIVE = "active"
VALUE = "value"
VALUE_NUM = "value_num"
NAME = "name"
PROFIT_ITD = "ITD"
PROFIT_YTD = "YTD"
DESCRIPTION = "description"
COMMITMENT = "commitment"
COMMITMENT_CURRENCY = COMMITMENT + "_currency"
MISSING = "missing"
UNFUNDED = "unfunded"
UNFUNDED_CURRENCY = UNFUNDED + "_currency"
UNFUNDED_NUM = "unfunded_num"
DIST_ITD = "Dist_ITD"
DIST_YTD = "Dist_YTD"
EVENTS = "events"
TYPE = "type"
DATE = "date"
ROI = "roi"
NET_GAIN = 'net_gain'
YTDP = "ytdp"
ITDP = "itdp"
IRR = "irr"
XIRR = "xirr"
MONTHS = "months"
YEARS = "years"
COUNT = "count"

TASKS = "tasks"
TODO = "TODO"
INVESTMENT_WATCHER_TYPES = ["Investment"]
OTHER_WATCHER_TYPES = ["Task", "Birthday"]
WATCHER_TYPES = INVESTMENT_WATCHER_TYPES + OTHER_WATCHER_TYPES
STATEMENT_EVENT_TYPE = "Statement"
DISTRIBUTION_EVENT_TYPE = "Distribution"
WIRE_RECEIPT_EVENT_TYPE = "Wire Receipt"
COMMITMENT_EVENT_TYPE = "Commitment"
INVESTMENT_EVENT_TYPES_MUST_HAVE = [STATEMENT_EVENT_TYPE,
                                    WIRE_RECEIPT_EVENT_TYPE,
                                    COMMITMENT_EVENT_TYPE]
INVESTMENT_EVENT_TYPES = INVESTMENT_EVENT_TYPES_MUST_HAVE + \
    [DISTRIBUTION_EVENT_TYPE]
