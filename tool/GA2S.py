import spacy
import string
import nltk
import argparse
import numpy as np
from tqdm import tqdm
from nltk import Tree
from benepar.spacy_plugin import BeneparComponent
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from pattern.text.en import conjugate, lemma, lexeme, PRESENT, INFINITIVE, PAST, FUTURE, SG, PLURAL, PROGRESSIVE

boolean_set = {"be", "do", "will", "can", "should", "may", "have", "must", "would", "am", "could", "shell", "might"}
WH_set = {"how", "what", "who", "why", "whose", "where", "when", "which"}


def order(child_list, sent_list):
    order_list = []
    start_plc = 0
    for part in sent_list:
        if part in [["that"], ["which"], ["who"]]:
            start_plc = sent_list.index(part)
    if start_plc == 0:
        return [], 0, 0
    num = 0
    for part in sent_list[start_plc:]:
        if len(order_list) == len(child_list):
            return order_list, start_plc, num
        if len(child_list) > len(sent_list) - start_plc:
            return [], 0, 0
        order_list.extend(part)
        num += 1
    return [], 0, 0


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


def tense(word, nlp):
    word_ = nlp(word)
    word_lemma = word_[0].lemma_
    word_did = conjugate(word_lemma, tense=PAST)
    word_does = conjugate(word_lemma, tense=PRESENT, number=SG)
    if word == word_did:
        return 1
    elif word == word_does:
        return 2
    else:
        return 3


def list_to_str(a_list):
    str_out = TreebankWordDetokenizer().detokenize(a_list)
    return str_out


def list_to_str2(a_list):
    str_out = ""
    for i in a_list:
        for j in i:
            str_out = str_out + " " + j
    return str_out[1:]


def shuchu(node, list):
    if isinstance(node, str):
        children = []
        children.append(node)
        list.append(children)
    else:
        if_print = True
        for child in node:
            if len(child) != 1 or not isinstance(child[0], str):
                if_print = False
        if if_print:
            children = []
            for i in node:
                children.append(i[0])
            list.append(children)
        else:
            for i in node:
                shuchu(i, list)


def intersection(part, answer):
    this_part = []
    this_answer = []
    for i in part:
        this_part.append(i.lower())
    for i in answer:
        this_answer.append(i.lower())
    if set(this_answer) <= set(this_part):
        return True
    return False


def is_noun_from_S2W(list_1, pos_list, str_list, str_tokens_answer):
    if_noun = True
    num = -1
    if list_1 == ["the"] or list_1 == ["The"]:
        return True
    if list_1[0] == "the" or list_1[0] == "The":
        return True
    for i in list_1:
        num += 1
        if '-' in i and i != "-":
            continue
        if i not in str_list:
            continue
        plc = str_list.index(i)
        pos = pos_list[plc]
        if num == len(list_1) - 1:
            if i != "." and pos == "PUNCT":
                continue
        if pos not in ["NOUN", "PROPN", "PRON", "ADJ", "ADJP"] and i not in ["'s", "'", "s", "-", "I", "IV", "VI",
                                                                             "well"] and i[-3:] != "ing":
            if_noun = False
    if "-" in list_1:
        if_noun = True
    return if_noun


def is_noun(list_0, list_1, pos_list):
    if_noun = True
    num = -1
    for i in list_1:
        num += 1
        if pos_list[len(list_0) + 1 + num] not in ["NOUN", "PROPN", "PRON"]:
            if_noun = False
    return if_noun


def is_adj(list_1, pos_list, str_list, str_tokens_answer):
    if_adj = True
    if list_1 == ["by"]:
        return False
    num = -1
    if list_1[0] == "the" or list_1[0] == "The":
        num = 0
        for i in list_1[1:]:
            num += 1
            if '-' in i and i != "-":
                continue
            plc = str_list.index(i)
            pos = pos_list[plc]
            if pos in ["NOUN", "PROPN", "PRON"]:
                return False
        return True
    for i in list_1:
        num += 1
        if '-' in i and i != "-":
            continue
        if i not in str_list:
            continue
        plc = str_list.index(i)
        pos = pos_list[plc]
        if pos not in ["ADJ", "ADJP", "DET", "CCONJ"] and i not in ["'s", "'", "s", "a", "an", "A", "-", "I", "IV",
                                                                    "VI", "well"] and i[-3:] != "ing":
            if_adj = False
    return if_adj


