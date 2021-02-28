# -*- coding: utf-8 -*-
# Hapax Predator
# see LICENSE file


#  Released under the GNU General Public License v3.
#  Copyright (C) - 2020 - user "thiswillbeyourgithub" of the website "github".
#  This file is the code for Hapax Predator : an tool that orders your words
#  by frequency to help find misspellings and pave the way for NLP tasks.
#  
#  Hapax Predator is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Hapax Predator is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with Hapax Predator.  If not, see <https://www.gnu.org/licenses/>.
#  
#  for more information or to get the latest version go to :
#  https://github.com/thiswillbeyourgithub/Clozolkor
#  Version : ferbuary 2021
#  
#  credits due to Glutanimate, his code for the addon "Batch Editing" was 
#  the basis for the QT code that I used below, as I have not yet learned QT.


import re
import pprint
from collections import Counter

from aqt.qt import *
from aqt.utils import tooltip
from anki.hooks import addHook


class HPDialog(QDialog):
    def __init__(self, browser, nids):
        QDialog.__init__(self, parent=browser)
        self.browser = browser
        self.nids = nids
        self._setup()

    def _setup(self):
        browser = self.browser
        nids = self.nids
        fld = "Body"
        mw = browser.mw
        mw.checkpoint("Hapax Predator")
        cnt = 0
        all_texts=[]
        for nid in nids:
            note = mw.col.getNote(nid)
            all_texts.extend(note.fields)
            cnt += 1

        all_text = " ".join(all_texts)
        #all_text = str(all_text).encode("utf8").decode("utf8")

        # remove clozes
        all_text = re.sub("{{c\d+::|}}", "", all_text)
        all_text = re.sub("::|/", " ", all_text)

        # html
        all_text = re.sub("src=\".*?\"", " ", all_text)
        all_text = re.sub("src='.*?'", " ", all_text)
        all_text = re.sub("&nbsp|&nbsp;", " ", all_text)
        all_text = re.sub("\\n", " ", all_text)
        all_text = re.sub("<br>|<br|<div>|<div|<span>|<div", " ", all_text)
        all_text = re.sub("<|>", " ", all_text)
        all_text = re.sub("title|style|class|height|source|width|paste|figure"
                , " ", all_text)

        # lang
        all_text = re.sub("d'|l'|\+|=", " ", all_text)
        all_text = re.sub("é|è|ê", "e", all_text)
        all_text = re.sub("ç", "c", all_text)
        all_text = re.sub("ï", "c", all_text)
        all_text = re.sub("à", "a", all_text)

        # misc
        all_text = re.sub("/|\"|'|!|\?|\.|\(|\)|-", " ", all_text)
        all_text = all_text.lower()

        alphaNumeric = re.compile("[a-zÀ-ú][a-zÀ-ú]{4,30}")
        words = [w for w in alphaNumeric.findall(all_text)]
        #words = all_text.split(" ")
        #words.remove('')

        count = Counter(words)
        doneText = str(pprint.pformat(count))
        tlabel = QLabel("Hapax Predator :\nHere are the words from your "\
            + "cards  by frequency\nUse it to correct mistakes")

        top_hbox = QHBoxLayout()
        top_hbox.addWidget(tlabel)
        top_hbox.insertStretch(1, stretch=1)
        self.tedit = QPlainTextEdit(doneText)
        self.tedit.setTabChangesFocus(True)
        button_box = QDialogButtonBox(Qt.Horizontal, self)
        close_btn = button_box.addButton("&Close",
                                         QDialogButtonBox.RejectRole)
        close_btn.clicked.connect(self.close)
        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(button_box)
        vbox_main = QVBoxLayout()
        vbox_main.addLayout(top_hbox)
        vbox_main.addWidget(self.tedit)
        vbox_main.addLayout(bottom_hbox)
        self.setLayout(vbox_main)
        self.tedit.setFocus()
        self.setMinimumWidth(540)
        self.setMinimumHeight(400)
        self.setWindowTitle("Hapax Predator")

def HP(browser):
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    dialog = HPDialog(browser, nids)
    dialog.exec_()

def setupMenu(browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('Hapax Predator')
    a.triggered.connect(lambda _, b=browser: HP(b))

addHook("browser.setupMenus", setupMenu)


