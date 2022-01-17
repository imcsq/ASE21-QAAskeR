import json
import spacy
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from pattern.text.en import conjugate, lemma, lexeme, PRESENT, INFINITIVE, PAST, FUTURE, SG, PLURAL, PROGRESSIVE

nlp = spacy.load('en_core_web_sm')


def tree_to_list_node(node, tree):
    if node.n_lefts + node.n_rights > 0:
        tree.insert(0, node)
        return [tree_to_list_node(child, tree) for child in node.children]
    else:
        tree.insert(0, node)


def child_to_list_node(node, tree):
    if node.n_lefts + node.n_rights > 0:
        for child in node.children:
            tree.insert(0, child)


def tree_to_list_str(node, tree):
    if node.n_lefts + node.n_rights > 0:
        tree.insert(0, node.orth_)
        return [tree_to_list_str(child, tree) for child in node.children]
    else:
        tree.insert(0, node.orth_)


def list_to_order(sent, list):
    ctnu = False
    order = []
    start = 0
    num = -1
    while (True):
        num += 1
        if sent[num] in list:
            if not ctnu:
                start = num
            order.append(sent[num])
            ctnu = True
            if len(order) == len(list):
                c = []
                c = [x for x in list if x not in order]
                if c == []:
                    break
                else:
                    num = num - len(list) + 1
                    start = 0
                    order = []
                    ctnu = False
        else:
            start = 0
            order = []
            ctnu = False
    return start, order


def list_to_str(a_list):
    str_out = TreebankWordDetokenizer().detokenize(a_list)
    return str_out


def tense(word):
    word_ = nlp(word)
    word_lemma = word_[0].lemma_
    word_doing = conjugate(word_lemma, tense=PRESENT, aspect=PROGRESSIVE)
    word_did = conjugate(word_lemma, tense=PAST)
    word_done = conjugate(word_lemma, tense=PAST, aspect=PROGRESSIVE)
    if word == word_doing:
        return 1
    elif word == word_did:
        if word_did == word_done:
            return 4
        return 2
    elif word == word_done:
        return 3
    else:
        return 5


def acl(this_acl, dep_tokens_new_question):
    need_change = True
    if this_acl + 1 != len(dep_tokens_new_question):
        if dep_tokens_new_question[this_acl + 1] == "advmod":
            return False
    if dep_tokens_new_question[this_acl - 1] == "aux":
        return False
    for dep in dep_tokens_new_question[this_acl + 1:]:
        if dep == "acl" or dep == "ROOT":
            break
        if dep == "xcomp" or dep == "pcomp" or dep == "pobj" or dep == "advcl":
            need_change = False
    return need_change