def boolean(question, answer, nlp):
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
    tag_tokens_question = [token.tag_ for token in doc_question if token.text != ""]
    str_tokens_question = [token.text for token in doc_question if token.text != ""]
    str_tokens_question[0] = str_tokens_question[0].lower()
    lemma_tokens_question = [token.lemma_ for token in doc_question if token.text != ""]
    tokens_answer = [token for token in doc_answer if token.text != ""]
    tag_tokens_answer = [token.tag_ for token in doc_answer if token.text != ""]
    dep_tokens_answer = [token.dep_ for token in doc_answer if token.text != ""]
    pos_tokens_answer = [token.pos_ for token in doc_answer if token.text != ""]
    str_tokens_answer = [token.text for token in doc_answer if token.text != ""]
    if "or" in lemma_tokens_question and answer not in ["yes", "no"] and intersection(str_tokens_question,
                                                                                      str_tokens_answer):
        doc = nlp(question)
        sent = list(doc.sents)[0]
        parse_str = sent._.parse_string
        t = Tree.fromstring(parse_str)
        this_one = []
        shuchu(t, this_one)
        num = -1
        if_ctn = True
        while if_ctn:
            num += 1
            if this_one[num] == ["-"]:
                this_one[num].extend(this_one[num + 1])
                this_one[num + 1] = []
                this_one[num - 1].extend(this_one[num])
                this_one[num] = []
                this_one.remove([])
                this_one.remove([])
                num -= 1
            if num == len(this_one) - 1:
                if_ctn = False
        num = -1
        if_ctn = True
        while if_ctn:
            num += 1
            if this_one[num - 1] == ["'"] and this_one[num + 1] == ["'"]:
                this_one[num - 1].extend(this_one[num])
                this_one[num - 1].extend(this_one[num + 1])
                this_one[num] = []
                this_one[num + 1] = []
                this_one[num] = []
                this_one.remove([])
                this_one.remove([])
                num -= 1
            if num == len(this_one) - 2:
                if_ctn = False
        num = -1
        if_ctn = True
        while if_ctn:
            num += 1
            if this_one[num] == ["or"]:
                this_one[num].extend(this_one[num + 1])
                this_one[num + 1] = []
                this_one[num - 1].extend(this_one[num])
                this_one[num] = []
                this_one.remove([])
                this_one.remove([])
                num -= 1
            if num == len(this_one) - 1:
                if_ctn = False
        num = -1
        if_ctn = True
        while if_ctn:
            num += 1
            if this_one[num] == ["a"] or this_one[num] == ["an"]:
                this_one[num].extend(this_one[num + 1])
                this_one[num + 1] = []
                this_one.remove([])
                num -= 1
            if num == len(this_one) - 1:
                if_ctn = False
        for part in this_one:
            if "or" in part and part != ["or"]:
                part_plc = this_one.index(part)
                vb = this_one[0]
                vb[0] = vb[0][0].lower() + vb[0][1:]
                word_before_be_plc = str_tokens_question.index(this_one[part_plc - 1][0])
                word_before_be_plc2 = str_tokens_question.index(this_one[part_plc - 2][0])
                if part_plc == 1:
                    part_1 = this_one[1:part_plc]
                    part_2 = this_one[part_plc + 1:]
                    new_one = part_1
                    new_one.extend([str_tokens_answer])
                    new_one.extend([vb])
                    new_one.extend(part_2)
                    final_out = list_to_str2(new_one)
                    final_out = final_out[0].upper() + final_out[1:-2] + "."
                    return final_out
                if tag_tokens_question[word_before_be_plc] == "IN" and pos_tokens_question[
                    word_before_be_plc2] == "VERB":
                    vb_in = [this_one[part_plc - 2][0], this_one[part_plc - 1][0]]
                    part_1 = this_one[1:part_plc - 2]
                    part_2 = this_one[part_plc + 1:]
                    new_one = part_1
                    new_one.extend([vb])
                    new_one.append(vb_in)
                    new_one.extend([str_tokens_answer])
                    new_one.extend(part_2)
                    final_out = list_to_str2(new_one)
                    final_out = final_out[0].upper() + final_out[1:-2] + "."
                    return final_out
                elif tag_tokens_question[word_before_be_plc] == "IN" or pos_tokens_question[
                    word_before_be_plc] == "VERB":
                    vb_in = [this_one[part_plc - 1][0]]
                    part_1 = this_one[1:part_plc - 1]
                    part_2 = this_one[part_plc + 1:]
                    new_one = part_1
                    new_one.extend([vb])
                    new_one.append(vb_in)
                    new_one.extend([str_tokens_answer])
                    new_one.extend(part_2)
                    final_out = list_to_str2(new_one)
                    final_out = final_out[0].upper() + final_out[1:-2] + "."
                    return final_out
                part_1 = this_one[1:part_plc]
                part_2 = this_one[part_plc + 1:]
                new_one = part_1
                new_one.extend([vb])
                new_one.extend([str_tokens_answer])
                new_one.extend(part_2)
                final_out = list_to_str2(new_one)
                final_out = final_out[0].upper() + final_out[1:-2] + "."
                return final_out
    if answer in ["yes", "no"]:
        if answer == "yes":
            this_answer = 1
        else:
            this_answer = 0
        first_vb = str_tokens_question[0].lower()
        new_question = list_to_str(str_tokens_question[1:])
        doc_new_question = nlp(new_question)
        tokens_new_question = [token for token in doc_new_question if token.text != ""]
        dep_tokens_new_question = [token.dep_ for token in doc_new_question if token.text != ""]
        tag_tokens_new_question = [token.tag_ for token in doc_new_question if token.text != ""]
        pos_tokens_new_question = [token.pos_ for token in doc_new_question if token.text != ""]
        str_tokens_new_question = [token.text for token in doc_new_question if token.text != ""]
        root = str_tokens_new_question[dep_tokens_new_question.index("ROOT")]
        root_plc = dep_tokens_new_question.index("ROOT")
        if "VB" not in tag_tokens_new_question[root_plc]:
            have_vb = False
            for i in tag_tokens_new_question:
                if "VB" in i:
                    root_plc = tag_tokens_new_question.index(i)
                    root = str_tokens_new_question[root_plc]
                    break
        if str_tokens_question[0].lower() in ["do", "did", "does"]:
            this_tense = 0
            if first_vb == "do":
                this_tense = 1
            elif first_vb == "does":
                this_tense = 2
            elif first_vb == "did":
                this_tense = 3
            this_verb = ""
            if this_tense == 1 or this_tense == 0:
                this_verb = str_tokens_new_question[root_plc]
            if this_tense == 2:
                this_verb = conjugate(tokens_new_question[root_plc].lemma_, tense=PRESENT, number=SG)
            if this_tense == 3:
                this_verb = conjugate(tokens_new_question[root_plc].lemma_, tense=PAST)
            final = []
            final.extend(str_tokens_new_question[:root_plc])
            if this_answer:
                final.extend([this_verb])
                final.extend(str_tokens_new_question[root_plc + 1:])
                final.pop()
                final_out = list_to_str(final)
                final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
            else:
                final.extend([str_tokens_question[0].lower(), "not"])
                final.extend([str_tokens_new_question[root_plc]])
                final.extend(str_tokens_new_question[root_plc + 1:])
                final.pop()
                final_out = list_to_str(final)
                final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        elif str_tokens_question[0].lower() in ["am", "is", "are", "was", "were"]:
            str_tokens_question[0] = str_tokens_question[0].lower()
            if "the same" in question:
                vb = str_tokens_question[0]
                same_plc = str_tokens_question.index("same")
                final = []
                final.extend(str_tokens_question[1:same_plc - 1])
                if this_answer:
                    final.extend([vb])
                else:
                    final.extend([vb, "not"])
                final.extend(str_tokens_question[same_plc - 1:])
                final_out = list_to_str(final)
                final_out = final_out[0].upper() + final_out[1:-1] + "."
                return final_out
            elif "same as " in question:
                vb = str_tokens_question[0]
                same_plc = str_tokens_question.index("same")
                final = []
                final.extend(str_tokens_question[1:same_plc])
                if this_answer:
                    final.extend([vb])
                else:
                    final.extend([vb, "not"])
                final.extend(str_tokens_question[same_plc:])
                final_out = list_to_str(final)
                final_out = final_out[0].upper() + final_out[1:-1] + "."
                return final_out
            doc = nlp(new_question)
            sent = list(doc.sents)[0]
            parse_str = sent._.parse_string
            t = Tree.fromstring(parse_str)
            this_one = []
            shuchu(t, this_one)
            have_that = False
            that = ""
            for i in this_one:
                for j in i:
                    if j in ["that", "which", "who"]:
                        have_that = True
                        that = j
            if have_that:
                parent = []
                for word in tokens_new_question:
                    tree = []
                    child_to_list_node(word, tree)
                    for child in tree:
                        if child.lemma_ in ["that", "which", "who"]:
                            parent.append(word)
                parent_tree = []
                tree_to_list_str(parent[0], parent_tree)
                order_list, order_plc, num = order(parent_tree, this_one)
                if order_list != []:
                    this_one[order_plc] = order_list
                    this_num = -1
                    for i in range(len(this_one[order_plc + 1:])):
                        this_num += 1
                        if num == 1:
                            break
                        this_one[order_plc + 1 + this_num] = []
                        num -= 1
                    num = -1
                    for part in range(len(this_one)):
                        if num == len(this_one) - 1:
                            break
                        num += 1
                        if this_one[num] == []:
                            this_one.remove([])
                            num -= 1
            num = -1
            if_ctn = True
            while if_ctn:
                num += 1
                if this_one[num] == ["-"]:
                    this_one[num].extend(this_one[num + 1])
                    this_one[num + 1] = []
                    this_one[num - 1].extend(this_one[num])
                    this_one[num] = []
                    this_one.remove([])
                    this_one.remove([])
                    num -= 1
                if num == len(this_one) - 1:
                    if_ctn = False
            num = -1
            if_ctn = True
            while if_ctn:
                num += 1
                if num == len(this_one) - 1:
                    if_ctn = False
                if this_one[num - 1] == ["'"] and this_one[num + 1] == ["'"]:
                    this_one[num - 1].extend(this_one[num])
                    this_one[num - 1].extend(this_one[num + 1])
                    this_one[num] = []
                    this_one[num + 1] = []
                    this_one[num] = []
                    this_one.remove([])
                    this_one.remove([])
                    num -= 1
                if num == len(this_one) - 2:
                    if_ctn = False
            num = -1
            if_ctn = True
            while if_ctn:
                num += 1
                if this_one[num] == ["a"] or this_one[num] == ["an"]:
                    this_one[num].extend(this_one[num + 1])
                    this_one[num + 1] = []
                    this_one.remove([])
                    num -= 1
                if num == len(this_one) - 1:
                    if_ctn = False
            str_tokens = str_tokens_question[1:]
            pos_tokens = pos_tokens_question[1:]
            all_noun = []
            all_adj = []
            for num in range(len(this_one)):
                if is_noun_from_S2W(this_one[num], pos_tokens_question[1:], str_tokens, str_tokens_answer):
                    all_noun.append(num)
            for num in range(len(this_one)):
                if is_adj(this_one[num], pos_tokens_question[1:], str_tokens, str_tokens_answer):
                    all_adj.append(num)
            comb = []
            num = -1
            for i in all_adj[:]:
                num += 1
                if num != len(all_adj) - 1:
                    if all_adj[num] + 1 == all_adj[num + 1]:
                        if comb == []:
                            comb.append(all_adj[num])
                        for plc in comb:
                            if plc > all_adj[num]:
                                comb.insert(comb.index(plc), all_adj[num])
                                break
                        continue
                if all_adj[num] + 1 in all_noun:
                    if comb == []:
                        comb.append(all_adj[num])
                    else:
                        for plc in comb:
                            if plc > all_adj[num]:
                                comb.insert(comb.index(plc), all_adj[num])
                                break
            all_nn_adj = all_noun
            for i in all_adj:
                if i not in all_nn_adj:
                    all_nn_adj.append(i)
            num = -1
            for i in this_one:
                num += 1
                if this_one[num] == []:
                    continue
                if this_one[num][0] in ["with", "of", "on", "in", "that", "which", "who", "of",
                                        "and"] and num - 1 in all_nn_adj:
                    first_plc = num - 1
                    second_plc = num
                    if first_plc not in comb:
                        if comb != []:
                            for plc in comb:
                                if plc > first_plc:
                                    comb.insert(comb.index(plc), first_plc)
                                    break
                            comb.append(first_plc)
                        else:
                            comb.append(first_plc)
                    if second_plc not in comb:
                        if comb != []:
                            for plc in comb:
                                if plc > second_plc:
                                    comb.insert(comb.index(plc), second_plc)
                                    break
                            comb.append(second_plc)
                        else:
                            comb.append(second_plc)
                if this_one[num][0] in ["my", "your", "their", "her", "his", "our"] and len(this_one[num]) == 1:
                    first_plc = num - 1
                    second_plc = num
                    if first_plc not in comb:
                        if comb != []:
                            for plc in comb:
                                if plc > first_plc:
                                    comb.insert(comb.index(plc), first_plc)
                                    break
                            comb.append(first_plc)
                        else:
                            comb.append(first_plc)
                    if second_plc not in comb:
                        if comb != []:
                            for plc in comb:
                                if plc > second_plc:
                                    comb.insert(comb.index(plc), second_plc)
                                    break
                            comb.append(second_plc)
                        else:
                            comb.append(second_plc)
            new_comb = []
            for i in range(len(comb)):
                new_comb.append(comb[len(comb) - i - 1])
            if new_comb != []:
                for i in new_comb:
                    this_one[i].extend(this_one[i + 1])
                    this_one[i + 1] = []
            final = []
            num = -1
            for i in range(len(this_one)):
                num += 1
                if num == len(this_one) - 1:
                    break
                if this_one[num] == []:
                    this_one.remove([])
                    num -= 1
            if len(this_one) == 1:
                final.extend(this_one[0])
                if this_answer:
                    final.extend([str_tokens_question[0]])
                else:
                    final.extend([str_tokens_question[0], "not"])
                for i in this_one[1:]:
                    final.extend(i)
            if len(this_one) == 2:
                have_in = False
                for i in this_one[0]:
                    if i in ["in", "on", "during", "from", "to"]:
                        have_in = True
                        in_plc = this_one[0].index(i)
                if have_in:
                    this_one.insert(1, [])
                    this_one[1].extend(this_one[0][in_plc:])
                    this_one[0] = this_one[0][:in_plc]
            final.extend(this_one[0])
            if this_answer:
                final.extend([str_tokens_question[0]])
            else:
                final.extend([str_tokens_question[0], "not"])
            for i in this_one[1:]:
                final.extend(i)
            final_out = list_to_str(final)
            final_out = final_out[0].upper() + final_out[1:-1] + "."
            return final_out
        elif str_tokens_question[0].lower() in ["would", "could", "will", "can", "should", "might", "may", "has", "had",
                                                "have"]:
            final = []
            if str_tokens_new_question[root_plc - 1] == "been" and str_tokens_new_question[root_plc - 2] == "ever":
                final.extend(str_tokens_new_question[:root_plc - 2])
                if this_answer:
                    final.extend([str_tokens_question[0]])
                else:
                    final.extend([str_tokens_question[0], "not"])
                final.extend(str_tokens_new_question[root_plc - 2:])
            elif pos_tokens_new_question[root_plc - 1] in ["ADJ", "ADV", "ADJP"] or str_tokens_new_question[
                root_plc - 1] == "been":
                final.extend(str_tokens_new_question[:root_plc - 1])
                if this_answer:
                    final.extend([str_tokens_question[0]])
                else:
                    final.extend([str_tokens_question[0], "not"])
                final.extend(str_tokens_new_question[root_plc - 1:])
            else:
                final.extend(str_tokens_new_question[:root_plc])
                if this_answer:
                    final.extend([str_tokens_question[0]])
                else:
                    final.extend([str_tokens_question[0], "not"])
                final.extend(str_tokens_new_question[root_plc:])
            final.pop()
            final_out = list_to_str(final)
            final_out = final_out[0].upper() + final_out[1:] + "."
            return final_out


