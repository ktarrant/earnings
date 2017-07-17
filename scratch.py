from bs4 import BeautifulSoup
import urllib
import pandas as pd

url = "http://finviz.com/screener.ashx?v=150&f=earningsdate_tomorrowbefore,geo_usa,sh_avgvol_o1000&ft=4&o=-volume"

def generate_results(url):
    with urllib.request.urlopen(url) as webobj:
        soup = BeautifulSoup(webobj.read())
        content = soup.find('div', {'id': 'screener-content'})
        subtable = content.find('table')
        subrows = subtable.findAll('tr', recursive=False)
        contentrow = subrows[3]
        contenttable = contentrow.find('table')
        contentrows = contenttable.findAll('tr')
        headers = [td.text for td in contentrows[0].findAll('td')]
        for contentrow in contentrows[1:]:
            values = [td.text for td in contentrow.findAll('td')]
            yield {header: value for header, value in zip(headers, values)}


if __name__ == "__main__":
    df = pd.DataFrame(generate_results(url))
    print(df)
    df.to_csv('results.csv')