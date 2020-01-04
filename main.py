import requests
from bs4 import BeautifulSoup
from re import sub as resub, findall as refindall
import os
import sys
from PIL import Image
def combine_url(url):
    root_url = 'https://mangacanblog.com/'
    output_url = root_url + url
    return output_url


def visit_url(url):
    response = None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            response = response.text

    except Exception as e:
        raise e

    return response


def visit_onepiece_web():
    url = combine_url(
        "baca-komik-one_piece-bahasa-indonesia-online-terbaru.html")
    source = visit_url(url)
    return source


def visit_latest_ep():
    source_web = visit_onepiece_web()
    if not source_web:
        return None
    bs_source = BeautifulSoup(source_web, 'html.parser')

    row_latest_ep = bs_source.find(class_='c3')
    latest_release = row_latest_ep.find(class_="c2").string
    latest_url = row_latest_ep.find(class_='chaptersrec')['href']
    latest_url = resub(r"(.*?)-\d+(\.html)$", r"\1\2", latest_url)
    latest_url = combine_url(latest_url)
    title_ep = row_latest_ep.find(class_='chaptersrec').get_text()
    source = visit_url(latest_url)
    return source, latest_release, title_ep


def get_title(source_web):
    bs_source = BeautifulSoup(source_web, 'html.parser')
    title = bs_source.title.string
    title = title.split("-")[0].strip()
    return title


def get_url_images(source_web):
    bs_source = BeautifulSoup(source_web, 'html.parser')
    images_group = bs_source.find_all(class_="picture")
    images_url = [x['src'] for x in images_group]
    return images_url


def save_images(dirname, urls):
    dirname = resub(r"[:\?<>\"\//|\*]","-",dirname)
    dirname = dirname.strip()
    try:
        os.mkdir(dirname)

    except Exception as e:

        print("direktori telah ada")
        loop = True
        while loop:
            opsi = input("apakah ingin melanjutkan ? (Y/N) : ")
            opsi = opsi.lower()
            print("")
            if opsi == "n":
                print("")
                print("##########")
                print("dibatalkan")
                print("##########")
                return None
            if opsi == "y":
                loop = False

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname)
    for x in range(len(urls)):
        image_file = requests.get(urls[x], stream=True)
        image_header = image_file.headers['content-disposition']
        image_name = refindall(r"filename=\"(.+)\"", image_header)[0]
        fullpath = os.path.join(path, image_name)
        if os.path.isfile(fullpath):
            continue

        with open(fullpath, "wb") as ff:
            ff.write(image_file.content)
            print("#" * 50)
            print('menyimpan -> {}'.format(image_name))
            print("#" * 50)
        print("")

def save_images_as_pdf(pdfname, urls):

    pdfname = resub(r"[:\?<>\"\//|\*]","-",pdfname)
    pdfname = pdfname.strip()
    pdfname = pdfname+".pdf"
    dirname = "CHAPTERS"

    try:
        os.mkdir(dirname)
    except Exception as e:
        pass
    fullpdfname = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[dirname,pdfname])
    if os.path.isfile(fullpdfname):
        loop = True
        while loop:
            dialog = input("File telah ada, ingin menimpa ? (Y/N) : ")
            dialog = dialog.lower()
            if dialog == "n":
                return fullpdfname
            if dialog == "y":
                loop = False

    list_images = []
    for x in range(len(urls)):
        image_file = requests.get(urls[x], stream=True)
        image_header = image_file.headers['content-disposition']
        image_name = refindall(r"filename=\"(.+)\"", image_header)[0]
        image_file.raw.decode_content = True
        im = Image.open(image_file.raw)
        list_images.append(im)
        print("processed image=> {}".format(image_name))

    saved_pdf = list_images[0].save(fullpdfname, "PDF",
        resolution=100.0,
        save_all=True,
        append_images=list_images[1:])

    return fullpdfname



def open_file_pdf(url):
    if os.name == 'nt':
        os.startfile(url)
    else:
        os.startfile("termux-open {}".format(url))

def opsi_latest_ep():
    source_web, latest_release, title_ep = visit_latest_ep()
    print("")
    print("#" * 50)
    print("{}, Release date: {}". format(title_ep, latest_release))
    print("#" * 50)
    print("")
    return source_web, latest_release, title_ep

def opsi_save_latest_ep():
    source_latest, date_release, title = opsi_latest_ep()
    if not source_latest:
        print("CEK INTERNET")
        return None
    source_title =title
    url_images = get_url_images(source_latest)
    fullpdfname = save_images_as_pdf(source_title, url_images)
    print("")
    open_file_dialog = input("Apakah ingin membaca file ? (Y/N) :").lower()
    if open_file_dialog == "y":
        open_file_pdf(fullpdfname)
    print("")
    print("#######")
    print("Selesai")
    print("#######")
    sys.exit()

def main():
    try:
        while True:
            print("")
            print("1. Check episode terakhir")
            print("2. Save episode terakhir")
            print("0. Exit")
            print("")

            opsi = input('Masukkan opsi : ')

            if opsi == "1":
                opsi_latest_ep()
            if opsi == "2":
                opsi_save_latest_ep()

            if opsi == "0":
                sys.exit()

    except KeyboardInterrupt:
        print("")
        print('Bye bye')

if __name__ == "__main__":
    main()
