GROUP = "https://www.facebook.com/groups/silvereaglebus/"  # id, name or URL of the group
USERNAME = ""
PASSWORD = ""
# 100015358482050 
#100007065700918
#100001035187911
FILTER_AUTHOR_ID = "1035187911"  # last digits in URL. Example: https://facebook.com/groups/1111111/user/2222222
FILTER_AUTHOR_NAME = ""  # Not used if author id filter is not empty. Case insensitive
FILTER_DATE_AFTER = "2022.05.14 00:00"  # YYYY.MM.DD hh:mm
FILTER_DATE_BEFORE = "2022.05.17 00:00"
FILTER_KEYWORDS = ""  # comma separated keywords
FILTER_KEYWORDS_MODE = "OR"  # "AND" - all of the keywords should be in the post. "OR" - any of the listed keywords
# Any of the filters can be left blank ("")
DELAY_MIN = 2  # Delay after each processed post in seconds
DELAY_MAX = 10
HIGH_RES_IMAGES = True  # Fetch higher quality image links. Uses additional request per post, so longer delays may be needed when set to True
DOWNLOAD_IMAGES = True
DOWNLOAD_VIDEOS = True
TIMEZONE = 'Etc/GMT-5'  # Time zone used in date/time calculations. POSIX style (sign reversed)
COOKIE_DIR = 'cookies'  # relative or absolute path to directory with cookie files
