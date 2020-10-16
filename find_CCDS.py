import requests
import re
import queue
import threading
from bs4 import BeautifulSoup


lock_list = list()
num = None


class GeneCrawler:

    def __init__(self, name, species="Homo sapiens", accession=None):
        self.name = name
        self.species = species
        self.accession = accession
        self.CCDS_url = None
        self.current_accession = None
        self.ID = None

    def find_gene_id(self):
        """
        This function is used to find the ID of the gene, callable
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }
        url_gene = "https://www.ncbi.nlm.nih.gov/gene/?term=" + self.name
        s = requests.Session()
        req = requests.Request('GET', url=url_gene, headers=headers)
        prepped = s.prepare_request(req)
        r = s.send(prepped, timeout=20)
        if r.status_code == requests.codes.ok:
            html_gene = r.text
            id_pattern = re.compile(r'<span class="gene-id">ID: (\d+).*?<em>(.*?)</em>', re.S|re.I)
            gene_id = re.findall(id_pattern, html_gene)
            for match in gene_id:
                if match[1] == self.species:
                    self.ID = match[0]
                    return match[0]
                else:
                    pass
            else:
                print(self.name + ": Can not find the correct gene ID")
        else:
            print('status_code = {}'.format(r.status_code))
            pass

    def _find_gene_id(self, html_gene):
        """
        This function is used to find the ID of the gene
        """
        id_pattern = re.compile(r'<span class="gene-id">ID: (\d+).*?<em>(.*?)</em>', re.S|re.I)
        gene_id = re.findall(id_pattern, html_gene)
        for match in gene_id:
            if match[1] == self.species:
                self.ID = match[0]
                return match[0]
            else:
                pass
        else:
            print(self.name + ": Can not find the correct gene ID")

    def find_gene_url(self):
        """
        This function returns the url of target gene in the gene database
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }
        url_gene = "https://www.ncbi.nlm.nih.gov/gene/?term=" + self.name
        s = requests.Session()
        req = requests.Request('GET', url=url_gene, headers=headers)
        prepped = s.prepare_request(req)
        r = s.send(prepped, timeout=20)
        if r.status_code == requests.codes.ok:
            # print(r.status_code)
            r.encoding = r.apparent_encoding
            html_gene = r.text
            gene_id = self._find_gene_id(html_gene)
            new_url = "https://www.ncbi.nlm.nih.gov/gene/" + gene_id
            return new_url
        else:
            print('status_code = {}'.format(r.status_code))
            pass

    def _parse_gene_html(self, id_html):
        """
        This function returns the url of CCDS
        """
        CCDS_base_url = "https://www.ncbi.nlm.nih.gov/CCDS/CcdsBrowse.cgi?REQUEST=CCDS&GO=MainBrowse&DATA="
        pattern = re.compile(r'CCDS(.*?)', re.S)
        accession_num = self.get_accession()
        soup = BeautifulSoup(id_html, "html.parser")
        new_accession = soup.find_all(text=re.compile(accession_num))[0]
        # print(soup.find_all(text=re.compile(accession_num)))
        self.current_accession = new_accession
        for item in soup.find_all(name="ol", attrs={"class": ""}):
            if new_accession in item.text:
                for li in item.find_all(name="li"):
                    if new_accession in li.text:
                        if not li.find(text=pattern):
                            print(self.name + ": Can not find CCDS in this accession")
                        else:
                            self.CCDS_url = CCDS_base_url + li.find(text=pattern)
                            return self.CCDS_url
                    else:
                        pass
            else:
                pass
        print("An error has occurred in function '_parse_gene_html'")
        return None

    def find_mRNA_url(self, url):
        """
        This function inputs gene url and returns CCDS url
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }
        s = requests.Session()
        req = requests.Request('GET', url=url, headers=headers)
        prepped = s.prepare_request(req)
        r = s.send(prepped, timeout=20)
        r.encoding = r.apparent_encoding
        id_html = r.text
        if not id_html:
            print("Can not get url of the specific gene page")
        else:
            pass
        m_url = self._parse_gene_html(id_html)
        return m_url

    def get_sequence(self, url):
        """
        This function returns the CCDS list
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }
        s = requests.Session()
        req = requests.Request('GET', url=url, headers=headers)
        prepped = s.prepare_request(req)
        r = s.send(prepped, timeout=20)
        r.encoding = r.apparent_encoding
        html = r.text
        nt_list = self.parse_html(html)
        return nt_list

    def parse_html(self, html):
        """
        This function parses the CCDS page and finds the CCDS contents in the CCDS page
        """
        nt_pattern = re.compile(r'<font color=([a-z]*?|#0089cc)>([A-Z]*?|[A-Z]*?<br>[A-Z]*?)</font>', re.S)
        codon = re.findall(nt_pattern, html)
        nt_list = self.decode_gene(codon)
        return nt_list

    @ staticmethod
    def decode_gene(codon):
        """
        This function decodes the CCDS contents
        """
        nt_list = list()
        new_list = list()
        for item in range(len(codon)):
            if codon[item][0] == 'black':
                nt_list.append(codon[item][1])
            elif codon[item][0] == '#0089cc':
                nt_list.append(str.lower(codon[item][1]))
            else:
                pass
        for string in nt_list:
            new_list.append(string.replace('<br>', ''))
        return new_list

    def write_gene(self, nt_list):
        """
        This function writes decoded gene sequence into 'panel.txt'
        """
        with open('panel.txt', mode='a', encoding='utf-8') as f:
            f.write('>' + self.name + '|' + self.current_accession + '\n')
            for nucleotide in nt_list:
                f.write(nucleotide)
            f.write('\n\n')
        return None

    def get_accession(self):
        """
        This function gets the accession number, from the first number to "."
        It omits the version of the sequence
        """
        str_list = list(self.accession)
        index = str_list.index(".")
        acce = str_list[0: index]
        return "".join(acce)


