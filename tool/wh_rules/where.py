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


class where(object):

    def generate(self, question, answer):
        try:
            return self.generate_statement(question, answer)
        except IndexError as e:
            return None

    def generate_statement(self, question, answer):
        if "WHere" in question:
            question = question.replace("WHere", "where")
        if " doe " in question:
            question = question.replace(" doe ", " do ")
        if "In which " in question:
            question = question.replace("In which ", "Where")
        elif "in which " in question:
            question = question.replace("in which ", "where")
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
        tag_tokens_answer = [token.tag_ for token in doc_answer if token.text != ""]
        tag_tokens_question = [token.tag_ for token in doc_question if token.text != ""]
        str_tokens_question = [token.text for token in doc_question if token.text != ""]
        have_comma = False
        all_comma = []
        all_where = []
        num = 0
        for token in tokens_question:
            if token.text == ",":
                all_comma.append(num)
                have_comma = True
            if token.text == "Where" or token.text == "where":
                all_where.append(num)
            num += 1
        small_question_start = 0
        have_comma_do = False
        if have_comma:
            for comma in all_comma:
                if all_where[0] > comma:
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
        where = []
        where_plc = []
        num = 0
        for word in tokens_new_question:
            if word.lemma_ == "where":
                where.append(word)
                where_plc.append(num)
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
            if "where " in new_question:
                new_question = new_question.replace("where ", "where is ")
            else:
                new_question = new_question.replace("Where ", "Where is ")
            doc_new_question = nlp(new_question)
            tokens_new_question = [token for token in doc_new_question if token.text != ""]
            str_tokens_new_question = [token.text for token in doc_new_question if token.text != ""]
            pos_tokens_new_question = [token.pos_ for token in doc_new_question if token.text != ""]
            dep_tokens_new_question = [token.dep_ for token in doc_new_question if token.text != ""]
            tag_tokens_new_question = [token.tag_ for token in doc_new_question if token.text != ""]
            real_root = str_tokens_new_question[dep_tokens_new_question.index("ROOT")]
            real_root_plc = dep_tokens_new_question.index("ROOT")
            vbs = []
            vbs_plc = []
            num = 0
            for pos in pos_tokens_new_question:
                if pos in ["VERB", 'AUX'] and tokens_new_question[num].text != conjugate(
                        tokens_new_question[num].lemma_,
                        tense=PRESENT,
                        aspect=PROGRESSIVE):
                    vbs.append(str_tokens_new_question[num])
                    vbs_plc.append(num)
                    num += 1
                    continue
                num += 1
        if vbs == []:
            final = []
            final.extend(str_tokens_new_question[:where_plc[0]])
            if tag_tokens_answer[0] in ["IN"]:
                final.extend([answer])
            else:
                final.extend(["in", answer])
            final.extend(str_tokens_new_question[where_plc[0] + 1:])
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
        if first_vb in be:
            if str_tokens_new_question[0] in ["Where", "where"]:
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                be_before_root = False
                if tokens_output2[root_plc - 1].lemma_ == "be":
                    be_before_root = True
                not_before_be_root = False
                if be_before_root and tokens_output2[root_plc - 2].lemma_ == "not":
                    not_before_be_root = True
                if "there" in str_tokens_new_question:
                    there_plc = str_tokens_new_question.index("there")
                    final = []
                    final.extend([str_tokens_new_question[there_plc]])
                    final.extend([str_tokens_new_question[first_vb_plc]])
                    final.extend(str_tokens_new_question[there_plc + 1:])
                    final.pop()
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend([answer])
                    else:
                        final.extend(["in", answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if first_vb_plc == len(str_tokens_new_question) - 2:
                    final = []
                    final.extend(str_tokens_new_question[where_plc[0] + 1:])
                    final.pop()
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend([answer])
                    else:
                        final.extend(["in", answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                output1 = str_tokens_new_question[:first_vb_plc + 1]
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                if pos_tokens_output2[root_plc] == "VERB" or root_plc + 2 == len(dep_tokens_output2):
                    final = []
                    final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                    final.extend([first_vb])
                    final.extend(str_tokens_new_question[len(output1) + root_plc:])
                    after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                    final.pop()
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend([answer])
                    else:
                        final.extend(["in", answer])
                    final.extend(after_where)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                next_output1 = str_tokens_output2[:root_plc + 1]
                next_output2 = str_tokens_output2[root_plc + 1:]
                next_doc_output2 = nlp(list_to_str(next_output2))
                next_tokens_output2 = [token for token in next_doc_output2 if token.text != ""]
                next_str_tokens_output2 = [token.text for token in next_doc_output2 if
                                           token.text != ""]
                next_dep_tokens_output2 = [token.dep_ for token in next_doc_output2 if token.text != ""]
                next_pos_tokens_output2 = [token.pos_ for token in next_doc_output2 if token.text != ""]
                next_root = str_tokens_output2[next_dep_tokens_output2.index("ROOT")]
                next_root_plc = next_dep_tokens_output2.index("ROOT")
                if next_pos_tokens_output2[next_root_plc] == "VERB":
                    final = []
                    final.extend(
                        str_tokens_new_question[first_vb_plc + 1:len(output1) + len(next_output1) + next_root_plc])
                    final.extend([first_vb])
                    final.extend(str_tokens_new_question[len(output1) + len(next_output1) + next_root_plc:])
                    final.pop()
                    after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend([answer])
                    else:
                        final.extend(["in", answer])
                    final.extend(after_where)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if tag_tokens_output2[-2] in ["IN"]:
                    final = []
                    final.extend(str_tokens_new_question[first_vb_plc + 1:-2])
                    final.extend([first_vb])
                    final.extend(str_tokens_new_question[-2:])
                    final.pop()
                    after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend(str_tokens_answer[1:])
                    else:
                        final.extend([answer])
                    final.extend(after_where)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                tag = nltk.pos_tag(str_tokens_output2)
                nltk_tag = [this_tag[1] for this_tag in tag]
                adj_plc = len(str_tokens_output2)
                for pos in pos_tokens_output2:
                    if pos in ["ADJ", "ADJP"]:
                        adj_plc = pos_tokens_output2.index(pos)
                for this_tag in nltk_tag:
                    if "VB" in this_tag:
                        if pos_tokens_output2[nltk_tag.index(this_tag)] in ["NOUN",
                                                                            "PROPN"] or adj_plc < nltk_tag.index(
                                this_tag):
                            if adj_plc < nltk_tag.index(this_tag):
                                for pos in pos_tokens_output2:
                                    if pos in ["ADJ", "ADJP"]:
                                        root_plc = pos_tokens_output2.index(pos)
                                        final = []
                                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                                        final.extend([str_tokens_new_question[first_vb_plc]])
                                        final.extend(str_tokens_new_question[len(output1) + root_plc:])
                                        final.pop()
                                        if tag_tokens_answer[0] in ["IN"]:
                                            final.extend([answer])
                                        else:
                                            final.extend(["in", answer])
                                        final_out = list_to_str(final)
                                        if have_comma_do:
                                            final_out = final_add + ", " + final_out + "."
                                        else:
                                            final_out = final_out[0].upper() + final_out[1:] + "."
                                        return final_out
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:])
                            final.pop()
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if tag_tokens_answer[0] in ["IN"]:
                                final.extend([answer])
                            else:
                                final.extend(["in", answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        root_plc = nltk_tag.index(this_tag)
                        final = []
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                        final.extend([str_tokens_new_question[first_vb_plc]])
                        final.extend([str_tokens_new_question[len(output1) + root_plc]])
                        after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                        if tag_tokens_answer[0] in ["IN"]:
                            final.extend([answer])
                        else:
                            final.extend(["in", answer])
                        final.extend(after_where)
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                final = []
                final.extend(str_tokens_new_question[first_vb_plc + 1:])
                final.pop()
                after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                final.extend([first_vb])
                if tag_tokens_answer[0] in ["IN"]:
                    final.extend([answer])
                else:
                    final.extend(["in", answer])
                final.extend(after_where)
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
            else:
                output1 = str_tokens_new_question[:first_vb_plc + 1]
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                if pos_tokens_output2[root_plc] == "VERB":
                    final = []
                    final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                    final.extend([first_vb])
                    final.extend(str_tokens_new_question[len(output1) + root_plc:])
                    final.pop()
                    before_where = str_tokens_new_question[:where_plc[0]]
                    if before_where != []:
                        before_where[0] = before_where[0][0].lower() + before_where[0][1:]
                    after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                    final.extend(before_where)
                    if len(tag_tokens_answer) == 0:
                        final = final
                    elif tag_tokens_answer[0] in ["IN"]:
                        final.extend(str_tokens_answer[1:])
                    else:
                        final.extend([answer])
                    final.extend(after_where)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                final = []
                final.extend(str_tokens_new_question[:where_plc[0]])
                if tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[where_plc[0] - 1] not in ["IN"]:
                    final.extend([answer])
                elif tag_tokens_answer[0] not in ["IN"] and tag_tokens_new_question[where_plc[0] - 1] in ["IN"]:
                    final.extend([answer])
                elif tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[where_plc[0] - 1] in ["IN"]:
                    final.extend(str_tokens_answer[1:])
                else:
                    final.extend(["in", answer])
                final.extend(str_tokens_new_question[where_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        elif first_vb in do:
            output1 = str_tokens_new_question[:first_vb_plc]
            output2 = str_tokens_new_question[first_vb_plc + 1:]
            doc_output2 = nlp(list_to_str(output2))
            tokens_output2 = [token for token in doc_output2 if token.text != ""]
            str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
            dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
            pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
            root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
            root_plc = dep_tokens_output2.index("ROOT")
            be_before_root = False
            if tokens_output2[root_plc - 1].lemma_ == "be":
                be_before_root = True
            not_before_be_root = False
            if be_before_root and tokens_output2[root_plc - 2].lemma_ == "not":
                not_before_be_root = True
            if str_tokens_new_question[0] in ["Where", "where"]:
                root_is_vb = False
                for noun in ["NOUN", "PROPN"]:
                    if noun in pos_tokens_output2[:root_plc]:
                        root_is_vb = True
                tag = nltk.pos_tag(str_tokens_output2)[root_plc][1]
                if "VB" in tag:
                    root_is_vb = True
                if pos_tokens_output2[root_plc] == "VERB" or root_is_vb:
                    if first_vb in did:
                        this_tense = 0
                        if first_vb == "do":
                            this_tense = 1
                        elif first_vb == "does":
                            this_tense = 2
                        elif first_vb == "did":
                            this_tense = 3
                        final = []
                        this_verb = ""
                        if this_tense == 1 or this_tense == 0:
                            this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                        if this_tense == 2:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                  tense=PRESENT,
                                                  number=SG)
                        if this_tense == 3:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_, tense=PAST)
                        if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                            first_vb_plc + root_plc - 1] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                            final.extend([this_verb])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                        elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                            final.extend([this_verb])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                        else:
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                            final.extend([this_verb])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        final.pop()
                        after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                        if tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[-2] not in ["IN"]:
                            final.extend([answer])
                        elif tag_tokens_answer[0] not in ["IN"] and tag_tokens_new_question[-2] in ["IN"]:
                            final.extend([answer])
                        elif tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[-2] in ["IN"]:
                            final.extend(str_tokens_answer[1:])
                        else:
                            final.extend(["in", answer])
                        final.extend(after_where)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        if tokens_output2[root_plc - 1].lemma_ == "be":
                            root = str_tokens_output2[root_plc - 1]
                            root_plc -= 1
                        if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                            first_vb_plc + root_plc - 1] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc - 1:])
                        elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                        else:
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc + 1:])
                        final.pop()
                        after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                        if tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[-2] not in ["IN"]:
                            final.extend([answer])
                        elif tag_tokens_answer[0] not in ["IN"] and tag_tokens_new_question[-2] in ["IN"]:
                            final.extend([answer])
                        elif tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[-2] in ["IN"]:
                            final.extend(str_tokens_answer[1:])
                        else:
                            final.extend(["in", answer])
                        final.extend(after_where)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                else:
                    final = []
                    final.extend(str_tokens_new_question[2:])
                    final.pop()
                    if tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[-2] not in ["IN"]:
                        final.extend([answer])
                    elif tag_tokens_answer[0] not in ["IN"] and tag_tokens_new_question[-2] in ["IN"]:
                        final.extend([answer])
                    elif tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[-2] in ["IN"]:
                        final.extend(str_tokens_answer[1:])
                    else:
                        final.extend(["in", answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
            else:
                if first_vb in did:
                    this_tense = 0
                    if first_vb == "do":
                        this_tense = 1
                    elif first_vb == "does":
                        this_tense = 2
                    elif first_vb == "did":
                        this_tense = 3
                    final = []
                    this_verb = ""
                    if this_tense == 1 or this_tense == 0:
                        this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                    if this_tense == 2:
                        this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                              tense=PRESENT,
                                              number=SG)
                    if this_tense == 3:
                        this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_, tense=PAST)
                    if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                        first_vb_plc + root_plc - 1] == "ADV":
                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                        final.extend([this_verb])
                        final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                    elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                        final.extend([this_verb])
                        final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                    else:
                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                        final.extend([this_verb])
                        final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                    final.pop()
                    before_where = str_tokens_new_question[:where_plc[0]]
                    before_where[0] = before_where[0][0].lower() + before_where[0][1:]
                    after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                    final.extend(before_where)
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend(str_tokens_answer[1:])
                    else:
                        final.extend([answer])
                    final.extend(after_where)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                else:
                    if pos_tokens_output2[root_plc] != "VERB":
                        if "VERB" in pos_tokens_output2:
                            root_plc = pos_tokens_output2.index("VERB")
                            root = str_tokens_output2[root_plc]
                        else:
                            final = []
                            final.extend(str_tokens_new_question[:where_plc[0]])
                            if tag_tokens_answer[0] in ["IN"]:
                                final.extend(str_tokens_answer[1:])
                            else:
                                final.extend([answer])
                            final.extend(str_tokens_new_question[where_plc[0] + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                    final = []
                    if tokens_output2[root_plc - 1].lemma_ == "be":
                        root = str_tokens_output2[root_plc - 1]
                        root_plc -= 1
                    if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                        first_vb_plc + root_plc - 1] == "ADV":
                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                        final.extend([str_tokens_new_question[first_vb_plc]])
                        final.extend(str_tokens_new_question[first_vb_plc + root_plc - 1:])
                    elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                        final.extend([str_tokens_new_question[first_vb_plc]])
                        final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                    else:
                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                        final.extend([str_tokens_new_question[first_vb_plc]])
                        final.extend(str_tokens_new_question[first_vb_plc + root_plc + 1:])
                    final.pop()
                    before_where = str_tokens_new_question[:where_plc[0]]
                    before_where[0] = before_where[0][0].lower() + before_where[0][1:]
                    after_where = str_tokens_new_question[where_plc[0] + 1:first_vb_plc]
                    final.extend(before_where)
                    if tag_tokens_answer[0] in ["IN"]:
                        final.extend(str_tokens_answer[1:])
                    else:
                        final.extend([answer])
                    final.extend(after_where)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
        final = []
        final.extend(str_tokens_new_question[:where_plc[0]])
        if tag_tokens_answer[0] in ["IN"]:
            final.extend([answer])
        else:
            final.extend(["in", answer])
        final.extend(str_tokens_new_question[where_plc[0] + 1:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "."
        else:
            final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out