def statement_not_boolean(question, answer, nlp):
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
    tag_tokens_question = [token.tag_ for token in doc_question if token.text != ""]
    str_tokens_question = [token.text for token in doc_question if token.text != ""]
    str_tokens_question[0] = str_tokens_question[0].lower()
    lemma_tokens_question = [token.lemma_ for token in doc_question if token.text != ""]
    tokens_answer = [token for token in doc_answer if token.text != ""]
    tag_tokens_answer = [token.tag_ for token in doc_answer if token.text != ""]
    dep_tokens_answer = [token.dep_ for token in doc_answer if token.text != ""]
    pos_tokens_answer = [token.pos_ for token in doc_answer if token.text != ""]
    str_tokens_answer = [token.text for token in doc_answer if token.text != ""]
    if answer == "no" and "ROOT" in dep_tokens_question:
        root_plc = dep_tokens_question.index("ROOT")
        root = str_tokens_question[root_plc]
        if pos_tokens_question[root_plc] == "VERB":
            if pos_tokens_question[root_plc - 1] == "VERB":
                final = []
                final.extend(str_tokens_question[:root_plc])
                final.extend(["not"])
                final.extend(str_tokens_question[root_plc:])
                final.pop()
                final_out = list_to_str(final)
                final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
            else:
                this_tense = tense(root, nlp)
                final = []
                final.extend(str_tokens_question[:root_plc])
                if this_tense == 1:
                    final.extend(["did", "not"])
                elif this_tense == 2:
                    final.extend(["does", "not"])
                elif this_tense == 3:
                    final.extend(["do", "not"])
                final.extend(str_tokens_question[root_plc:])
                final.pop()
                final_out = list_to_str(final)
                final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        else:
            return None
    elif answer == "yes":
        final = []
        final.extend(str_tokens_question)
        final.pop()
        final_out = list_to_str(final)
        final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out


