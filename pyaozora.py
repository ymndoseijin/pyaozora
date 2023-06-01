from ebooklib import epub
import requests
import argparse
from bs4 import BeautifulSoup, Tag, NavigableString

allowed_tags = ["a", "div", "ruby", "rb", "rp", "rt", "p", "br", "em", "h4", "h3", "h2", "h1", "h", "span"]
def process_tag(tag):
    for i in tag.contents:
        if type(i) == Tag:
            if i.name in allowed_tags:
                process_tag(i)
            elif i.name != None:
                i.extract()

def sanitize_soup(soup):
    result = soup.html.body.find_all("div", "main_text")

    main = result[0]
    j = 0
    chapters=[]
    current_chapter = BeautifulSoup()
    chapter_name = None
    process_tag(main)
    kids = list(main.children).copy()
    for i in kids:
        if type(i) == Tag:
            chapter_result = i.find_all("a", "midashi_anchor")
            if len(chapter_result) != 0:
                if chapter_name:
                    chapters.append((chapter_name, current_chapter))
                    current_chapter = BeautifulSoup()
                chapter_name = chapter_result[0].string

        current_chapter.append(i)
        j+=1

    if chapter_name:
        chapters.append((chapter_name, current_chapter))
        current_chapter = BeautifulSoup()
    return chapters

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'pyaozora',
                    description = 'aozoraのXHTMLリンクからEPUB3に')

    parser.add_argument('url')
    parser.add_argument('--yokogaki', '-y', action="store_true", help="横書きにする")
    parser.add_argument('--tategaki', '-t', action="store_true", help="縦書きにする")
    parser.add_argument('--output', '-o', help="ファイルに出力")

    args = parser.parse_args()

    page = requests.get(args.url)

    soup = BeautifulSoup(page.content, 'html5lib')
    chapters = sanitize_soup(soup)

    title = soup.find_all("meta", attrs={"name":"DC.Title"})[0]['content']
    author = soup.find_all("meta", attrs={"name":"DC.Creator"})[0]['content']

    book = epub.EpubBook()

    # add metadata
    #book.set_identifier('sample123456')
    book.set_title(title)
    book.set_language('ja')

    book.add_author(author)

    # defube style
    if args.yokogaki:
        style = '''
body {
    word-break: normal;
    text-align: justify;
    text-justify: inter-ideograph;
    vertical-align: baseline;
    word-wrap: break-word;
    line-break: normal;
    -epub-line-break: normal;
    -webkit-line-break: normal;
}
'''

    if args.tategaki or (not args.tategaki and not args.yokogaki):
        style = '''
html {
    direction: rtl;
    -ms-writing-mode: tb-rl;
    -epub-writing-mode: vertical-rl;
    -webkit-writing-mode: vertical-rl;
    writing-mode: vertical-rl;
}
body {
    direction: ltr;
    word-break: normal;
    text-align: justify;
    text-justify: inter-ideograph;
    vertical-align: baseline;
    word-wrap: break-word;
    line-break: normal;
    -epub-line-break: normal;
    -webkit-line-break: normal;
}
'''
    default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=style)
    book.add_item(default_css)


    c1 = epub.EpubHtml(title=title, file_name='intro.xhtml', lang='hr')
    c1.content=f'<h1>{title}</h1><h2>{author}</h2>'
    book.add_item(c1)

    # about chapter
    cn = []
    for chapter in chapters:
        c = epub.EpubHtml(title=chapter[0], file_name=f'{chapter[0]}.xhtml')
        c.content = str(chapter[1])
        c.set_language('hr')
        c.properties.append('rendition:layout-pre-paginated rendition:orientation-landscape rendition:spread-none')
        c.add_item(default_css)
        book.add_item(c)
        cn += [c]

    # create table of contents
    # - add manual link
    # - add section
    # - add auto created links to chapters

    intro = chapters[0]
    book.toc = cn

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define css style
    style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}

h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;
}

ol {
        list-style-type: none;
}

ol > li:first-child {
        margin-top: 0.3em;
}


nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}


nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}

'''

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spine
    book.spine = ['nav', c1]
    for chapter in cn:
        book.spine.append(chapter)

    book.add_metadata(None, 'meta', '', {'name': 'primary-writing-mode', 'content': 'horizontal-rl'})

    # create epub file
    if args.output is None:
        epub.write_epub(f'{title}.epub', book, {})
    else:
        epub.write_epub(f'{args.output}', book, {})
