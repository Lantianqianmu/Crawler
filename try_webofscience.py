import requests
import re
from bs4 import BeautifulSoup


def get_html(url):
    from_data = {
        'fieldCount': 1,
        'action': 'search',
        'product': 'UA',
        'search_mode': 'GeneralSearch',
        'SID': '8FMB6cLYD9SPsjcnRFx',
        'max_field_count': 25,
        'max_field_notice': '注意: 无法添加另一字段。',
        'input_invalid_notice': '检索错误: 请输入检索词。',
        'exp_notice': "检索错误: 专利检索词可以在多个家族中找到(",
        'input_invalid_notice_limits': "<br/> 注意: 滚动框中显示的字段必须至少与一个其他检索字段相组配。",
        'sa_params': "UA||8FMB6cLYD9SPsjcnRFx|http://apps.webofknowledge.com|'",
        'formUpdated': 'true',
        'value(input1)': 'Hepatocellular',    # input search keys
        'value(select1)': 'TS',
        'value(hidInput1)': '',
        'limitStatus': 'collapsed',
        'ss_lemmatization': 'On',
        'ss_spellchecking': 'Suggest',
        'SinceLastVisit_UTC': '',
        'SinceLastVisit_DATE': '',
        'period': 'Range Selection',
        'range': 'ALL',
        'startYear': '1900',
        'endYear': '2020',
        'update_back2search_link_param': 'yes',
        'ssStatus': 'display:none',
        'ss_showsuggestions': 'ON',
        'ss_query_language': 'auto',
        'ss_numDefaultGeneralSearchFields': 1,
        'rs_sort_by': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
    }
    headers = {
        "Host": "apps.webofknowledge.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://apps.webofknowledge.com",
        "Referer": "http://apps.webofknowledge.com/UA_GeneralSearch_input.do?"
                   "product=UA&search_mode=GeneralSearch&SID=8FMB6cLYD9SPsjcnRFx&preferencesSaved="

    }
    s = requests.Session()
    req = requests.Request('POST', url=url, data=from_data, headers=headers)
    prepped = s.prepare_request(req)
    r = s.send(prepped, timeout=20)
    r.encoding = r.apparent_encoding
    # print(r.status_code)
    return r.text


def get_html2(url):
    headers = {
        "Host": "apps.webofknowledge.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "keep-alive"

    }
    s = requests.Session()
    req = requests.Request('GET', url=url, headers=headers)
    prepped = s.prepare_request(req)
    r = s.send(prepped, timeout=20)
    r.encoding = r.apparent_encoding
    return r.text


def find_page_url(html):
    # find the tag that contains url which is needed for method "GET" to change page
    soup = BeautifulSoup(html, "html.parser")
    tag_url = soup.find_all(name='form', attrs={'id': 'summary_navigation'})[0]['onsubmit']
    # use re to find url for method "GET"
    pattern = re.compile(r'(http://.*?page=)', re.S)
    url = re.findall(pattern, tag_url)
    # return url as str format (instead of list format)
    return url[0]


def parse_html(html):
    name_pattern = re.compile(r'<value lang_id="">(.*?)</value>')
    name = re.findall(name_pattern, html)
    return name


def write_file(paper_list):
    with open('paper_name.txt', 'a', encoding='utf-8') as f:
        for item in paper_list:
            f.write(item + '\n')
    return None


def main(max_page=1):
    base_url = "http://apps.webofknowledge.com/UA_GeneralSearch.do"
    # set search parameters
    '''
    params = {
        'product': 'UA',
        'search_mode': 'GeneralSearch',
        'SID': '8FMB6cLYD9SPsjcnRFx',
        'preferencesSaved': ''
    }
    '''
    url = base_url    # + parse.urlencode(params)

    if __name__ == "__main__":
        try:
            # page 1
            html = get_html(url)
            name = parse_html(html)
            write_file(name)
            # page 2 ~ max_page
            if max_page > 1 and type(max_page) == int:
                for i in range(2, max_page+1):
                    url = find_page_url(html) + str(i)
                    html = get_html2(url)
                    name = parse_html(html)
                    write_file(name)
            elif not type(max_page) == int:
                print('input an integer as the max page number')
            elif max_page < 1:
                print('input an integer >= 1')
            else:
                pass
        except requests.exceptions.BaseHTTPError as e:
            print(e)
    return None


main(max_page=1)
