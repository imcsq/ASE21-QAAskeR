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


class how(object):

    def generate(self, question, answer):
        try:
            return self.generate_statement(question, answer)
        except IndexError as e:
            return None

    def generate_statement(self, question, answer):
        if "HOw" in question:
            question = question.replace("HOw", "how")
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
        pos_tokens_answer = [token.pos_ for token in doc_answer if token.text != ""]
        str_tokens_question = [token.text for token in doc_question if token.text != ""]
        have_comma = False
        all_comma = []
        all_how = []
        num = 0
        for token in tokens_question:
            if token.text == ",":
                all_comma.append(num)
                have_comma = True
            if token.lemma_ == "how":
                all_how.append(num)
            num += 1
        small_question_start = 0
        have_comma_do = False
        if have_comma:
            for comma in all_comma:
                if all_how[0] > comma:
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
        how = []
        how_plc = []
        num = 0
        for word in tokens_new_question:
            if word.lemma_ == "how":
                how.append(word)
                how_plc.append(num)
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
            final.extend(str_tokens_new_question[:how_plc[0]])
            final.extend([answer])
            if pos_tokens_new_question[1] in ["ADJ", "ADV", "ADJP"]:
                final.extend(str_tokens_new_question[how_plc[0] + 2:])
            else:
                final.extend(str_tokens_new_question[how_plc[0] + 1:])
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
            if str_tokens_new_question[0] in ["How", "how"]:
                if pos_tokens_new_question[1] in ["ADJ", "ADV", "ADJP"]:
                    if "there" in str_tokens_new_question:
                        if str_tokens_new_question.index("there") == vbs_plc[0] + 1:
                            how_adj = str_tokens_new_question[:2]
                            answer_add = str_tokens_new_question[2:first_vb_plc]
                            there_plc = str_tokens_new_question.index("there")
                            final = []
                            final.extend([str_tokens_new_question[there_plc]])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend([answer])
                            final.extend(answer_add)
                            final.extend(str_tokens_new_question[there_plc + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                    if str_tokens_new_question[2] in be:
                        output2 = str_tokens_new_question[first_vb_plc + 1:]
                        doc_output2 = nlp(list_to_str(output2))
                        tokens_output2 = [token for token in doc_output2 if token.text != ""]
                        str_tokens_output2 = [token.text for token in doc_output2 if
                                              token.text != ""]
                        dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                        pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                        root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                        root_plc = dep_tokens_output2.index("ROOT")
                        if pos_tokens_output2[root_plc] == "VERB" and root_plc != 0:
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + 1 + root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[first_vb_plc + 1 + root_plc:])
                            final.pop()
                            final.extend([answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        final = []
                        final.extend(str_tokens_new_question[3:])
                        final.pop()
                        final.extend([str_tokens_new_question[2]])
                        final.extend([answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    final = []
                    final.extend([answer])
                    final.extend(str_tokens_new_question[2:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                elif str_tokens_new_question[1] in be:
                    output2 = str_tokens_new_question[first_vb_plc + 1:]
                    doc_output2 = nlp(list_to_str(output2))
                    tokens_output2 = [token for token in doc_output2 if token.text != ""]
                    str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                    dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                    pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                    root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                    root_plc = dep_tokens_output2.index("ROOT")
                    if pos_tokens_output2[root_plc] in ["NOUN", "PROPN"]:
                        acl_plc = []
                        appos_plc = []
                        num = -1
                        for dep in dep_tokens_output2:
                            num += 1
                            if dep == "acl":
                                acl_plc.append(num)
                            if dep == "appos":
                                appos_plc.append(num)
                        if len(acl_plc):
                            final = []
                            if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                                first_vb_plc + root_plc - 1] == "ADV":
                                final.extend(str_tokens_new_question[2:first_vb_plc + root_plc - 1])
                                final.extend([str_tokens_new_question[1]])
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc - 1:])
                            elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                                final.extend(str_tokens_new_question[2:first_vb_plc + root_plc])
                                final.extend([str_tokens_new_question[1]])
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                            else:
                                final.extend(str_tokens_new_question[2:first_vb_plc + root_plc + 1])
                                final.extend([str_tokens_new_question[1]])
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 1:])
                            final.pop()
                            if pos_tokens_answer == ["ADV"]:
                                final.extend([answer])
                            elif "by" in str_tokens_answer or "By" in str_tokens_answer:
                                final.extend([answer])
                            else:
                                final.extend(["by", answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        elif len(appos_plc):
                            appos = tokens_output2[appos_plc[0]]
                            appos_tree = []
                            tree_to_list_str(appos, appos_tree)
                            appos_start, appos_tree_order = list_to_order(str_tokens_output2, appos_tree)
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + appos_start + 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[first_vb_plc + appos_start + 1:])
                            final.pop()
                            if pos_tokens_answer == ["ADV"]:
                                final.extend([answer])
                            elif "by" in str_tokens_answer or "By" in str_tokens_answer:
                                final.extend([answer])
                            else:
                                final.extend(["by", answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if pos_tokens_new_question[real_root_plc] == "ADJ":
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:real_root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[real_root_plc:])
                            final.pop()
                            if pos_tokens_answer == ["ADV"]:
                                final.extend([answer])
                            elif "by" in str_tokens_answer or "By" in str_tokens_answer:
                                final.extend([answer])
                            else:
                                final.extend(["by", answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if "VERB" in pos_tokens_new_question[first_vb_plc + 1:]:
                            num = -1
                            for pos in pos_tokens_new_question[first_vb_plc + 1:]:
                                num += 1
                                if pos == "VERB":
                                    root_plc = num + first_vb_plc + 1
                                    root = str_tokens_new_question[num + first_vb_plc + 1]
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[root_plc:])
                            final.pop()
                            if pos_tokens_answer == ["ADV"]:
                                final.extend([answer])
                            elif "by" in str_tokens_answer or "By" in str_tokens_answer:
                                final.extend([answer])
                            else:
                                final.extend(["by", answer])
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
                        final.extend([answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                            first_vb_plc + root_plc - 1] == "ADV":
                            final.extend(str_tokens_new_question[2:first_vb_plc + root_plc - 1])
                            final.extend([str_tokens_new_question[1]])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc - 1:])
                        elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                            final.extend(str_tokens_new_question[2:first_vb_plc + root_plc])
                            final.extend([str_tokens_new_question[1]])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                        else:
                            final.extend(str_tokens_new_question[2:first_vb_plc + root_plc + 1])
                            final.extend([str_tokens_new_question[1]])
                            final.extend(str_tokens_new_question[first_vb_plc + root_plc + 1:])
                        final.pop()
                        if pos_tokens_answer == ["ADV"]:
                            final.extend([answer])
                        elif "by" in str_tokens_answer:
                            final.extend([answer])
                        else:
                            if tag_tokens_new_question[-2] == "IN":
                                final.extend([answer])
                            else:
                                final.extend(["by", answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                else:
                    final = []
                    final.extend(str_tokens_new_question[how_plc[0] + 1:])
                    final.pop()
                    if pos_tokens_answer == ["ADV"]:
                        final.extend([answer])
                    elif "by" in str_tokens_answer:
                        final.extend([answer])
                    else:
                        if tag_tokens_new_question[-2] == "IN":
                            final.extend([answer])
                        else:
                            final.extend(["by", answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
            else:
                if first_vb_plc < how_plc[0]:
                    final = []
                    final.extend(str_tokens_new_question[:how_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[how_plc[0] + 2:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if pos_tokens_new_question[how_plc[0] + 1] in ["ADJ", "ADV", "ADJP"]:
                    output2 = str_tokens_new_question[first_vb_plc + 1:]
                    doc_output2 = nlp(list_to_str(output2))
                    tokens_output2 = [token for token in doc_output2 if token.text != ""]
                    str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                    dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                    pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                    root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                    root_plc = dep_tokens_output2.index("ROOT")
                    if pos_tokens_output2[root_plc] == "VERB":
                        between_vb_and_ed = pos_tokens_output2[:root_plc]
                    else:
                        between_vb_and_ed = []
                    need_change = False
                    for pos in between_vb_and_ed:
                        if pos in ["NOUN", "PROPN"]:
                            need_change = True
                    if need_change:
                        final = []
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
                        start = str_tokens_new_question[:how_plc[0]]
                        start[0] = start[0][0].lower() + start[0][1:]
                        final.extend(start)
                        final.extend([answer])
                        after_answer = str_tokens_new_question[how_plc[0] + 2:first_vb_plc]
                        for word in str_tokens_answer:
                            if word in after_answer:
                                after_answer.remove(word)
                                break
                        final.extend(after_answer)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        final.extend(str_tokens_new_question[:how_plc[0]])
                        after_answer = str_tokens_new_question[how_plc[0] + 2]
                        final.extend([answer])
                        if after_answer in answer:
                            final.extend(str_tokens_new_question[how_plc[0] + 3:])
                        else:
                            final.extend(str_tokens_new_question[how_plc[0] + 2:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                if pos_tokens_output2[root_plc] in ["NOUN", "PROPN"]:
                    for pos in pos_tokens_output2:
                        if pos == "VERB":
                            root_plc = pos_tokens_output2.index(pos)
                            break
                    final = []
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
                    start = str_tokens_new_question[:how_plc[0]]
                    start[0] = start[0][0].lower() + start[0][1:]
                    final.extend(start)
                    final.extend([answer])
                    after_answer = str_tokens_new_question[how_plc[0] + 1:first_vb_plc]
                    for word in str_tokens_answer:
                        if word in after_answer:
                            after_answer.remove(word)
                            break
                    final.extend(after_answer)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                else:
                    final = []
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
                    start = str_tokens_new_question[:how_plc[0]]
                    start[0] = start[0][0].lower() + start[0][1:]
                    final.extend(start)
                    final.extend([answer])
                    after_answer = str_tokens_new_question[how_plc[0] + 1:first_vb_plc]
                    for word in str_tokens_answer:
                        if word in after_answer:
                            after_answer.remove(word)
                            break
                    final.extend(after_answer)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
        if first_vb in do:
            if str_tokens_new_question[0] in ["How", "how"]:
                if pos_tokens_new_question[first_vb_plc + 1] == "VERB" and str_tokens_new_question[first_vb_plc + 1] == \
                        tokens_new_question[first_vb_plc + 1].lemma_:
                    final = []
                    final.extend([answer])
                    if pos_tokens_new_question[1] in ["ADJ", "ADV", "ADJP"]:
                        final.extend(str_tokens_new_question[2:first_vb_plc])
                    else:
                        final.extend(str_tokens_new_question[1:first_vb_plc])
                    final.extend(str_tokens_new_question[first_vb_plc:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if pos_tokens_new_question[1] in ["ADJ", "ADV", "ADJP"]:
                    output1 = str_tokens_new_question[:first_vb_plc]
                    output2 = str_tokens_new_question[first_vb_plc + 1:]
                    doc_output2 = nlp(list_to_str(output2))
                    tokens_output2 = [token for token in doc_output2 if token.text != ""]
                    str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                    dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                    pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                    tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                    root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                    root_plc = dep_tokens_output2.index("ROOT")
                    if tokens_output2[root_plc].text != tokens_output2[root_plc].lemma_:
                        num = -1
                        for pos in pos_tokens_output2:
                            num += 1
                            if pos == "VERB" and tokens_output2[num].text == tokens_output2[num].lemma_:
                                root = str_tokens_output2[num]
                                root_plc = num
                                break
                    is_adv = False
                    dobj_plc = []
                    num = -1
                    for dep in dep_tokens_output2:
                        num += 1
                        if dep == "dobj":
                            dobj_plc.append(num)
                            break
                    if len(dobj_plc) != 0 and dobj_plc[0] > root_plc:
                        if "IN" not in tag_tokens_output2[root_plc:dobj_plc[0]] and "aux" not in dep_tokens_output2[
                                                                                                 root_plc:dobj_plc[0]]:
                            is_adv = True
                    if not is_adv:
                        if first_vb in did:
                            this_tense = 0
                            if first_vb == "do":
                                this_tense = 1
                            elif first_vb == "does":
                                this_tense = 2
                            elif first_vb == "did":
                                this_tense = 3
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                            this_verb = ""
                            if this_tense == 1 or this_tense == 0:
                                this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                            if this_tense == 2:
                                this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                      tense=PRESENT,
                                                      number=SG)
                            if this_tense == 3:
                                this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                      tense=PAST)
                            final.extend([this_verb])
                            final.extend([answer])
                            final.extend(output1[2:])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        else:
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                            final.extend([first_vb])
                            final.extend([str_tokens_new_question[len(output1) + root_plc + 1]])
                            final.extend([answer])
                            final.extend(output1[2:])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                            final.pop()
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
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                            this_verb = ""
                            if this_tense == 1 or this_tense == 0:
                                this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                            if this_tense == 2:
                                this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                      tense=PRESENT,
                                                      number=SG)
                            if this_tense == 3:
                                this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                      tense=PAST)
                            final.extend([this_verb])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                            final.pop()
                            in_normal = "by"
                            if output1 == ["How", "long", "ago"] or output1 == ["how", "long", "ago"]:
                                in_normal = ""
                            if output1 == ["How", "long"] or output1 == ["how", "long"]:
                                in_normal = "for"
                            if tag_tokens_output2[-2] == "IN":
                                if tag_tokens_answer[0] == "IN":
                                    final.extend(str_tokens_answer[1:])
                                else:
                                    final.extend(str_tokens_answer)
                            else:
                                if pos_tokens_answer == ["ADV"]:
                                    final.extend([answer])
                                elif tag_tokens_answer[0] == "IN":
                                    final.extend(str_tokens_answer)
                                else:
                                    final.extend([in_normal, answer])
                            if list_to_str(output1[2:]) not in answer:
                                final.extend(output1[2:])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        else:
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                            final.extend([first_vb])
                            final.extend([str_tokens_new_question[len(output1) + root_plc + 1]])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                            final.pop()
                            in_normal = "by"
                            if output1 == ["How", "long", "ago"] or output1 == ["how", "long", "ago"]:
                                in_normal = ""
                            if output1 == ["How", "long"] or output1 == ["how", "long"]:
                                in_normal = "for"
                            if tag_tokens_output2[-2] == "IN":
                                if tag_tokens_answer[0] == "IN":
                                    final.extend(str_tokens_answer[1:])
                                else:
                                    final.extend(str_tokens_answer)
                            else:
                                if pos_tokens_answer == ["ADV"]:
                                    final.extend([answer])
                                elif tag_tokens_answer[0] == "IN":
                                    final.extend(str_tokens_answer)
                                else:
                                    final.extend([in_normal, answer])
                            if list_to_str(output1[2:]) not in answer:
                                final.extend(output1[2:])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                else:
                    output1 = str_tokens_new_question[:first_vb_plc]
                    output2 = str_tokens_new_question[first_vb_plc + 1:]
                    doc_output2 = nlp(list_to_str(output2))
                    tokens_output2 = [token for token in doc_output2 if token.text != ""]
                    str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                    dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                    pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                    tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                    root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                    root_plc = dep_tokens_output2.index("ROOT")
                    if tokens_output2[root_plc].text != tokens_output2[root_plc].lemma_:
                        num = -1
                        for pos in pos_tokens_output2:
                            num += 1
                            if pos == "VERB" and tokens_output2[num].text == tokens_output2[num].lemma_:
                                root = str_tokens_output2[num]
                                root_plc = num
                                break
                    if first_vb in did:
                        this_tense = 0
                        if first_vb == "do":
                            this_tense = 1
                        elif first_vb == "does":
                            this_tense = 2
                        elif first_vb == "did":
                            this_tense = 3
                        final = []
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        this_verb = ""
                        if this_tense == 1 or this_tense == 0:
                            this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                        if this_tense == 2:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                  tense=PRESENT,
                                                  number=SG)
                        if this_tense == 3:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_, tense=PAST)
                        final.extend([this_verb])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        in_normal = "by"
                        if output1 == ["How", "long", "ago"] or output1 == ["how", "long", "ago"]:
                            in_normal = ""
                        if output1 == ["How", "long"] or output1 == ["how", "long"]:
                            in_normal = "for"
                        if tag_tokens_output2[-2] == "IN":
                            if tag_tokens_answer[0] == "IN":
                                final.extend(str_tokens_answer[1:])
                            else:
                                final.extend(str_tokens_answer)
                        else:
                            if pos_tokens_answer == ["ADV"]:
                                final.extend([answer])
                            elif tag_tokens_answer[0] == "IN":
                                final.extend(str_tokens_answer)
                            else:
                                final.extend([in_normal, answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        final.extend([first_vb])
                        final.extend([str_tokens_new_question[len(output1) + root_plc + 1]])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        in_normal = "by"
                        if output1 == ["How", "long", "ago"] or output1 == ["how", "long", "ago"]:
                            in_normal = ""
                        if output1 == ["How", "long"] or output1 == ["how", "long"]:
                            in_normal = "for"
                        if tag_tokens_output2[-2] == "IN":
                            if tag_tokens_answer[0] == "IN":
                                final.extend(str_tokens_answer[1:])
                            else:
                                final.extend(str_tokens_answer)
                        else:
                            if pos_tokens_answer == ["ADV"]:
                                final.extend([answer])
                            elif tag_tokens_answer[0] == "IN":
                                final.extend(str_tokens_answer)
                            else:
                                final.extend([in_normal, answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
            else:
                if pos_tokens_new_question[first_vb_plc + 1] == "VERB" and str_tokens_new_question[first_vb_plc + 1] == \
                        tokens_new_question[first_vb_plc + 1].lemma_:
                    final = []
                    final.extend(str_tokens_new_question[:how_plc[0]])
                    if pos_tokens_new_question[how_plc[0] + 1] in ["ADJ", "ADV", "ADJP"]:
                        final.extend([answer])
                        final.extend(str_tokens_new_question[how_plc[0] + 2:])
                    else:
                        final.extend([answer])
                        final.extend(str_tokens_new_question[how_plc[0] + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                output1 = str_tokens_new_question[:first_vb_plc]
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                if how_plc[0] != 0:
                    if first_vb in did:
                        this_tense = 0
                        if first_vb == "do":
                            this_tense = 1
                        elif first_vb == "does":
                            this_tense = 2
                        elif first_vb == "did":
                            this_tense = 3
                        final = []
                        final.extend(str_tokens_new_question[:how_plc[0]])
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        this_verb = ""
                        if this_tense == 1 or this_tense == 0:
                            this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                        if this_tense == 2:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                  tense=PRESENT,
                                                  number=SG)
                        if this_tense == 3:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_, tense=PAST)
                        final.extend([this_verb])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        if pos_tokens_new_question[how_plc[0] + 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend([answer])
                            final.extend(str_tokens_new_question[how_plc[0] + 2:first_vb_plc])
                        else:
                            final.extend([answer])
                            final.extend(str_tokens_new_question[how_plc[0] + 1:first_vb_plc])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        final.extend(str_tokens_new_question[:how_plc[0]])
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        final.extend([first_vb])
                        final.extend([str_tokens_new_question[len(output1) + root_plc + 1]])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        if pos_tokens_new_question[how_plc[0] + 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend([answer])
                            final.extend(str_tokens_new_question[how_plc[0] + 2:first_vb_plc])
                        else:
                            final.extend([answer])
                            final.extend(str_tokens_new_question[how_plc[0] + 1:first_vb_plc])
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
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        this_verb = ""
                        if this_tense == 1 or this_tense == 0:
                            this_verb = str_tokens_new_question[len(output1) + root_plc + 1]
                        if this_tense == 2:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_,
                                                  tense=PRESENT,
                                                  number=SG)
                        if this_tense == 3:
                            this_verb = conjugate(tokens_new_question[len(output1) + root_plc + 1].lemma_, tense=PAST)
                        final.extend([this_verb])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        how_what = output1[0]
                        how_what = how_what[0].lower() + how_what[1:]
                        final.extend([how_what])
                        if pos_tokens_answer == ["ADV"]:
                            final.extend([answer])
                        elif tag_tokens_answer[0] == "IN":
                            final.extend([list_to_str(str_tokens_answer[1:])])
                        else:
                            final.extend([answer])
                        final.extend(output1[3:])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                        final.extend([first_vb])
                        final.extend([str_tokens_new_question[len(output1) + root_plc + 1]])
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        how_what = output1[0]
                        how_what = how_what[0].lower() + how_what[1:]
                        final.extend([how_what])
                        if pos_tokens_answer == ["ADV"]:
                            final.extend([answer])
                        elif tag_tokens_answer[0] == "IN":
                            final.extend([list_to_str(str_tokens_answer[1:])])
                        else:
                            final.extend([answer])
                        final.extend(output1[3:])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
        final = []
        final.extend(str_tokens_new_question[:how_plc[0]])
        if pos_tokens_new_question[how_plc[0] + 1] in ["ADJ", "ADV", "ADJP"]:
            final.extend([answer])
            final.extend(str_tokens_new_question[how_plc[0] + 2:])
        else:
            final.extend([answer])
            final.extend(str_tokens_new_question[how_plc[0] + 1:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "."
        else:
            final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out