class howmany(object):

    def generate(self, question, answer):
        try:
            return self.generate_statement(question, answer)
        except IndexError as e:
            return None

    def generate_statement(self, question, answer):
        is_how_long = False
        this_question = question
        if "How many " in question:
            question = this_question.replace("How many ", "howmany ")
        elif "how many " in question:
            question = this_question.replace("how many ", "howmany ")
        elif "How much " in question:
            question = this_question.replace("How much ", "howmany ")
        elif "how much " in question:
            question = this_question.replace("how much ", "howmany ")
        elif "How old " in question:
            question = this_question.replace("How old ", "howmany ")
        elif "how old " in question:
            question = this_question.replace("how old ", "howmany ")
        elif "How far " in question:
            is_how_long = True
            question = this_question.replace("How far ", "howmany ")
        elif "how far " in question:
            is_how_long = True
            question = this_question.replace("how far ", "howmany ")
        elif "How long " in question:
            is_how_long = True
            question = this_question.replace("How long ", "howmany ")
        elif "how long " in question:
            is_how_long = True
            question = this_question.replace("how long ", "howmany ")
        question = question.replace("  ", " ")
        if question[-1] == " ":
            question = question[:-1]
        if question[-2:-1] == ".?":
            question = question[:-2] + "?"
        elif question[-2:-1] == "??":
            question = question[:-1]
        elif question[-1] != "?":
            question = question + "?"
        doc_question = nlp(question)
        doc_answer = nlp(answer)
        tokens_question = [token for token in doc_question if token.text != ""]
        dep_tokens_question = [token.dep_ for token in doc_question if token.text != ""]
        pos_tokens_question = [token.pos_ for token in doc_question if token.text != ""]
        str_tokens_answer = [token.text for token in doc_answer if token.text != ""]
        pos_tokens_answer = [token.pos_ for token in doc_answer if token.text != ""]
        tag_tokens_question = [token.tag_ for token in doc_question if token.text != ""]
        str_tokens_question = [token.text for token in doc_question if token.text != ""]
        have_comma = False
        all_comma = []
        all_howmany = []
        num = 0
        for token in tokens_question:
            if token.text == ",":
                all_comma.append(num)
                have_comma = True
            if token.text == "howmany":
                all_howmany.append(num)
            num += 1
        small_question_start = 0
        have_comma_do = False
        if have_comma:
            for comma in all_comma:
                if all_howmany[0] > comma:
                    small_question_start = comma
                    have_comma_do = True
        if have_comma_do:
            new_question = list_to_str(str_tokens_question[small_question_start + 1:])
            final_add = list_to_str(str_tokens_question[:small_question_start])
        else:
            new_question = question
        doc_new_question = nlp(new_question)
        tokens_new_question = [token for token in doc_new_question if token.text != ""]
        str_tokens_new_question = [token.text for token in doc_new_question if token.text != ""]
        pos_tokens_new_question = [token.pos_ for token in doc_new_question if token.text != ""]
        dep_tokens_new_question = [token.dep_ for token in doc_new_question if token.text != ""]
        tag_tokens_new_question = [token.tag_ for token in doc_new_question if token.text != ""]
        real_root = str_tokens_new_question[dep_tokens_new_question.index("ROOT")]
        real_root_plc = dep_tokens_new_question.index("ROOT")
        howmany = []
        howmany_plc = []
        num = 0
        for word in tokens_new_question:
            if word.lemma_ == "howmany":
                howmany.append(word)
                howmany_plc.append(num)
            num += 1
        vbs = []
        vbs_plc = []
        num = 0
        for pos in pos_tokens_new_question:
            if pos in ["VERB", 'AUX'] and tokens_new_question[num].text != conjugate(tokens_new_question[num].lemma_,
                                                                                      tense=PRESENT,
                                                                                      aspect=PROGRESSIVE):
                vbs.append(str_tokens_new_question[num])
                vbs_plc.append(num)
                num += 1
                continue
            num += 1
        if vbs == []:
            final = []
            final.extend(str_tokens_new_question[:howmany_plc[0]])
            final.extend([answer])
            if str_tokens_new_question[howmany_plc[0] + 1] in answer:
                final.extend(str_tokens_new_question[howmany_plc[0] + 2:])
            else:
                final.extend(str_tokens_new_question[howmany_plc[0] + 1:])
            final.pop()
            final_out = list_to_str(final)
            if have_comma_do:
                final_out = final_add + ", " + final_out + "."
            else:
                final_out = final_out[0].upper() + final_out[1:] + "."
            return final_out
        first_vb = vbs[0]
        first_vb_plc = vbs_plc[0]
        be = ["be", "is", "are", "was", "were", "am"]
        do = ["did", "do", "does", "would", "could", "will", "can", "should", "might", "may", "has", "have", "had",
              "must"]
        did = ["did", "do", "does"]
        would = ["would", "could", "will", "can", "should", "might", "may", "has", "had", "have", "must"]
        if "there" in str_tokens_new_question and str_tokens_new_question[0] == "howmany":
            there_plc = str_tokens_new_question.index("there")
            final = []
            after_answer = str_tokens_new_question[howmany_plc[0] + 1:there_plc - 1]
            after_there = str_tokens_new_question[there_plc + 1:]
            final.extend([str_tokens_new_question[there_plc]])
            final.extend([str_tokens_new_question[there_plc - 1]])
            if str_tokens_answer[-1] in after_answer:
                final.extend(str_tokens_answer[:-2])
            else:
                final.extend([answer])
            final.extend(after_answer)
            final.extend(after_there)
            final.pop()
            final_out = list_to_str(final)
            final_out = final_out[0].upper() + final_out[1:] + "."
            return final_out
        if first_vb in be:
            if str_tokens_new_question[0] == "howmany":
                output1 = str_tokens_new_question[:first_vb_plc + 1]
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                if tag_tokens_question[1] == "IN":
                    final = []
                    final.extend([answer])
                    final.extend(str_tokens_new_question[1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if "there" in str_tokens_new_question:
                    there_plc = str_tokens_new_question.index("there")
                    final = []
                    after_answer = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                    final.extend([str_tokens_new_question[there_plc]])
                    final.extend([str_tokens_new_question[first_vb_plc]])
                    if str_tokens_answer[-1] in after_answer:
                        final.extend(str_tokens_answer[:-2])
                    else:
                        final.extend([answer])
                    final.extend(after_answer)
                    final.extend(str_tokens_new_question[there_plc + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                tag = nltk.pos_tag(str_tokens_output2)
                nltk_tag = [this_tag[1] for this_tag in tag]
                if "than" in str_tokens_new_question:
                    than_plc = str_tokens_new_question.index("than")
                    final = []
                    after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                    final.extend(str_tokens_new_question[first_vb_plc + 1:than_plc])
                    final.extend([first_vb])
                    if str_tokens_answer[-1] in after_howmany:
                        final.extend(str_tokens_answer[:-2])
                    else:
                        final.extend([answer])
                    final.extend(after_howmany)
                    final.extend(str_tokens_new_question[than_plc:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if pos_tokens_output2[0] == "VERB" or pos_tokens_output2[0] == "VERB" or "VB" in nltk_tag[0]:
                    final = []
                    final.extend(str_tokens_new_question[:howmany_plc[0]])
                    final.extend([answer])
                    if str_tokens_new_question[howmany_plc[0] + 1] in answer:
                        final.extend(str_tokens_new_question[howmany_plc[0] + 2:])
                    else:
                        final.extend(str_tokens_new_question[howmany_plc[0] + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if pos_tokens_output2[root_plc] == "VERB" or "VB" in nltk_tag[root_plc]:
                    final = []
                    after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                    final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                    final.extend([first_vb])
                    final.extend([str_tokens_new_question[len(output1) + root_plc]])
                    if str_tokens_answer[-1] in after_howmany:
                        final.extend(str_tokens_answer[:-2])
                    else:
                        final.extend([answer])
                    final.extend(after_howmany)
                    final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if len(tag_tokens_question) >= 2 and len(nltk_tag) >= 3:
                    if tag_tokens_question[-2] == "IN" and "VB" in nltk_tag[-3]:
                        final = []
                        after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                        final.extend(str_tokens_new_question[first_vb_plc + 1:-3])
                        final.extend([first_vb])
                        final.extend([str_tokens_new_question[-3]])
                        final.extend(str_tokens_new_question[-2:])
                        final.pop()
                        if str_tokens_answer[-1] in after_howmany:
                            final.extend(str_tokens_answer[:-2])
                        else:
                            final.extend([answer])
                        final.extend(after_howmany)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                if len(tag_tokens_question) >= 2:
                    if tag_tokens_question[-2] == "IN":
                        output2 = str_tokens_new_question[first_vb_plc + 1:]
                        final = []
                        after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        final.extend([first_vb])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        if str_tokens_answer[-1] in after_howmany:
                            final.extend(str_tokens_answer[:-2])
                        else:
                            final.extend([answer])
                        final.extend(after_howmany)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                for tag in nltk_tag:
                    if "VB" in tag:
                        root_plc = nltk_tag.index(tag)
                        root = str_tokens_output2[root_plc]
                        final = []
                        after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                        final.extend([first_vb])
                        final.extend([str_tokens_new_question[len(output1) + root_plc]])
                        if is_how_long:
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            if "until" in answer or "to" in answer:
                                final.extend(["from"])
                            else:
                                final.extend(["for"])
                            final.extend([answer])
                            final.extend(after_howmany)
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if str_tokens_answer[-1] in after_howmany:
                            final.extend(str_tokens_answer[:-2])
                        else:
                            final.extend([answer])
                        final.extend(after_howmany)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                if is_how_long:
                    final = []
                    final.extend(str_tokens_new_question[first_vb_plc + 1:])
                    final.pop()
                    final.extend([str_tokens_new_question[first_vb_plc]])
                    if "to" in answer:
                        final.extend(["from"])
                    elif "until" in answer and str_tokens_answer[0] != "until":
                        final.extend(["from"])
                    elif "year" in answer:
                        final.extend(["for"])
                    elif "NUM" in pos_tokens_answer and "km" not in answer and "long" not in answer:
                        final.extend(["for"])
                    final.extend([answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                final = []
                final.extend(str_tokens_new_question[:howmany_plc[0]])
                final.extend([answer])
                if str_tokens_new_question[howmany_plc[0] + 1] in answer:
                    final.extend(str_tokens_new_question[howmany_plc[0] + 2:])
                else:
                    final.extend(str_tokens_new_question[howmany_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
            else:
                final = []
                final.extend(str_tokens_new_question[:howmany_plc[0]])
                final.extend([answer])
                if str_tokens_new_question[howmany_plc[0] + 1] in answer:
                    final.extend(str_tokens_new_question[howmany_plc[0] + 2:])
                else:
                    final.extend(str_tokens_new_question[howmany_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        if first_vb in do:
            if str_tokens_new_question[0] in ["howmany"]:
                output1 = str_tokens_new_question[:first_vb_plc + 1]
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                tag = nltk.pos_tag(str_tokens_output2)
                nltk_tag = [this_tag[1] for this_tag in tag]
                if first_vb in do:
                    if first_vb in did:
                        this_tense = 0
                        if first_vb == "do":
                            this_tense = 1
                        elif first_vb == "does":
                            this_tense = 2
                        elif first_vb == "did":
                            this_tense = 3
                        if tag_tokens_new_question[-2] == "IN":
                            final = []
                            after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                            this_verb = ""
                            if this_tense == 1 or this_tense == 0:
                                this_verb = str_tokens_new_question[len(output1) + root_plc]
                            if this_tense == 2:
                                this_verb = conjugate(tokens_new_question[len(output1) + root_plc].lemma_,
                                                      tense=PRESENT,
                                                      number=SG)
                            if this_tense == 3:
                                this_verb = conjugate(tokens_new_question[len(output1) + root_plc].lemma_, tense=PAST)
                            final.extend([this_verb])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            if str_tokens_answer[-1] in after_howmany:
                                final.extend(str_tokens_answer[:-2])
                            else:
                                final.extend([answer])
                            final.extend(after_howmany)
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if_next_vb = False
                        num = -1
                        for word in str_tokens_output2[:-2]:
                            num += 1
                            if word in would:
                                if pos_tokens_output2[num + 1] == "VERB":
                                    answer_plc = num
                                    if_next_vb = True
                        final = []
                        after_howmany = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                        pos_after_howmany = pos_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                        this_verb = ""
                        if this_tense == 1 or this_tense == 0:
                            this_verb = str_tokens_new_question[len(output1) + root_plc]
                        if this_tense == 2:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc].lemma_, tense=PRESENT,
                                                  number=SG)
                        if this_tense == 3:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc].lemma_, tense=PAST)
                        final.extend([this_verb])
                        if if_next_vb:
                            final.extend(
                                str_tokens_new_question[len(output1) + root_plc + 1:len(output1) + answer_plc + 2])
                            if str_tokens_answer[-1] in after_howmany:
                                final.extend(str_tokens_answer[:-2])
                            else:
                                final.extend([answer])
                            final.extend(after_howmany)
                            final.extend(str_tokens_new_question[len(output1) + answer_plc + 2:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if is_how_long:
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            if pos_tokens_answer[0] == "IN":
                                final.extend([answer])
                            else:
                                if after_howmany != []:
                                    if pos_after_howmany[0] == "IN" or after_howmany[0] in ["after", "before"]:
                                        final.extend([answer])
                                else:
                                    final.extend(["for", answer])
                            final.extend(after_howmany)
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if str_tokens_answer[-1] in after_howmany:
                            final.extend(str_tokens_answer[:-2])
                        else:
                            final.extend([answer])
                        final.extend(after_howmany)
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        if pos_tokens_output2[0] == "VERB" or "VB" in nltk_tag[0]:
                            final = []
                            after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                            final.extend(str_tokens_new_question[:howmany_plc[0]])
                            if str_tokens_answer[-1] in after_how:
                                final.extend(str_tokens_answer[:-2])
                            else:
                                final.extend([answer])
                            final.extend(after_how)
                            final.extend(str_tokens_new_question[first_vb_plc:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if tokens_output2[root_plc - 1].lemma_ == "be":
                            if tag_tokens_output2[-2] == "IN":
                                final = []
                                after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                                final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc - 1])
                                final.extend([first_vb])
                                final.extend(str_tokens_output2[root_plc - 1:])
                                final.pop()
                                if str_tokens_answer[-1] in after_how:
                                    final.extend(str_tokens_answer[:-2])
                                else:
                                    final.extend([answer])
                                final.extend(after_how)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            final = []
                            if is_how_long:
                                after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                                final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc - 1])
                                final.extend([first_vb])
                                final.extend(str_tokens_output2[root_plc - 1:])
                                final.pop()
                                if pos_tokens_answer[0] == "IN" or str_tokens_answer[0] in ["since", "before", "after"]:
                                    final.extend([answer])
                                else:
                                    final.extend(["for", answer])
                                final.extend(after_how)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc - 1])
                            final.extend([first_vb])
                            final.extend(str_tokens_output2[root_plc - 1:root_plc + 1])
                            if str_tokens_answer[-1] in after_how:
                                final.extend(str_tokens_answer[:-2])
                            else:
                                final.extend([answer])
                            final.extend(after_how)
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if len(tag_tokens_output2) > 1:
                            if tag_tokens_output2[-2] == "IN":
                                final = []
                                after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                                final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                                final.extend([first_vb])
                                final.extend([str_tokens_output2[root_plc]])
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                                final.pop()
                                if str_tokens_answer[-1] in after_how:
                                    final.extend(str_tokens_answer[:-2])
                                else:
                                    final.extend([answer])
                                final.extend(after_how)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                        final = []
                        if is_how_long:
                            after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                            final.extend([first_vb])
                            final.extend(str_tokens_output2[root_plc:])
                            final.pop()
                            if pos_tokens_answer[0] == "IN" or str_tokens_answer[0] in ["since", "before", "after"]:
                                final.extend([answer])
                            else:
                                final.extend(["for", answer])
                            final.extend(after_how)
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        after_how = str_tokens_new_question[howmany_plc[0] + 1:first_vb_plc]
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                        final.extend([first_vb])
                        final.extend([str_tokens_output2[root_plc]])
                        if str_tokens_answer[-1] in after_how:
                            final.extend(str_tokens_answer[:-2])
                        else:
                            final.extend([answer])
                        final.extend(after_how)
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
        final = []
        final.extend(str_tokens_new_question[:howmany_plc[0]])
        final.extend([answer])
        if str_tokens_new_question[howmany_plc[0] + 1] in answer:
            final.extend(str_tokens_new_question[howmany_plc[0] + 2:])
        else:
            final.extend(str_tokens_new_question[howmany_plc[0] + 1:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "."
        else:
            final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out


