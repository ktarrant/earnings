import urllib
import re
import pandas as pd
from bs4 import BeautifulSoup

url_root = "http://finviz.com"
url_query = "screener.ashx"
url_views = {
    "Overview": "111",
    
}
url_fields = {
    "v": {"name":"View", "default":"111"},
    "s": {"name":"Signal", "default":"ta_unusualvolume"},
    "f": {"name":"Filter", "default":"earningsdate_nextweek"},
    "o": {"name":"Order", "default":"-price"},
}

def get_screener_url(**kwargs):
    rv = urllib.parse.urljoin(url_root, url_query)
    params = []
    for key in url_fields:
        if url_fields[key]["name"] in kwargs:
            value = kwargs[url_fields[key]["name"]]
        elif "default" in url_fields[key]:
            value = url_fields[key]["default"]
        params += [ "{}={}".format(key, value) ]
    return rv + "?" + "&".join(params)

def _yield_td(trsoup):
    for td in trsoup.findAll('td'):
        yield td.text

def _yield_tr(tablesoup):
    first = True
    for tr in tablesoup.findAll('tr'):
        if first:
            first = False
            continue
        yield list(_yield_td(tr))

def get_screener_table(screener_url):
    with urllib.request.urlopen(screener_url) as webobj:
        soup = BeautifulSoup(webobj.read(), 'lxml')
        root_table = soup.find(id="screener-content").table
        subtables = root_table.findAll('table')
        data_table = subtables[2]
        firstRow = data_table.tr
        columns = [ re.sub('[\W_]+', '', td.text) for td in firstRow.findAll('td') ]
        df = pd.DataFrame(_yield_tr(data_table), columns=columns)
        return df

if __name__ == "__main__":
    url = get_screener_url()
    print(url)
    table = get_screener_table(url)
    print(table)
