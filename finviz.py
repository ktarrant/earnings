import urllib
import re
from collections import OrderedDict
import pandas as pd
from bs4 import BeautifulSoup

url_root = "http://finviz.com"
url_query = "screener.ashx"

column_options = OrderedDict([
    ("No.", 0),
    ("Ticker", 1),
    ("Company", 2),
    ("Sector", 3),
    ("Industry", 4),
    ("Country", 5),
    ("Market Cap", 6),
    ("P/E", 7),
    ("EPS", 16),
    ("EPS this Y", 17),
    ("Float Short", 30),
    ("Avg Volume", 63),
    ("Price", 65),
    ("Volume", 67),
    ("Earnings", 68),
])

filter_options = [
    "cap_smallover",
    "earningsdate_todayafter",
    "earningsdate_tomorrowbefore",
    "earningsdate_nextweek",
    "earningsdate_thisweek",
    "geo_usa",
]

url_fields = OrderedDict([
    ("v", {"name":"view", "default":"150"}),
    ("f", {"name":"filter", "default": ["cap_smallover", "earningsdate_todayafter", "geo_usa"]}),
    ("o", {"name":"order", "default":"-volume"}),
    ("c", {"name":"columns", "default": [key for key in column_options]})
])

def get_screener_url(**kwargs):
    rv = urllib.parse.urljoin(url_root, url_query)
    params = []
    for key in url_fields:
        if url_fields[key]["name"] in kwargs:
            value = kwargs[url_fields[key]["name"]]
        elif "default" in url_fields[key]:
            value = url_fields[key]["default"]
        else:
            raise KeyError("'{}' not provided in arguments and no default available".format(key))
        if key == "f":
            value = ",".join(value)
        elif key == "c":
            value = ",".join([str(column_options[colkey]) for colkey in value])
        params += [ "{}={}".format(key, value) ]
    return rv + "?" + "&".join(params)

def get_screener_earnings_url(earningsdate="earningsdate_todayafter"):
    f = ["cap_smallover", earningsdate, "geo_usa"]
    return get_screener_url(filter=f)

def _yield_contentrows(contenttable):
    contentrows = contenttable.findAll('tr')
    headers = [td.text for td in contentrows[0].findAll('td', recursive=False)]
    print(headers)
    for contentrow in contentrows[1:]:
        values = [td.text for td in contentrow.findAll('td')]
        yield OrderedDict([(header, value) for header, value in zip(headers, values)])

def get_screener_table(screener_url):
    with urllib.request.urlopen(screener_url) as webobj:
        soup = BeautifulSoup(webobj.read(), "html.parser")
        content = soup.find('div', {'id': 'screener-content'})
        subtable = content.find('table')
        subrows = subtable.findAll('tr', recursive=False)
        contentrow = subrows[3]
        contenttable = contentrow.find('table')
        return pd.DataFrame(_yield_contentrows(contenttable))

if __name__ == "__main__":
    after_url = get_screener_earnings_url()
    before_url = get_screener_earnings_url("earningsdate_tomorrowbefore")

    after_table = get_screener_table(after_url)
    before_table = get_screener_table(before_url)
    table = pd.concat([after_table, before_table])
    print(table)

    table.to_csv('results.csv')