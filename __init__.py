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
from anki.utils import stripHTML
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
        mw = browser.mw
        mw.checkpoint("Hapax Predator")
        all_texts = []
        selected_fields = "Body,Header".split(",")  # testing
        for nid in nids:
            note = mw.col.getNote(nid)
            if selected_fields != [""]:
                model = note.note_type()
                fields = {}
                for info in model['flds']:
                    order = info['ord']
                    name = info['name']
                    fields[name] =  note.fields[order]

                for field, content in fields.items():
                    if field in selected_fields:
                        all_texts.append(content)
            else:
                all_texts.extend(note.fields)

        all_text = " ".join(all_texts).strip()

        if all_text == "":
            doneText = "No text found, wrong field name?"

        else:
            all_text = stripHTML(all_text.lower())
            all_text = re.sub(r"\W|\d", " ", all_text)

            all_text = re.sub("é|è|ê", "e", all_text)
            all_text = re.sub("ç", "c", all_text)
            all_text = re.sub("ï", "i", all_text)
            all_text = re.sub("à", "a", all_text)


            alphaNumeric = re.compile("[a-zÀ-ú]{3,30}")
            words = [w for w in alphaNumeric.findall(all_text)]

            count = Counter(words)

            count_list = []
            for word, cnt in count.items():
                count_list.append([cnt, word])
            count_list = sorted(count_list, key=lambda x: x[0], reverse=False)

            lines = ["Rank / Frequency / Word"]
            for i, both in enumerate(count_list):
                i += 1
                cnt = both[0]
                word = both[1]
                lines.append(f"#{i:04d}:  {cnt:04d} : {word:<34}")
            doneText = "\n".join(lines)

        tlabel = QLabel("Hapax Predator :\nHere are the words from your "\
                        + "cards  by frequency\nUse it to correct mistakes")

        top_hbox = QHBoxLayout()
        top_hbox.addWidget(tlabel)
        top_hbox.insertStretch(1, stretch=1)
        self.tedit = QTextEdit(self)
        self.tedit.setReadOnly(True)
        self.tedit.setText(doneText)
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