class MultiThread(threading.Thread):

    def __init__(self, thread_id, working_queue):
        super(MultiThread, self).__init__()
        self.queue = working_queue
        self.ID = thread_id

    def run(self):
        # print("开启线程", self.ID)
        if self.ID < num:
            thread_process(self.ID, self.queue, lock_list[self.ID-1], lock_list[self.ID])
        else:
            thread_process(self.ID, self.queue, lock_list[self.ID-1], lock_list[0])
        # print("结束线程", self.ID)


def thread_process(thread_id, gene_queue, lock1, lock2):
    while True:
        if not gene_queue.empty():
            gene = gene_queue.get()
            gene_crawler = GeneCrawler(gene["name"], accession=gene["accession"])
            try:
                gene_url = gene_crawler.find_gene_url()
                mRNA_url = gene_crawler.find_mRNA_url(gene_url)
                seq_list = gene_crawler.get_sequence(mRNA_url)
                lock1.acquire()
                gene_crawler.write_gene(seq_list)
                print("thread %s is processing %s" % (thread_id, gene_crawler.name))
                lock2.release()
            except Exception:
                print(gene_crawler.name + ": ERROR")
        else:
            break


def easy_find_seq(gene_to_find, threads_num=5):
    global num
    num = threads_num
    # create work queue
    work_queue = queue.Queue(len(gene_to_find))
    for gene_dict in gene_to_find:
        work_queue.put(gene_dict)
    # create locks
    global lock_list
    number = 0
    while number < threads_num:
        lock_list.append(threading.Lock())
        lock_list[number].acquire()
        number += 1
    lock_list[0].release()
    # create threads
    threads = list()
    thread_ID = 1
    for no_threads in range(threads_num):
        thread = MultiThread(thread_ID, work_queue)
        thread.start()
        threads.append(thread)
        thread_ID += 1
    # wait for the threads to finish
    for t in threads:
        t.join()
    print("\nJob done!")
    pass


if __name__ == "__main__":
    # generate gene list
    gene_list = [
        {"name": "AIM2", "accession": "NM_004833.1"},
        {"name": "ANXA5", "accession": "NM_001154.3"},
        {"name": "APOBEC3G", "accession": "NM_021822.3"},
        {"name": "ARL4C", "accession": "NM_005737.3"},
        {"name": "AURKB", "accession": "NM_004217.3"},
        {"name": "B3GAT1", "accession": "NM_018644.3"},
        {"name": "BAX", "accession": "NM_001291428.1"},
        {"name": "BCL11B", "accession": "NM_022898.2"},
        {"name": "BCL2", "accession": "NM_000633.2"},
        {"name": "BCL6", "accession": "NM_001706.4"},
        {"name": "BIN2", "accession": "NM_016293.3"},
        {"name": "BTG1", "accession": "NM_001731.2"},
        {"name": "BTLA", "accession": "NM_181780.3"},
        {"name": "C10orf54", "accession": "NM_022153.1"},
        {"name": "CASP3", "accession": "NM_004346.3"},
        {"name": "CBLB", "accession": "NM_170662.4"},
        {"name": "CCL1", "accession": "NM_002981.2"},
        {"name": "CCL2", "accession": "NM_002982.3"},
        {"name": "CCL20", "accession": "NM_004591.2"},
        {"name": "CCL3", "accession": "NM_002983.2"},
        {"name": "CTLA4", "accession": "NM_005214.4"}
    ]
    easy_find_seq(gene_list)
