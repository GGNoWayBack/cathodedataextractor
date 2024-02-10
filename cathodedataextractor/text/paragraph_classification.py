# coding=utf-8
"""
Document preprocessing: paragraph classification.
"""
import os
import re
import copy
import logging
from typing import List, Optional, Union

import bs4.element
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

from ..parse import PARAGRAPH_SEPARATOR, c_a_pattern, fig_pattern, BACKSLASH_REPLACEMENT

log = logging.getLogger(__name__)


class TagClassificationPar2Text:
    """
    Classification of Elsevier XML and RSC HTML document paragraphs based on title tags.
    """

    def __init__(self):
        """
        Basic elements.
        """

        self.doi: str = ''
        self.year: int = 0
        self.abstract: str = ''
        self.introduction: str = ''
        self.experiment: str = ''
        self.partial_text: str = ''
        self.soup: Optional[BeautifulSoup] = None

        self._do_getabstract: bool = True

    def get_abstract(self, path: str = None, head: str = None, tail: str = None):
        """
        Get abstract section of the document.

        Note:
            The file name is named after the doi of the article where '/' is replaced by '.'.

        Args:
            path (str): Document file path. If there is a path, head and tail are not necessary.
            head (str): Document directory path. If head is set there must be tail.
            tail (str): Document file name.
        """
        if path:
            head, tail = os.path.split(path)
        elif not head or not tail:
            raise TypeError("You need to provide the 'path' argument or both 'head' and 'tail'!!!")

        self._do_getabstract = False

        self.doi = tail.rsplit(".", 1)[0].replace(BACKSLASH_REPLACEMENT, "/")

        select_pattern = 'xml' if tail.endswith('xml') else 'html.parser'
        fp = open(f'{head}/{tail}', 'rb')
        soup = BeautifulSoup(fp, features=select_pattern)
        fp.close()

        if select_pattern == 'xml':
            year_tag = ['xocs:year-nav', 'prism:coverDisplayDate']
            for _tag in year_tag:
                year = soup.find(_tag)
                if year:
                    self.year = year.text.rsplit()[-1]
                    break

            abstract = soup.find('ce:abstract', attrs={'class': 'author'})

            if abstract:
                abstract = abstract.find('ce:simple-para')
            else:
                abstract = soup.find('dc:description')
                if not abstract:
                    return
            self.abstract = self._process_soup_contents(abstract.contents).strip()

        else:
            year = soup.find('span', {'class': re.compile("bold italic|italic bold")})
            if year:
                _ = re.search(r'\d{4}', year.text)
                if _:
                    self.year = _.group()
            if self.year == 0:
                con = soup.find('div', attrs={'class': 'article_info'})
                while con and self.year == 0 and con.contents:
                    year = re.search(r'(1[98]\d|20[0-2])\d', str(getattr(con.contents.pop(), 'string')))
                    if year:
                        self.year = year.group()

            s_find = soup.find('h2')
            if s_find and re.search(r'abstract', s_find.text, re.I) and isinstance(s_find.nextSibling, Tag):
                self.abstract = s_find.nextSibling.text.replace('\n', ' ')

        self.soup = soup

    def fulltext(self, path: str = None, head: str = None, tail: str = None):
        """
        Get different topic paragraphs of the document.

        Note:
            The file name is named after the doi of the article where '/' is replaced by '.'.

        Args:
            path (str): Document file path. If there is a path, head and tail are not necessary.
            head (str): Document directory path. If head is set there must be tail.
            tail (str): Document file name.
        """
        if path is not None:
            head, tail = os.path.split(path)
        elif not head or not tail:
            raise TypeError("You need to provide the 'path' argument or both 'head' and 'tail'!!!")

        if self._do_getabstract:
            self.get_abstract(head=head, tail=tail)
        if self.soup.is_xml:

            intro = self.soup.find('section')  # First chapter
            if intro is None:
                log.info('No section tag found: %s', self.doi)
                rawtext = self.soup.find('rawtext')
                if rawtext is not None:
                    self.partial_text = rawtext.text
                else:
                    self.partial_text = copy.copy(self.abstract)
                return

            itr_title = intro.find_all('section-title')  # All subheadings under a major section

            experiment, introduction, total_text = self._elsevier_xml_parse(intro, itr_title)

        else:
            title = self.soup.findAll('h2')  # All major headings
            intro_fg = any(True for _ in title if 'intro' in _.string.lower())
            if len(title) <= 2:
                log.info('Incomplete article: %s  %s', self.doi, title)
                experiment, total_text = self._rcs_html_parse(self.soup.find('div',
                                                                             attrs={'abstract'}).find_next_siblings()
                                                              if self.soup.find('div', attrs={'abstract'}) else
                                                              self.soup.find_all('p'))
                self.experiment = experiment
                self.partial_text = total_text
                return
            # Simply determine whether headings and paragraphs are nested or parallel.
            is_parallel_relation = False
            if len(title[1].contents) == 1:
                is_parallel_relation = True
            experiment, introduction, total_text = '', '', ''
            if is_parallel_relation and intro_fg:  # parallel relationship
                for ind, t in enumerate(title[1:]):
                    if not re.search(r'intro', t.text, re.I):
                        continue
                    full_article_tag = t.find_next_siblings()
                    if not full_article_tag or full_article_tag[0] == title[ind + 1]:
                        # Paragraph and title at the same level
                        break
                    after_intro_tag = full_article_tag.index(title[ind + 2])
                    introduction_tag = full_article_tag[:after_intro_tag]
                    full_article = full_article_tag[after_intro_tag:]
                    _, introduction = self._rcs_html_parse(introduction_tag)

                    experiment, total_text = self._rcs_html_parse(full_article)
                    break

            if not (experiment or total_text):
                experiment, total_text = self._rcs_html_parse(
                    self.soup.find('div', attrs={'abstract'}).find_next_siblings()
                    if self.soup.find('div', attrs={'abstract'}) else self.soup.find_all('p')
                )

        self.experiment = experiment
        self.introduction = introduction
        self.partial_text = total_text

    def _tag_without_linefeed(self, tag):
        re_str = ''
        for t in tag.contents:
            if isinstance(t, NavigableString) and t != '\n':
                re_str += t
            elif isinstance(t, Tag):
                re_str += self._tag_without_linefeed(t)
        return re_str

    def _process_soup_contents(self, contens: list) -> str:
        """
        Marking cross-references
        """
        res_text, cr_fg, pre_iscr = '', False, False
        for con in contens:
            if not cr_fg:
                if isinstance(con, NavigableString):
                    if con[-1] == '[':
                        cr_fg = True
                        res_text += con[:-1]
                    else:
                        res_text += con
                        if con != '\n':
                            pre_iscr = False
                elif 'refid' in con.attrs:
                    if not pre_iscr:
                        res_text += '<FIG>' if fig_pattern.search(con.text) else '<CR>'
                        pre_iscr = True
                else:
                    res_text += self._tag_without_linefeed(con)
                    pre_iscr = False
            else:
                if isinstance(con, NavigableString) and con[0] == ']':
                    if con[-1] == '[':
                        res_text += '<CR>' + con[1:-1]
                    else:
                        res_text += '<CR>' + con[1:]
                        cr_fg = False
                        pre_iscr = False
        return res_text.replace('\n', ' ')

    def _whether_multiple_par(self, oth):
        """
        Separate paragraphs under headings with spaces.
        """
        if len(oth.find_all('para')) > 1:
            return ' '.join(list(map(lambda x: self._process_soup_contents(x), oth.find_all('para'))))
        return self._process_soup_contents(oth.para)

    def _to_find_next_siblings(self, intro):
        """
        Find all sibling nodes after the intro without keeping the title.
        """

        def _all_pare(intro_):
            for int_ in intro_.find_next_siblings():
                pare_text = int_.find_all(name='para')
                for par in pare_text:
                    # manuscript
                    yield None if any(_ for _ in ['review & editing', 'manuscript', 'original draft'] if _ in par.text) \
                        else self._process_soup_contents(par)

        return PARAGRAPH_SEPARATOR.join(list(filter(lambda x: x is not None, list(_all_pare(intro)))))

    def _find_experiment_in_subtitle(self, other, experiment):
        """
        Identify potential experimental sections in all subheadings.
        """
        character_after_exp = False
        for oth in other.contents:
            if oth == '\n':
                continue
            elif oth.name == 'para':
                experiment += oth.text + PARAGRAPH_SEPARATOR
            elif oth.name == 'section' and self.search_experiment(str(oth.find('section-title').text)):
                character_after_exp = True
                if len(oth.find_all('section-title')) == 1:
                    if any(_ for _ in ['°C', '℃', 'temperature', 'K'] if _ in oth.text):
                        experiment += self._whether_multiple_par(oth)
                    continue
                else:
                    return self._find_experiment_in_subtitle(oth, experiment)
            elif any(_ for _ in ['state reaction', 'calcination'] if _ in oth.text) and not character_after_exp and \
                    re.search('character', str(oth.find('section-title')), re.I):
                experiment += self._whether_multiple_par(oth)
        return experiment

    @staticmethod
    def search_experiment(text):
        pattern1 = 'prepar|Synthes|proce|experiment|Method|Material|Chemical|Fabrication|Composition'
        pattern2 = 'model|Comput|Electro|cell'
        search_pattern1 = True if re.search(pattern1, text, re.I) else False
        search_pattern2 = True if re.search(pattern2, text, re.I) else False
        # 'Material preparation and Characterization' cha = 'character'
        return search_pattern1 and not search_pattern2

    def _elsevier_xml_parse(self, intro, itr_title: list) -> tuple:
        """
        Elsevier XML parser.

        Returns:
            Experimental part, intro, full text.
        """
        total_text, experiment, introduction = self.abstract, '', []

        if len(itr_title) > 1:
            fg = False

            for itr in intro.children:
                if itr == '\n':
                    continue

                if self.search_experiment(str(itr.find('section-title'))):
                    fg = True
                    experiment += self._process_soup_contents(itr)
                    total_text += PARAGRAPH_SEPARATOR + self._process_soup_contents(itr)
                    continue
                if not fg:
                    introduction.append(self._process_soup_contents(itr))
                fg = False

        else:
            for _intro in intro.find_all(name='para'):
                introduction.append(self._process_soup_contents(_intro.contents))

        if not experiment:
            for other in intro.find_next_siblings():
                # The default second major heading is the experimental section.
                experimental_section = True if re.search('Material|Experiment|Method|Fabrication',
                                                         other.find('section-title').text, re.I) else False
                all_nex_title_merge = ' '.join(
                    [ot.text for ot in other.find('section-title').find_all_next('section-title')])
                experimental_section_last = True if re.search('Material|Experiment|Method|Fabrication',
                                                              all_nex_title_merge, re.I) else False
                if experimental_section:
                    # If there is no secondary heading for the experimental section,
                    # the first paragraph is selected as the experimental synthesis.
                    if len(other.find_all('section-title')) == 1:
                        if any(_ for _ in ['°C', '℃'] if _ in other.para.text):
                            experiment += self._process_soup_contents(other.para)

                    # The experimental section has a secondary heading and
                    # the synthesis section is under the secondary heading.
                    else:
                        experiment = self._find_experiment_in_subtitle(other, experiment)
                    break
                else:
                    # The experimental part is in the discussion of the results.
                    if not (re.search('Results?|discussions?',
                                      other.find('section-title').text) and not experimental_section_last):
                        continue
                    if len(other.find_all('section-title')) == 1:
                        experiment += self._process_soup_contents(other.para)
                    else:
                        for oth in other.contents:
                            if oth == '\n':
                                continue
                            if self.search_experiment(str(oth.find('section-title'))) \
                                    and ('°C' in oth.text or 'synthe' in oth.text):
                                experiment = self._whether_multiple_par(oth)

        return experiment, PARAGRAPH_SEPARATOR.join(
            introduction), total_text + PARAGRAPH_SEPARATOR + self._to_find_next_siblings(intro)

    def _rcs_html_parse(self, full_article_tag: list) -> tuple:
        """
        RCS HTML parser.

        Returns:
            Experimental paragraphs and full text.
        """

        def _check_if_h2(ind, length):  # Detecting the presence of secondary headings.
            for id_ in range(ind + 1, length):
                if full_article_tag[id_].name == 'h3':
                    return True
                elif full_article_tag[id_].name == 'h2':
                    return False

        total_text, experiment, ex_action, exx_action, break_fg = self.abstract, '', False, False, False
        for ind, tag in enumerate(full_article_tag):
            # Remove citation tags.
            tag_text, span_class = [], ''
            for _ in tag.contents:  # Handling leaf nodes
                if isinstance(_, NavigableString):
                    tag_text.append(_)
                elif tag_text and tag_text[-1].endswith(('<CR>', '<CR>.', '<CR>,')):
                    continue
                elif re.search(r'#cit', str(_.attrs)):  # img fig
                    if tag_text:
                        if tag_text[-1].endswith('.'):
                            tag_text[-1] = tag_text[-1][:-1] + ' <CR>.'
                        elif tag_text[-1].endswith(','):
                            tag_text[-1] = tag_text[-1][:-1] + ' <CR>,'
                        else:
                            tag_text.append(' <CR>')
                    else:
                        tag_text.append('<CR> ')
                elif re.search(r'#img', str(_.attrs)):
                    tag_text.append('<FIG>')
                else:
                    span_class = _.attrs['class'][0] if 'class' in _.attrs else ''
                    if any(c_a_pattern.search(c.text) for c in _.children
                           if (isinstance(c, Tag) and 'class' in c.attrs)) or \
                            (tag.name == 'h2' and c_a_pattern.search(tag.text)):
                        # The tags are nested in different layers.
                        break_fg = True
                        break
                    tag_text.append(_.text)
            if break_fg:
                break
            elif not tag_text:
                continue

            tag_text = ''.join(tag_text)

            if span_class.startswith('a_'):  # a_heading First level title.
                if ex_action and exx_action:
                    ex_action = False
                else:
                    if self.search_experiment(tag.text):
                        if _check_if_h2(ind, len(full_article_tag)):  # Early checking of secondary headings.
                            ex_action = True
                        else:
                            exx_action = True
                            ex_action = True

            elif span_class.startswith('b_'):  # b_heading secondary heading.
                # Build subheadings into it.
                exx_action = True if self.search_experiment(tag.text) else False

            if tag_text:
                tag_text = tag_text.replace('\n', ' ').strip()
                tag_text += ' ' if tag_text.endswith(('.', ',', ';', ':')) else '. '
                total_text += PARAGRAPH_SEPARATOR + tag_text
                if ex_action and exx_action:
                    experiment += tag_text
        return experiment, total_text
