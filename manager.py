from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd


def get_nfl_table(url="https://www.nfl.com/teams/new-york-jets/roster"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=50)
        page = browser.new_page()
        page.goto(url, timeout=0)
        html = page.inner_html('table')
        return html


def parse_nfl_info(html):
    players_stats = []

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    table_tr = soup.find_all('tr')

    # ['Player', 'No', 'Pos', 'Status', 'Height', 'Weight', 'Experience', 'College']
    col_name = [th.text.replace('\n', ' ').strip() for th in table_tr[0].find_all("th")]

    # Get all stats to list
    # [{'Player': 'Jabari Zuniga', 'No': '92', 'Pos': 'DE', 'Status': 'DEV', 'Height': '6-3',
    #   'Weight': '264', 'Experience': '2', 'College': 'Florida'}, ]
    
    for tr in table_tr[1:]:
        t_row = {}
        for td, th in zip(tr.find_all("td"), col_name):
            t_row[th] = td.text.replace('\n', '').strip()
        players_stats.append(t_row)
    
    return players_stats
        

if __name__ == "__main__":
    url = 'https://www.nfl.com/teams/baltimore-ravens/roster'
    html = get_nfl_table(url)
    players_stats = parse_nfl_info(html)
    # Converting to pandas df
    #               Player  No  Pos Status Height Weight Experience           College
    # 0        Zach Wilson   2   QB    ACT    6-2    214          R     Brigham Young
    # 1      Jarrod Wilson  39   DB    ACT    6-2    210          6          Michigan
    df = pd.DataFrame(players_stats)
    print(df)

    # write players by pos to difference files
    csv_path = 'players_no_pos_{pos}.csv'
    for pos in ['QB', 'DB', 'WR']:
        df[df['Pos'] == pos].to_csv(csv_path.format(pos=pos), mode='w', columns=['Player', 'No'], index=False)
