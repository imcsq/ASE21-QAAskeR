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


class which(object):

    def generate(self, question, answer):
        try:
            return self.generate_statement(question, answer)
        except IndexError as e:
            return None

    def generate_statement(self, question, answer):
        if "WHich " in question:
            question = question.replace("WHich ", "which ")
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
        str_tokens_question = [token.text for token in doc_question if token.text != ""]
        have_comma = False
        all_comma = []
        all_which = []
        num = 0
        for token in tokens_question:
            if token.text == ",":
                all_comma.append(num)
                have_comma = True
            if token.text == "Which" or token.text == "which":
                all_which.append(num)
            num += 1
        small_question_start = 0
        have_comma_do = False
        if have_comma:
            for comma in all_comma:
                if all_which[0] > comma:
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
        which = []
        which_plc = []
        num = 0
        for word in tokens_new_question:
            if word.lemma_ == "which":
                which.append(word)
                which_plc.append(num)
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
            if str_tokens_new_question[0] in ["Which", "which"]:
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
            else:
                parent = []
                for word in tokens_new_question:
                    tree = []
                    child_to_list_node(word, tree)
                    for child in tree:
                        if child.lemma_ == "which":
                            parent.append(word)
                if parent == []:
                    final = []
                    final.extend(str_tokens_new_question[:which_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[which_plc[0] + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                parents = []
                for prt in parent:
                    for word in tokens_new_question:
                        if word.lemma_ == prt.lemma_:
                            parents.append(word)
                parent_tree = []
                tree_to_list_str(parent[0], parent_tree)
                if " " in parent_tree:
                    parent_tree.remove(" ")
                if "?" in parent_tree:
                    parent_tree.remove("?")
                what_tree_plc, what_tree = list_to_order(str_tokens_new_question, parent_tree)
                num = 0
                for word in what_tree:
                    if word in ["which", "Which"]:
                        what_tree = what_tree[num:]
                        what_tree_plc += num
                        break
                    num += 1

                IN_what_tree = list_to_str(what_tree)
                doc_what_tree = nlp(IN_what_tree)
                tag_what_tree = [token.tag_ for token in doc_what_tree if token.text != ""]
                num = 0
                for tag in tag_what_tree:
                    if tag == "IN" and what_tree[num] != "of":
                        what_tree = what_tree[:num - 1]
                        break
                    num += 1
                final = []
                final.extend(str_tokens_new_question[:what_tree_plc])
                final.extend([answer])
                final.extend(str_tokens_new_question[what_tree_plc + len(what_tree):])
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
        if str_tokens_new_question[-2] == "which":
            final = []
            final.extend(str_tokens_new_question[:which_plc[0]])
            if tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[which_plc[0] - 1] not in ["IN"]:
                final.extend([answer])
            elif tag_tokens_answer[0] not in ["IN"] and tag_tokens_new_question[which_plc[0] - 1] in ["IN"]:
                final.extend([answer])
            elif tag_tokens_answer[0] in ["IN"] and tag_tokens_new_question[which_plc[0] - 1] in ["IN"]:
                final.extend(str_tokens_answer[1:])
            else:
                final.extend(["in", answer])
            final.extend(str_tokens_new_question[which_plc[0] + 1:])
            final.pop()
            final_out = list_to_str(final)
            if have_comma_do:
                final_out = final_add + ", " + final_out + "."
            else:
                final_out = final_out[0].upper() + final_out[1:] + "."
            return final_out
        if first_vb in be:
            if str_tokens_new_question[0] in ["Which", "which"]:
                if tag_tokens_new_question[-2] == "IN" and "VB" not in tag_tokens_new_question[-3]:
                    final = []
                    final.extend(str_tokens_new_question[first_vb_plc + 1:-2])
                    final.extend([str_tokens_new_question[first_vb_plc]])
                    final.extend([str_tokens_new_question[-2]])
                    final.extend([answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                output1 = str_tokens_new_question[:first_vb_plc]
                doc_output1 = nlp(list_to_str(output1))
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                final = []
                after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                if "'s" in after_which:
                    s_plc = after_which.index("'s")
                    after_which = after_which[s_plc:]
                elif "IN" in tag_after_which:
                    in_plc = tag_after_which.index("IN")
                    after_which = after_which[in_plc:]
                else:
                    after_which = []
                if pos_tokens_new_question[first_vb_plc + 1] not in ["ADJ", "ADV", "ADJP", "VERB"] and \
                        pos_tokens_new_question[first_vb_plc + 2] not in ["VERB"]:
                    final.extend(str_tokens_new_question[first_vb_plc + 1:])
                    final.pop()
                    final.extend([first_vb])
                    final.extend([answer])
                    final.extend(after_which)
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                final.extend([answer])
                final.extend(after_which)
                final.extend(str_tokens_new_question[first_vb_plc:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
            else:
                final = []
                final.extend(str_tokens_new_question[:which_plc[0]])
                final.extend([answer])
                final.extend(str_tokens_new_question[which_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        elif first_vb in do:
            if str_tokens_new_question[0] in ["Which", "which"]:
                output1 = str_tokens_new_question[:first_vb_plc]
                doc_output1 = nlp(list_to_str(output1))
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                tag = nltk.pos_tag(str_tokens_output2)
                nltk_tag = [this_tag[1] for this_tag in tag]
                have_vb = False
                for this_tag in nltk_tag:
                    if "VB" in this_tag:
                        have_vb = True
                        root_plc = nltk_tag.index(this_tag)
                        root = str_tokens_output2[root_plc]
                if "VERB" not in pos_tokens_output2 and not have_vb or root_plc == 0 or first_vb in ["has", "had",
                                                                                                     "have"]:
                    final = []
                    after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                    tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                    if "'s" in after_which:
                        s_plc = after_which.index("'s")
                        after_which = after_which[s_plc:]
                    elif "IN" in tag_after_which:
                        in_plc = tag_after_which.index("IN")
                        after_which = after_which[in_plc:]
                    else:
                        after_which = []
                    final.extend(str_tokens_new_question[:which_plc[0]])
                    final.extend([answer])
                    final.extend(after_which)
                    final.extend(str_tokens_new_question[first_vb_plc:])
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
                        after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        if "'s" in after_which:
                            s_plc = after_which.index("'s")
                            after_which = after_which[s_plc:]
                        elif "IN" in tag_after_which:
                            in_plc = tag_after_which.index("IN")
                            after_which = after_which[in_plc:]
                        else:
                            after_which = []
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
                        final.extend([answer])
                        final.extend(after_which)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        if first_vb in would and pos_tokens_new_question[first_vb_plc + 1] in ["NOUN", "PROPN",
                                                                                               "PRON"] and "VERB" in pos_tokens_new_question[
                                                                                                                     first_vb_plc + 1:]:
                            final = []
                            vb_plc = pos_tokens_new_question[first_vb_plc + 1:].index("VERB") + first_vb_plc + 1
                            final.extend(str_tokens_new_question[first_vb_plc + 1:vb_plc])
                            final.extend([first_vb])
                            final.extend([str_tokens_new_question[vb_plc]])
                            final.extend([answer])
                            final.extend(str_tokens_new_question[vb_plc + 1:])
                            final.pop()
                            final.extend(str_tokens_new_question[which_plc[0] + 1:first_vb_plc])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        final = []
                        after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        if "'s" in after_which:
                            s_plc = after_which.index("'s")
                            after_which = after_which[s_plc:]
                        elif "IN" in tag_after_which:
                            in_plc = tag_after_which.index("IN")
                            after_which = after_which[in_plc:]
                        else:
                            after_which = []
                        root_be = False
                        if tokens_output2[root_plc - 1].lemma_ == "be":
                            root = str_tokens_output2[root_plc - 1]
                            root_plc -= 1
                            root_be = True
                        if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                            first_vb_plc + root_plc - 1] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if root_be:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc - 1:first_vb_plc + root_plc + 3])
                                if tag_tokens_new_question[first_vb_plc + root_plc + 3] == "IN":
                                    final.extend([str_tokens_new_question[first_vb_plc + root_plc + 3]])
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 4:])
                                else:
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                            else:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc - 1:first_vb_plc + root_plc + 2])
                                if tag_tokens_new_question[first_vb_plc + root_plc + 2] == "IN":
                                    final.extend([str_tokens_new_question[first_vb_plc + root_plc + 2]])
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                                else:
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if root_be:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc:first_vb_plc + root_plc + 3])
                                if tag_tokens_new_question[first_vb_plc + root_plc + 3] == "IN":
                                    final.extend([str_tokens_new_question[first_vb_plc + root_plc + 3]])
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 4:])
                                else:
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                            else:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc:first_vb_plc + root_plc + 2])
                                if tag_tokens_new_question[first_vb_plc + root_plc + 2] == "IN":
                                    final.extend([str_tokens_new_question[first_vb_plc + root_plc + 2]])
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                                else:
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        else:
                            if root_be:
                                final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                                final.extend([str_tokens_new_question[first_vb_plc]])
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc + 1:first_vb_plc + root_plc + 3])
                                if tag_tokens_new_question[first_vb_plc + root_plc + 3] == "IN":
                                    final.extend([str_tokens_new_question[first_vb_plc + root_plc + 3]])
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 4:])
                                else:
                                    final.extend([answer])
                                    final.extend(after_which)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                            else:
                                if str_tokens_new_question[first_vb_plc] in would:
                                    final.extend(str_tokens_new_question[:which_plc[0]])
                                    if str_tokens_new_question[which_plc[0] + 1] == str_tokens_answer[-1]:
                                        final.extend(str_tokens_answer[:-1])
                                    else:
                                        final.extend([answer])
                                    final.extend(str_tokens_new_question[which_plc[0] + 1:])
                                else:
                                    final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                                    final.extend([str_tokens_new_question[first_vb_plc]])
                                    final.extend(
                                        str_tokens_new_question[
                                        first_vb_plc + root_plc + 1:first_vb_plc + root_plc + 2])
                                    if tag_tokens_new_question[first_vb_plc + root_plc + 2] == "IN":
                                        final.extend([str_tokens_new_question[first_vb_plc + root_plc + 2]])
                                        final.extend([answer])
                                        final.extend(after_which)
                                        final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                                    else:
                                        final.extend([answer])
                                        final.extend(after_which)
                                        final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
            else:
                output1 = str_tokens_new_question[:first_vb_plc]
                doc_output1 = nlp(list_to_str(output1))
                output2 = str_tokens_new_question[first_vb_plc + 1:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                tag = nltk.pos_tag(str_tokens_output2)
                nltk_tag = [this_tag[1] for this_tag in tag]
                have_vb = False
                for this_tag in nltk_tag:
                    if "VB" in this_tag:
                        have_vb = True
                        root_plc = nltk_tag.index(this_tag)
                        root = str_tokens_output2[root_plc]
                if "VERB" not in pos_tokens_output2 and not have_vb or root_plc == 0 or first_vb in ["has", "had",
                                                                                                     "have"] or \
                        which_plc[0] > first_vb_plc:
                    final = []
                    after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                    tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                    if "'s" in after_which:
                        s_plc = after_which.index("'s")
                        after_which = after_which[s_plc:]
                    elif "IN" in tag_after_which:
                        in_plc = tag_after_which.index("IN")
                        after_which = after_which[in_plc:]
                    else:
                        after_which = []
                    if which_plc[0] < first_vb_plc:
                        final.extend(str_tokens_new_question[first_vb_plc + 1:])
                        final.pop()
                        before = str_tokens_new_question[:which_plc[0]]
                        before[0] = before[0][0].lower() + before[0][1:]
                        final.extend(before)
                        final.extend([answer])
                        final.extend(after_which)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final.extend(str_tokens_new_question[:which_plc[0]])
                        final.extend([answer])
                        final.extend(str_tokens_new_question[which_plc[0] + 1:])
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
                        before = str_tokens_new_question[:which_plc[0]]
                        before[0] = before[0][0].lower() + before[0][1:]
                        after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        if "'s" in after_which:
                            s_plc = after_which.index("'s")
                            after_which = after_which[s_plc:]
                        elif "IN" in tag_after_which:
                            in_plc = tag_after_which.index("IN")
                            after_which = after_which[in_plc:]
                        else:
                            after_which = []
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
                        final.extend(before)
                        final.extend([answer])
                        final.extend(after_which)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
                        final = []
                        before = str_tokens_new_question[:which_plc[0]]
                        before[0] = before[0][0].lower() + before[0][1:]
                        after_which = str_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        tag_after_which = tag_tokens_new_question[which_plc[0] + 1:first_vb_plc]
                        if "'s" in after_which:
                            s_plc = after_which.index("'s")
                            after_which = after_which[s_plc:]
                        elif "IN" in tag_after_which:
                            in_plc = tag_after_which.index("IN")
                            after_which = after_which[in_plc:]
                        else:
                            after_which = []
                        root_be = False
                        if tokens_output2[root_plc - 1].lemma_ == "be":
                            root = str_tokens_output2[root_plc - 1]
                            root_plc -= 1
                            root_be = True
                        if pos_tokens_new_question[first_vb_plc + root_plc] == "ADV" and pos_tokens_new_question[
                            first_vb_plc + root_plc - 1] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if root_be:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc - 1:first_vb_plc + root_plc + 3])
                                final.extend([answer])
                                final.extend(after_which)
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                            else:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc - 1:first_vb_plc + root_plc + 2])
                                final.extend([answer])
                                final.extend(after_which)
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        elif pos_tokens_new_question[first_vb_plc + root_plc] == "ADV":
                            final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if root_be:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc:first_vb_plc + root_plc + 3])
                                final.extend([answer])
                                final.extend(after_which)
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                            else:
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc:first_vb_plc + root_plc + 2])
                                final.extend([answer])
                                final.extend(after_which)
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        else:
                            if root_be:
                                final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                                final.extend([str_tokens_new_question[first_vb_plc]])
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc + 1:first_vb_plc + root_plc + 3])
                                final.extend([answer])
                                final.extend(after_which)
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 3:])
                            else:
                                final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc + 1])
                                final.extend([str_tokens_new_question[first_vb_plc]])
                                final.extend(
                                    str_tokens_new_question[first_vb_plc + root_plc + 1:first_vb_plc + root_plc + 2])
                                final.extend([answer])
                                final.extend(after_which)
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc + 2:])
                        final.pop()
                        final.extend(before)
                        final.extend([answer])
                        final.extend(after_which)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
        final = []
        final.extend(str_tokens_new_question[:which_plc[0]])
        final.extend([answer])
        final.extend(str_tokens_new_question[which_plc[0] + 1:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "."
        else:
            final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out