def this_main(npy_file_path, out_file_path, nlp):
    output = np.load(npy_file_path, allow_pickle=True)
    output = output.tolist()
    data_save_in_npy = []
    for a_num in tqdm(range(len(output))):
        i = output[a_num]
        question = i[0]
        doc_question = nlp(question)
        tokens_question = [doc_question[0]]
        if tokens_question[0].lemma_ in boolean_set:
            try:
                statement = boolean(question, i[1], nlp)
            except IndexError as e:
                continue
            if statement is None:
                continue
            data_save_in_npy.append({'statement': str(statement),
                                     'answer': i[1],
                                     'article': i[2],
                                     'question': question,
                                     'GT': i[5],
                                     'index': i[3],
                                     'dataset': i[4]})
            continue
        elif i[1] in ["yes", "no"] and tokens_question[0].lemma_ not in WH_set:
            try:
                statement = boolean(question, i[1], nlp)
            except IndexError as e:
                continue
            if statement is None:
                continue
            data_save_in_npy.append({'statement': str(statement),
                                     'answer': i[1],
                                     'article': i[2],
                                     'question': question,
                                     'GT': i[5],
                                     'index': i[3],
                                     'dataset': i[4]})
            continue
    np.save(out_file_path, data_save_in_npy)


def main():
    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument(
        "--npy_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--out_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('benepar', config={'model': 'benepar_en3'})
    args = parser.parse_args()
    this_main(args.npy_file_path, args.out_file_path, nlp)


if __name__ == "__main__":
    main()
