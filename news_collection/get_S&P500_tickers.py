import bs4 as bs
import requests

def get_tickers():
    """
    Methods that scrapes Wikipedia page to retrieve the list of the S&P500 tickers

    :return: list
        List of the S&P500 tickers
    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find_all('table')[0]

    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip('\n')
        tickers.append(ticker)

    return tickers

if __name__ == "__main__":
    print(get_tickers())