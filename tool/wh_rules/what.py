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
    while(True):
        num += 1
        if num == len(sent):
            start = 0
            order = []
            ctnu = False
            break
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
                    num = num-len(list) + 1
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
    if this_acl+1 != len(dep_tokens_new_question):
        if dep_tokens_new_question[this_acl+1] == "advmod":
            return False
    if dep_tokens_new_question[this_acl-1] == "aux":
        return False
    for dep in dep_tokens_new_question[this_acl+1:]:
        if dep == "acl" or dep == "ROOT":
            break
        if dep == "xcomp" or dep == "pcomp" or dep == "pobj" or dep == "advcl":
            need_change = False
    return need_change


class what(object):

    def generate(self, question, answer):
        try:
            return self.generate_statement(question, answer)
        except IndexError as e:
            return None

    def generate_statement(self, question, answer):
        if "WHat " in question:
            question = question.replace("WHat ", "What ")
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
        str_tokens_question = [token.text for token in doc_question if token.text != ""]
        tokens_answer = [token for token in doc_answer if token.text != ""]
        tag_tokens_answer = [token.tag_ for token in doc_answer if token.text != ""]
        dep_tokens_answer = [token.dep_ for token in doc_answer if token.text != ""]
        pos_tokens_answer = [token.pos_ for token in doc_answer if token.text != ""]
        str_tokens_answer = [token.text for token in doc_answer if token.text != ""]
        have_comma = False
        all_comma = []
        all_what = []
        num = 0
        for token in tokens_question:
            if token.text == ",":
                all_comma.append(num)
                have_comma = True
            if token.text == "what" or token.text == "What":
                all_what.append(num)
            num += 1
        small_question_start = 0
        have_comma_do = False
        if have_comma:
            for comma in all_comma:
                if all_what[0] > comma:
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
        tag_tokens_new_question = [token.tag_ for token in doc_new_question if token.text != ""]
        pos_tokens_new_question = [token.pos_ for token in doc_new_question if token.text != ""]
        dep_tokens_new_question = [token.dep_ for token in doc_new_question if token.text != ""]
        what = []
        what_plc = []
        num = 0
        for word in tokens_new_question:
            if word.lemma_ == "what":
                what.append(word)
                what_plc.append(num)
            num += 1
        if what_plc == []:
            return
        vbs = []
        vbs_plc = []
        num = 0
        for pos in pos_tokens_new_question:
            if pos in ["VERB", 'AUX'] and tokens_new_question[num].text != conjugate(tokens_new_question[num].lemma_,
                                                                                      tense=PRESENT,
                                                                                      aspect=PROGRESSIVE) and \
                    str_tokens_new_question[num] != "logo":
                vbs.append(str_tokens_new_question[num])
                vbs_plc.append(num)
                num += 1
                continue
            num += 1
        if vbs == []:
            if str_tokens_new_question[0] in ["What", "what"]:
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
                        if child.lemma_ == "what":
                            parent.append(word)
                if parent == []:
                    final = []
                    final.extend(str_tokens_new_question[:what_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[what_plc[0] + 1:])
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
                    if word in ["what", "What"]:
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
        have = ["has", "had", "have"]
        if first_vb in do:
            if str_tokens_new_question[0] in ["What", "what"]:
                output1 = str_tokens_new_question[:first_vb_plc]
                doc_output1 = nlp(list_to_str(output1))
                str_tokens_output1 = [token.text for token in doc_output1 if token.text != ""]
                tag_tokens_output1 = [token.tag_ for token in doc_output1 if token.text != ""]
                vb = str_tokens_new_question[first_vb_plc]
                output2 = str_tokens_new_question[first_vb_plc:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_lemma = tokens_output2[dep_tokens_output2.index("ROOT")].lemma_
                root_plc = dep_tokens_output2.index("ROOT")
                tag = nltk.pos_tag(str_tokens_output2)
                nltk_tag = [this_tag[1] for this_tag in tag]
                be_before_root = False
                if tokens_output2[root_plc - 1].lemma_ == "be":
                    be_before_root = True
                need_change = False
                num = -1
                acl_plc = []
                num = -1
                for dep in dep_tokens_output2:
                    num += 1
                    if dep == "nsubj" and num < root_plc:
                        need_change = True
                if dep_tokens_output2[0] == "ROOT":
                    need_change = True
                if tokens_output2[0].lemma_ == "do":
                    need_change = True
                if need_change:
                    if first_vb in would:
                        if "be able to" in new_question and root_lemma == "be":
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[len(output1) + root_plc:len(output1) + root_plc + 4])
                            final.extend([answer])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 4:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if root_plc == 0:
                            final = []
                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                in_plc = tag_after_what.index("IN")
                                after_what = after_what[in_plc:]
                            else:
                                if "type" in after_what:
                                    type_plc = after_what.index("type")
                                    after_what = after_what[type_plc:]
                                else:
                                    after_what = []
                            for this_word in after_what:
                                if this_word in answer.lower():
                                    after_what = []
                            final.extend([answer])
                            final.extend(after_what)
                            final.extend(str_tokens_new_question[first_vb_plc:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        follow_answer = []
                        if "IN" in tag_tokens_output1:
                            follow_answer = str_tokens_output1[tag_tokens_output1.index("IN"):]
                        final = []
                        aux_vb = str_tokens_new_question[first_vb_plc]
                        if be_before_root:
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc - 1])
                            final.extend([aux_vb])
                            final.extend([str_tokens_new_question[len(output1) + root_plc - 1]])
                        else:
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                            final.extend([aux_vb])
                        if str_tokens_new_question[len(output1) + root_plc] != "do":
                            final.extend([str_tokens_new_question[len(output1) + root_plc]])
                        if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century",
                                                                                                         "year"]:
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            if tokens_new_question[1].lemma_ in ["year"]:
                                final.extend(["in", answer])
                            elif "century" not in answer:
                                final.extend(["in", answer, str_tokens_new_question[1]])
                            else:
                                final.extend(["in", answer])
                        else:
                            if dep_tokens_answer[0] == "aux":
                                final.extend(str_tokens_answer[1:])
                                final.extend(follow_answer)
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                                final.pop()
                            else:
                                final.extend([answer])
                                final.extend(follow_answer)
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                                final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    elif first_vb in did:
                        if tag_tokens_new_question[-2] == "IN":
                            this_tense = 0
                            if first_vb == "do":
                                this_tense = 1
                            elif first_vb == "does":
                                this_tense = 2
                            elif first_vb == "did":
                                this_tense = 3
                            final = []
                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                in_plc = tag_after_what.index("IN")
                                after_what = after_what[in_plc:]
                            else:
                                if "type" in after_what:
                                    type_plc = after_what.index("type")
                                    after_what = after_what[type_plc:]
                                else:
                                    after_what = []
                            for this_word in after_what:
                                if this_word in answer.lower():
                                    after_what = []
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
                            if tag_tokens_answer[0] in ["IN"]:
                                final.extend(list_to_str(str_tokens_answer[1:]))
                            else:
                                final.extend([answer])
                            final.extend(after_what)
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if str_tokens_new_question[first_vb_plc + 1] == "not":
                            final = []
                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                in_plc = tag_after_what.index("IN")
                                after_what = after_what[in_plc:]
                            if "TO" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                in_plc = tag_after_what.index("TO")
                                after_what = after_what[in_plc:]
                            else:
                                if "type" in after_what:
                                    type_plc = after_what.index("type")
                                    after_what = after_what[type_plc:]
                                else:
                                    after_what = []
                            for this_word in after_what:
                                if this_word in answer.lower():
                                    after_what = []
                            final.extend(str_tokens_new_question[:what_plc[0]])
                            final.extend([answer])
                            final.extend(after_what)
                            final.extend(str_tokens_new_question[first_vb_plc:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        this_tense = 0
                        if first_vb == "do":
                            this_tense = 1
                        elif first_vb == "does":
                            this_tense = 2
                        elif first_vb == "did":
                            this_tense = 3
                        final = []
                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                            else:
                                after_what = []
                        for this_word in after_what:
                            if this_word in answer.lower():
                                after_what = []
                        if root_plc == 0:
                            output1 = str_tokens_new_question[:first_vb_plc]
                            doc_output1 = nlp(list_to_str(output1))
                            str_tokens_output1 = [token.text for token in doc_output1 if
                                                  token.text != ""]
                            tag_tokens_output1 = [token.tag_ for token in doc_output1 if token.text != ""]
                            vb = str_tokens_new_question[first_vb_plc]
                            output2 = str_tokens_new_question[first_vb_plc + 1:]
                            doc_output2 = nlp(list_to_str(output2))
                            tokens_output2 = [token for token in doc_output2 if token.text != ""]
                            str_tokens_output2 = [token.text for token in doc_output2 if
                                                  token.text != ""]
                            dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                            pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                            root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                            root_plc = dep_tokens_output2.index("ROOT")
                            tag = nltk.pos_tag(str_tokens_output2)
                            nltk_tag = [this_tag[1] for this_tag in tag]
                            this_tense = 0
                            if first_vb == "do":
                                this_tense = 1
                            elif first_vb == "does":
                                this_tense = 2
                            elif first_vb == "did":
                                this_tense = 3
                            final = []
                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                in_plc = tag_after_what.index("IN")
                                after_what = after_what[in_plc:]
                            else:
                                if "type" in after_what:
                                    type_plc = after_what.index("type")
                                    after_what = after_what[type_plc:]
                                else:
                                    after_what = []
                            for this_word in after_what:
                                if this_word in answer.lower():
                                    after_what = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc + 1])
                            this_verb = ""
                            if this_tense == 1 or this_tense == 0:
                                this_verb = str_tokens_new_question[len(output1) + 1 + root_plc]
                            if this_tense == 2:
                                this_verb = conjugate(tokens_new_question[len(output1) + 1 + root_plc].lemma_,
                                                      tense=PRESENT,
                                                      number=SG)
                            if this_tense == 3:
                                this_verb = conjugate(tokens_new_question[len(output1) + 1 + root_plc].lemma_,
                                                      tense=PAST)
                            final.extend([this_verb])
                            if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century",
                                                                                                             "year"]:
                                final.extend(str_tokens_new_question[len(output1) + 1 + root_plc + 1:])
                                final.pop()
                                if tokens_new_question[1].lemma_ in ["year"]:
                                    final.extend(["in", answer])
                                if "century" not in answer:
                                    final.extend(["in", answer, str_tokens_new_question[1]])
                                else:
                                    final.extend(["in", answer])
                            else:
                                final.extend([answer])
                                final.extend(after_what)
                                final.extend(str_tokens_new_question[len(output1) + 1 + root_plc + 1:])
                                final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if pos_tokens_output2[root_plc] in ["NOUN", "PROPN", "PRON"] and "VERB" in pos_tokens_output2[
                                                                                                   1:]:
                            root_plc = pos_tokens_output2[1:].index("VERB") + 1
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
                        if str_tokens_new_question[-2] in ["be"]:
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            final.extend([answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if str_tokens_new_question[-2] in ["do"]:
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            final.pop()
                            final.extend([answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if root_plc + 1 < len(str_tokens_output2) and root_plc + 2 < len(pos_tokens_output2) and \
                                str_tokens_output2[root_plc + 1] == "to" and pos_tokens_output2[root_plc + 2] == "VERB":
                            final.extend(
                                str_tokens_new_question[len(output1) + root_plc + 1:len(output1) + root_plc + 3])
                            final.extend([answer])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 3:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if root_plc + 1 < len(str_tokens_output2) and str_tokens_output2[root_plc + 1] == "to" and len(
                                output1) + root_plc + 3 == len(str_tokens_new_question):
                            final.extend(
                                str_tokens_new_question[len(output1) + root_plc + 1:len(output1) + root_plc + 2])
                            final.extend([answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if str_tokens_new_question[what_plc[0] + 1] == "kind":
                            final.extend([answer])
                            after_what = str_tokens_new_question[what_plc[0] + 3:first_vb_plc]
                            final.extend(after_what)
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century",
                                                                                                         "year"]:
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            if tokens_new_question[1].lemma_ in ["year"]:
                                final.extend(["in", answer])
                            elif "century" not in answer:
                                final.extend(["in", answer, str_tokens_new_question[1]])
                            else:
                                final.extend(["in", answer])
                        else:
                            if str_tokens_new_question[len(output1) + root_plc + 1:len(output1) + root_plc + 4] == ["a",
                                                                                                                    "roll",
                                                                                                                    "in"]:
                                final.extend(
                                    str_tokens_new_question[len(output1) + root_plc + 1:len(output1) + root_plc + 4])
                                final.extend([answer])
                                final.extend(after_what)
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 4:])
                                final.pop()
                            else:
                                if root_lemma in ["call"]:
                                    final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                                    final.pop()
                                    final.extend(["as", answer])
                                else:
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                                    final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                else:
                    need_change = True
                    if pos_tokens_output2[1] in ["VERB"]:
                        need_change = False
                    elif pos_tokens_output2[1] in ["ADJ", "ADV", "ADJP", "VERB"] and pos_tokens_output2[2] in ["VERB"]:
                        need_change = False
                    elif pos_tokens_output2[1] in ["ADJ", "ADV", "ADJP", "VERB"] and pos_tokens_output2[2] in ["ADJ",
                                                                                                               "ADV",
                                                                                                               "ADJP",
                                                                                                               "VERB"] and \
                            pos_tokens_output2[3] in ["VERB"]:
                        need_change = False
                    if need_change:
                        if "end" in str_tokens_output2:
                            pos_tokens_output2[str_tokens_output2.index("end")] = "VERB"
                        if pos_tokens_output2[root_plc] != "VERB":
                            if "VERB" in pos_tokens_output2[1:]:
                                root_plc = pos_tokens_output2[1:].index("VERB") + 1
                                if tag_tokens_output2[root_plc + 1] == "IN":
                                    final = []
                                    final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                                    final.extend([str_tokens_new_question[first_vb_plc]])
                                    final.extend(
                                        str_tokens_new_question[len(output1) + root_plc:len(output1) + root_plc + 2])
                                    final.pop()
                                    final.extend([answer])
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                                final = []
                                final.extend(str_tokens_new_question[:what_plc[0]])
                                final.extend([answer])
                                final.extend(str_tokens_new_question[what_plc[0] + 1:])
                                final.pop()
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc - 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if tag_tokens_output2[root_plc + 1] == "IN":
                                final.extend(
                                    str_tokens_new_question[len(output1) + root_plc - 1:len(output1) + root_plc + 2])
                                final.extend([answer])
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                                final.pop()
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            else:
                                final.extend(
                                    str_tokens_new_question[len(output1) + root_plc - 1:len(output1) + root_plc + 1])
                                final.extend([answer])
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                                final.pop()
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                        if tokens_output2[root_plc - 1].lemma_ == "be":
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc - 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            if tag_tokens_output2[root_plc + 1] == "IN":
                                final.extend(
                                    str_tokens_new_question[len(output1) + root_plc - 1:len(output1) + root_plc + 2])
                                final.extend([answer])
                                final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                                final.pop()
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            final.extend(
                                str_tokens_new_question[len(output1) + root_plc - 1:len(output1) + root_plc + 1])
                            final.extend([answer])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                    final = []
                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                        in_plc = tag_after_what.index("IN")
                        after_what = after_what[in_plc:]
                    else:
                        if "type" in after_what:
                            type_plc = after_what.index("type")
                            after_what = after_what[type_plc:]
                        else:
                            after_what = []
                    for this_word in after_what:
                        if this_word in answer.lower():
                            after_what = []
                    final.extend([answer])
                    final.extend(after_what)
                    final.extend(str_tokens_new_question[first_vb_plc:])
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
                        if child.lemma_ == "what":
                            parent.append(word)
                if parent == []:
                    final = []
                    final.extend(str_tokens_new_question[:what_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[what_plc[0] + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                if str_tokens_new_question[what_plc[0] + 1] in do:
                    what_tree = [str_tokens_new_question[what_plc[0]]]
                    what_tree_plc = what_plc[0]
                else:
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
                        if word in ["what", "What"]:
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
                IN = []
                IN.extend(str_tokens_new_question[:what_tree_plc])
                WHAT = []
                WHAT.extend(str_tokens_new_question[what_tree_plc:what_tree_plc + len(what_tree)])
                if WHAT == []:
                    final = []
                    final.extend(str_tokens_new_question[:what_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[what_plc[0] + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                output1 = str_tokens_new_question[:first_vb_plc + 1]
                vb = str_tokens_new_question[first_vb_plc]
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
                if (len(IN) + len(WHAT) + 1) == len(str_tokens_new_question) or vbs_plc[0] < what_plc[0]:
                    if first_vb in would:
                        final = []
                        after_what = str_tokens_new_question[what_plc[0] + 1:what_plc[0] + len(what_tree)]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:what_plc[0] + len(what_tree)]
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                            else:
                                after_what = []
                        for this_word in after_what:
                            if this_word in answer.lower():
                                after_what = []
                        final.extend(str_tokens_new_question[:what_tree_plc])
                        final.extend([answer])
                        final.extend(after_what)
                        if len(what_tree) == 0:
                            final.extend(str_tokens_new_question[what_tree_plc + 1:])
                        else:
                            final.extend(str_tokens_new_question[what_tree_plc + len(what_tree):])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    elif first_vb in did:
                        final = []
                        after_what = str_tokens_new_question[what_plc[0] + 1:what_plc[0] + len(what_tree)]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:what_plc[0] + len(what_tree)]
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                            else:
                                after_what = []
                        for this_word in after_what:
                            if this_word in answer.lower():
                                after_what = []
                        final.extend(str_tokens_new_question[:what_tree_plc])
                        final.extend([answer])
                        final.extend(after_what)
                        if len(what_tree) == 0:
                            final.extend(str_tokens_new_question[what_tree_plc + 1:])
                        else:
                            final.extend(str_tokens_new_question[what_tree_plc + len(what_tree):])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                else:
                    if first_vb in would:
                        change = True
                        if pos_tokens_new_question[first_vb_plc + 1] in ["ADJ", "ADV", "ADJP"] and \
                                pos_tokens_new_question[
                                    first_vb_plc + 2] in ["ADJ", "ADV", "ADJP"] and pos_tokens_new_question[
                            first_vb_plc + 3] == "VERB":
                            change = False
                        if pos_tokens_new_question[first_vb_plc + 1] in ["ADJ", "ADV", "ADJP"] and \
                                pos_tokens_new_question[
                                    first_vb_plc + 2] == "VERB":
                            change = False
                        if pos_tokens_new_question[first_vb_plc + 1] == "VERB":
                            change = False
                        if not change:
                            final = []
                            final.extend(str_tokens_new_question[:what_plc[0]])
                            final.extend([answer])
                            final.extend(str_tokens_new_question[what_plc[0] + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        final = []
                        aux_vb = str_tokens_new_question[first_vb_plc]
                        final.extend(str_tokens_new_question[first_vb_plc + 1:len(output1) + root_plc])
                        final.extend([aux_vb])
                        final.extend(str_tokens_new_question[len(output1) + root_plc:])
                        final.pop()
                        IN[0] = IN[0][0].lower() + IN[0][1:]
                        final.extend(IN)
                        final.extend([answer])
                        if list_to_str(WHAT[1:]) not in list_to_str(str_tokens_answer).lower():
                            final.extend(WHAT[1:])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    elif first_vb in did:
                        this_tense = 0
                        if first_vb == "do":
                            this_tense = 1
                        elif first_vb == "does":
                            this_tense = 2
                        elif first_vb == "did":
                            this_tense = 3
                        final = []
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
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        if IN != []:
                            IN[0] = IN[0][0].lower() + IN[0][1:]
                        final.extend(IN)
                        final.extend([answer])
                        if list_to_str(WHAT[1:]) not in list_to_str(str_tokens_answer).lower():
                            final.extend(WHAT[1:])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
        if first_vb in be:
            if str_tokens_new_question[0] in ["What", "what"]:
                output1 = str_tokens_new_question[:first_vb_plc]
                vb = str_tokens_new_question[first_vb_plc]
                output2 = str_tokens_new_question[first_vb_plc:]
                doc_output2 = nlp(list_to_str(output2))
                tokens_output2 = [token for token in doc_output2 if token.text != ""]
                str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                root_plc = dep_tokens_output2.index("ROOT")
                if root in be:
                    vbs_plc = []
                    num = 0
                    for pos in pos_tokens_output2:
                        if pos == "VERB":
                            vbs_plc.append(num)
                            num += 1
                            continue
                        num += 1
                    acl_plc = []
                    if len(vbs_plc) != 1:
                        for this_vb_plc in vbs_plc[1:]:
                            if dep_tokens_output2[this_vb_plc] == "acl":
                                acl_plc.append(this_vb_plc)
                    need_change_acl_plc = []
                    if tokens_new_question[root_plc].orth_ == conjugate(tokens_new_question[root_plc].lemma_,
                                                                        tense=PAST, aspect=PROGRESSIVE):
                        acl_plc.append(root_plc)
                    if len(acl_plc):
                        for this_acl in acl_plc:
                            if acl(this_acl, dep_tokens_output2):
                                need_change_acl_plc.append(this_acl)
                        if len(need_change_acl_plc):
                            if len(need_change_acl_plc) == 2:
                                final = []
                                after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                    in_plc = tag_after_what.index("IN")
                                    after_what = after_what[in_plc:]
                                else:
                                    if "type" in after_what:
                                        type_plc = after_what.index("type")
                                        after_what = after_what[type_plc:]
                                    else:
                                        after_what = []
                                for this_word in after_what:
                                    if this_word in answer.lower():
                                        after_what = []
                                final.extend(
                                    str_tokens_new_question[len(output1) + 1:len(output1) + need_change_acl_plc[1]])
                                final.extend([str_tokens_new_question[len(output1)]])
                                final.extend(str_tokens_new_question[len(output1) + need_change_acl_plc[1]:])
                                final.pop()
                                if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in [
                                    "century", "year"]:
                                    if tokens_new_question[1].lemma_ in ["year"]:
                                        final.extend(["in", answer])
                                    elif "century" not in answer:
                                        final.extend(["in", answer, str_tokens_new_question[1]])
                                    else:
                                        final.extend(["in", answer])
                                else:
                                    final.extend([answer])
                                    final.extend(after_what)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            else:
                                final = []
                                after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                    in_plc = tag_after_what.index("IN")
                                    after_what = after_what[in_plc:]
                                else:
                                    if "type" in after_what:
                                        type_plc = after_what.index("type")
                                        after_what = after_what[type_plc:]
                                    else:
                                        after_what = []
                                for this_word in after_what:
                                    if this_word in answer.lower():
                                        after_what = []
                                final.extend(
                                    str_tokens_new_question[len(output1) + 1:len(output1) + need_change_acl_plc[0]])
                                final.extend([str_tokens_new_question[len(output1)]])
                                final.extend(str_tokens_new_question[len(output1) + need_change_acl_plc[0]:])
                                final.pop()
                                if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in [
                                    "century", "year"]:
                                    if tokens_new_question[1].lemma_ in ["year"]:
                                        final.extend(["in", answer])
                                    elif "century" not in answer:
                                        final.extend(["in", answer, str_tokens_new_question[1]])
                                    else:
                                        final.extend(["in", answer])
                                else:
                                    final.extend([answer])
                                    final.extend(after_what)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                        else:
                            final = []
                            if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century",
                                                                                                             "year"]:
                                final.extend(str_tokens_new_question[len(output1) + 1:])
                                final.pop()
                                final.extend([str_tokens_new_question[len(output1)]])
                                if tokens_new_question[1].lemma_ in ["year"]:
                                    final.extend(["in", answer])
                                elif "century" not in answer:
                                    final.extend(["in", answer, str_tokens_new_question[1]])
                                else:
                                    final.extend(["in", answer])
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                            else:
                                after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                    in_plc = tag_after_what.index("IN")
                                    after_what = after_what[in_plc:]
                                else:
                                    if "type" in after_what:
                                        type_plc = after_what.index("type")
                                        after_what = after_what[type_plc:]
                                    else:
                                        after_what = []
                                for this_word in after_what:
                                    if this_word in answer.lower():
                                        after_what = []
                                final.extend([answer])
                                final.extend(after_what)
                                final.extend(str_tokens_output2[root_plc:])
                                final.pop()
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                    else:
                        final = []
                        if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century",
                                                                                                         "year"]:
                            final.extend(str_tokens_new_question[len(output1) + 1:])
                            final.pop()
                            final.extend([str_tokens_new_question[len(output1)]])
                            if tokens_new_question[1].lemma_ in ["year"]:
                                final.extend(["in", answer])
                            elif "century" not in answer:
                                final.extend(["in", answer, str_tokens_new_question[1]])
                            else:
                                final.extend(["in", answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                        else:
                            tag = nltk.pos_tag(str_tokens_output2)
                            nltk_tag = [this_tag[1] for this_tag in tag]
                            if "VERB" in pos_tokens_new_question and pos_tokens_output2[1] != "VERB" and "VB" not in \
                                    nltk_tag[1]:
                                num = -1
                                for pos in pos_tokens_new_question[:-1]:
                                    num += 1
                                    if pos in ["ADJ", "ADV", "ADJP"] and pos_tokens_new_question[num + 1] in ["ADJ",
                                                                                                              "ADV",
                                                                                                              "ADJP"] and \
                                            str_tokens_new_question[num + 2] == "to":
                                        final = []
                                        final.extend(str_tokens_new_question[first_vb_plc + 1:num])
                                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                            in_plc = tag_after_what.index("IN")
                                            after_what = after_what[in_plc:]
                                        else:
                                            if "type" in after_what:
                                                type_plc = after_what.index("type")
                                                after_what = after_what[type_plc:]
                                            else:
                                                after_what = []
                                        for this_word in after_what:
                                            if this_word in answer.lower():
                                                after_what = []
                                        final.extend([str_tokens_new_question[first_vb_plc]])
                                        final.extend(str_tokens_new_question[num:])
                                        final.pop()
                                        final.extend([answer])
                                        final.extend(after_what)
                                        final_out = list_to_str(final)
                                        if have_comma_do:
                                            final_out = final_add + ", " + final_out + "."
                                        else:
                                            final_out = final_out[0].upper() + final_out[1:] + "."
                                        return final_out
                                    if pos in ["ADJ", "ADV", "ADJP"] and str_tokens_new_question[num + 1] == "to":
                                        if pos_tokens_new_question[first_vb_plc + 1] in ["ADJ", "ADV", "ADJP"]:
                                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                            final = []
                                            final.extend(str_tokens_new_question[:what_plc[0]])
                                            final.extend(after_what)
                                            final.extend(str_tokens_new_question[first_vb_plc:])
                                            final.pop()
                                            final_out = list_to_str(final)
                                            if have_comma_do:
                                                final_out = final_add + ", " + final_out + "."
                                            else:
                                                final_out = final_out[0].upper() + final_out[1:] + "."
                                            return final_out
                                        if str_tokens_new_question[first_vb_plc + 1] in ["there"]:
                                            final = []
                                            final.extend([str_tokens_new_question[first_vb_plc + 1]])
                                            final.extend([first_vb])
                                            final.extend([answer])
                                            final.extend(str_tokens_new_question[first_vb_plc + 2:])
                                            final.pop()
                                            final_out = list_to_str(final)
                                            if have_comma_do:
                                                final_out = final_add + ", " + final_out + "."
                                            else:
                                                final_out = final_out[0].upper() + final_out[1:] + "."
                                            return final_out
                                        output3 = str_tokens_new_question[first_vb_plc + 1:]
                                        doc_output3 = nlp(list_to_str(output3))
                                        tokens_output3 = [token for token in doc_output3 if token.text != ""]
                                        str_tokens_output3 = [token.text for token in doc_output3 if
                                                              token.text != ""]
                                        dep_tokens_output3 = [token.dep_ for token in doc_output3 if
                                                              token.text != ""]
                                        pos_tokens_output3 = [token.pos_ for token in doc_output3 if
                                                              token.text != ""]
                                        root3 = str_tokens_output3[dep_tokens_output3.index("ROOT")]
                                        root_plc3 = dep_tokens_output3.index("ROOT")
                                        if root_plc3 <= 1:
                                            final = []
                                            before_what = str_tokens_new_question[:what_plc[0]]
                                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                            final.extend(before_what)
                                            final.extend([answer])
                                            final.extend(after_what)
                                            final.extend(str_tokens_new_question[first_vb_plc:])
                                            final.pop()
                                            final_out = list_to_str(final)
                                            if have_comma_do:
                                                final_out = final_add + ", " + final_out + "."
                                            else:
                                                final_out = final_out[0].upper() + final_out[1:] + "."
                                            return final_out
                                        final = []
                                        final.extend(str_tokens_new_question[first_vb_plc + 1:num])
                                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                            in_plc = tag_after_what.index("IN")
                                            after_what = after_what[in_plc:]
                                        else:
                                            if "type" in after_what:
                                                type_plc = after_what.index("type")
                                                after_what = after_what[type_plc:]
                                            else:
                                                after_what = []
                                        for this_word in after_what:
                                            if this_word in answer.lower():
                                                after_what = []
                                        final.extend([str_tokens_new_question[first_vb_plc]])
                                        final.extend(str_tokens_new_question[num:])
                                        final.pop()
                                        final.extend([answer])
                                        final.extend(after_what)
                                        final_out = list_to_str(final)
                                        if have_comma_do:
                                            final_out = final_add + ", " + final_out + "."
                                        else:
                                            final_out = final_out[0].upper() + final_out[1:] + "."
                                        return final_out
                                if tag_tokens_new_question[-2] == "IN" and pos_tokens_new_question[-3] in ["ADJ", "ADV",
                                                                                                           "ADJP"]:
                                    final = []
                                    this_num = -3
                                    if pos_tokens_new_question[-4] in ["ADJ", "ADV", "ADJP"]:
                                        this_num = -4
                                    final.extend(str_tokens_new_question[first_vb_plc + 1:this_num])
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    final.extend([str_tokens_new_question[first_vb_plc]])
                                    final.extend(str_tokens_new_question[this_num:])
                                    final.pop()
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                                else:
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        elif "kind" in after_what:
                                            type_plc = after_what.index("kind")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    if "there" in str_tokens_new_question:
                                        there_plc = str_tokens_new_question.index("there")
                                        final.extend([str_tokens_new_question[there_plc]])
                                        final.extend([str_tokens_new_question[first_vb_plc]])
                                        final.extend([answer])
                                        final.extend(after_what)
                                        final.extend(str_tokens_new_question[there_plc + 1:])
                                        final.pop()
                                        final_out = list_to_str(final)
                                        if have_comma_do:
                                            final_out = final_add + ", " + final_out + "."
                                        else:
                                            final_out = final_out[0].upper() + final_out[1:] + "."
                                        return final_out
                                    final.extend(str_tokens_new_question[first_vb_plc + 1:])
                                    final.pop()
                                    final.extend([first_vb])
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                            if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                in_plc = tag_after_what.index("IN")
                                after_what = after_what[in_plc:]
                            else:
                                if "type" in after_what:
                                    type_plc = after_what.index("type")
                                    after_what = after_what[type_plc:]
                                else:
                                    after_what = []
                            for this_word in after_what:
                                if this_word in answer.lower():
                                    after_what = []
                            final.extend([answer])
                            final.extend(after_what)
                            final.extend(str_tokens_output2[root_plc:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                else:
                    output1 = str_tokens_new_question[:first_vb_plc]
                    vb = str_tokens_new_question[first_vb_plc]
                    output2 = str_tokens_new_question[first_vb_plc + 1:]
                    doc_output2 = nlp(list_to_str(output2))
                    tokens_output2 = [token for token in doc_output2 if token.text != ""]
                    str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                    dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                    pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                    tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                    root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                    root_plc = dep_tokens_output2.index("ROOT")
                    have_noun = False
                    if "NOUN" in pos_tokens_output2[:root_plc]:
                        have_noun = True
                    if "PROPN" in pos_tokens_output2[:root_plc]:
                        have_noun = True
                    if root in ["called"]:
                        final = []
                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                            else:
                                after_what = []
                        for this_word in after_what:
                            if this_word in answer.lower():
                                after_what = []
                        if pos_tokens_output2[root_plc - 2] in ["ADJ", "ADV", "ADJP"] and pos_tokens_output2[
                            root_plc - 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend(
                                str_tokens_new_question[len(output1) + 1:len(output1) + root_plc - 1])
                            final.extend([str_tokens_new_question[len(output1)]])
                            final.extend(
                                str_tokens_new_question[len(output1) + root_plc - 1:len(output1) + root_plc + 2])
                            final.extend(["as", answer])
                            final.extend(after_what)
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        elif pos_tokens_output2[root_plc - 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend(
                                str_tokens_new_question[len(output1) + 1:len(output1) + root_plc])
                            final.extend([str_tokens_new_question[len(output1)]])
                            final.extend(str_tokens_new_question[len(output1) + root_plc:len(output1) + root_plc + 2])
                            final.extend(["as", answer])
                            final.extend(after_what)
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        else:
                            final.extend(
                                str_tokens_new_question[len(output1) + 1:len(output1) + root_plc + 1])
                            final.extend([str_tokens_new_question[len(output1)]])
                            final.extend(
                                str_tokens_new_question[len(output1) + root_plc + 1:len(output1) + root_plc + 2])
                            final.extend(["as", answer])
                            final.extend(after_what)
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    if "VB" in tag_tokens_output2[root_plc] and root_plc != 0 and have_noun:
                        final = []
                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                            else:
                                after_what = []
                        for this_word in after_what:
                            if this_word in answer.lower():
                                after_what = []
                        if pos_tokens_output2[root_plc - 2] in ["ADJ", "ADV", "ADJP"] and pos_tokens_output2[
                            root_plc - 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend(
                                str_tokens_new_question[len(output1) + 1:len(output1) + root_plc - 1])
                            final.extend([str_tokens_new_question[len(output1)]])
                            final.extend(str_tokens_new_question[len(output1) + root_plc - 1:])
                        elif pos_tokens_output2[root_plc - 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend(
                                str_tokens_new_question[len(output1) + 1:len(output1) + root_plc])
                            final.extend([str_tokens_new_question[len(output1)]])
                            final.extend(str_tokens_new_question[len(output1) + root_plc:])
                        else:
                            final.extend(
                                str_tokens_new_question[len(output1) + 1:len(output1) + root_plc + 1])
                            final.extend([str_tokens_new_question[len(output1)]])
                            final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century",
                                                                                                         "year"]:
                            if tokens_new_question[1].lemma_ in ["year"]:
                                final.extend(["in", answer])
                            elif "century" not in answer:
                                final.extend(["in", answer, str_tokens_new_question[1]])
                            else:
                                final.extend(["in", answer])
                        else:
                            final.extend([answer])
                            final.extend(after_what)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    final = []
                    if tokens_new_question[0].lemma_ == "what" and tokens_new_question[1].lemma_ in ["century", "year"]:
                        final.extend(str_tokens_new_question[len(output1) + 1:])
                        final.pop()
                        final.extend([str_tokens_new_question[len(output1)]])
                        if tokens_new_question[1].lemma_ in ["year"]:
                            final.extend(["in", answer])
                        elif "century" not in answer:
                            final.extend(["in", answer, str_tokens_new_question[1]])
                        else:
                            final.extend(["in", answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                    else:
                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        have_type = False
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                                have_type = True
                            else:
                                after_what = []
                        if "type" in answer or "Type" in answer:
                            if have_type and "IN" in tag_after_what:
                                after_what = []
                        final.extend([answer])
                        final.extend(after_what)
                        final.append(vb)
                        final.extend(str_tokens_output2)
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
                        if child.lemma_ == "what":
                            parent.append(word)
                if parent == []:
                    final = []
                    final.extend(str_tokens_new_question[:what_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[what_plc[0] + 1:])
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
                    if word in ["what", "What"]:
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
                IN = []
                IN.extend(str_tokens_new_question[:what_tree_plc])
                WHAT = []
                if WHAT == []:
                    final = []
                    final.extend(str_tokens_new_question[:what_plc[0]])
                    final.extend([answer])
                    final.extend(str_tokens_new_question[what_plc[0] + 1:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                WHAT.extend(str_tokens_new_question[what_tree_plc:what_tree_plc + len(what_tree)])
                if (len(IN) + len(WHAT) + 1) == len(str_tokens_new_question) or vbs_plc[0] < what_plc[0]:
                    if first_vb_plc > what_plc[0] and what_plc[0] == 1:
                        if "a" in str_tokens_new_question:
                            a_plc = str_tokens_new_question.index("a")
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:a_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[a_plc:])
                            final.pop()
                            before_what = str_tokens_new_question[0]
                            before_what = before_what[0].lower() + before_what[1:]
                            final.extend([before_what])
                            final.extend([answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        if "more" in str_tokens_new_question:
                            more_plc = str_tokens_new_question.index("more")
                            final = []
                            final.extend(str_tokens_new_question[first_vb_plc + 1:more_plc])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[more_plc:])
                            final.pop()
                            before_what = str_tokens_new_question[0]
                            before_what = before_what[0].lower() + before_what[1:]
                            final.extend([before_what])
                            final.extend([answer])
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                    final = []
                    after_what = str_tokens_new_question[what_tree_plc + 1:what_tree_plc + len(what_tree)]
                    tag_after_what = tag_tokens_new_question[what_tree_plc + 1:what_tree_plc + len(what_tree)]
                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                        in_plc = tag_after_what.index("IN")
                        after_what = after_what[in_plc:]
                    else:
                        if "type" in after_what:
                            type_plc = after_what.index("type")
                            after_what = after_what[type_plc:]
                        else:
                            after_what = []
                    for this_word in after_what:
                        if this_word in answer.lower():
                            after_what = []
                    final.extend(str_tokens_new_question[:what_tree_plc])
                    final.extend([answer])
                    final.extend(after_what)
                    final.extend(str_tokens_new_question[what_tree_plc + len(what_tree):])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                else:
                    output1 = str_tokens_new_question[:first_vb_plc]
                    vb = str_tokens_new_question[first_vb_plc]
                    output2 = str_tokens_new_question[first_vb_plc:]
                    doc_output2 = nlp(list_to_str(output2))
                    tokens_output2 = [token for token in doc_output2 if token.text != ""]
                    str_tokens_output2 = [token.text for token in doc_output2 if token.text != ""]
                    dep_tokens_output2 = [token.dep_ for token in doc_output2 if token.text != ""]
                    pos_tokens_output2 = [token.pos_ for token in doc_output2 if token.text != ""]
                    tag_tokens_output2 = [token.tag_ for token in doc_output2 if token.text != ""]
                    root = str_tokens_output2[dep_tokens_output2.index("ROOT")]
                    root_plc = dep_tokens_output2.index("ROOT")
                    if root in be:
                        vbs_plc = []
                        num = 0
                        for pos in pos_tokens_output2:
                            if pos == "VERB":
                                vbs_plc.append(num)
                                num += 1
                                continue
                            num += 1
                        acl_plc = []
                        if len(vbs_plc) != 1:
                            for this_vb_plc in vbs_plc[1:]:
                                if dep_tokens_output2[this_vb_plc] == "acl":
                                    acl_plc.append(this_vb_plc)
                        need_change_acl_plc = []
                        if tokens_new_question[root_plc].orth_ == conjugate(tokens_new_question[root_plc].lemma_,
                                                                            tense=PAST, aspect=PROGRESSIVE):
                            acl_plc.append(root_plc)
                        if len(acl_plc):
                            for this_acl in acl_plc:
                                if acl(this_acl, dep_tokens_output2):
                                    need_change_acl_plc.append(this_acl)
                            if len(need_change_acl_plc):
                                if len(need_change_acl_plc) == 2:
                                    final = []
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    if pos_tokens_new_question[need_change_acl_plc[1] - 1] in ["ADJ", "ADV", "ADJP"]:
                                        final.extend(
                                            str_tokens_new_question[len(output1) + 1:need_change_acl_plc[1] - 1])
                                        final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                        final.extend(str_tokens_new_question[need_change_acl_plc[1] - 1:])
                                    else:
                                        final.extend(str_tokens_new_question[len(output1) + 1:need_change_acl_plc[1]])
                                        final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                        final.extend(str_tokens_new_question[need_change_acl_plc[1]:])
                                    final.pop()
                                    IN[0] = IN[0][0].lower() + IN[0][1:]
                                    final.extend(IN)
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                                else:
                                    final = []
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                                        after_what = [str_tokens_new_question[what_plc[0] + 1]]
                                    if pos_tokens_new_question[len(output1) + need_change_acl_plc[0] - 1] in ["ADJ",
                                                                                                              "ADV",
                                                                                                              "ADJP"]:
                                        final.extend(
                                            str_tokens_new_question[
                                            len(output1) + 1:len(output1) + need_change_acl_plc[0] - 1])
                                        final.extend([str_tokens_new_question[len(output1)]])
                                        final.extend(
                                            str_tokens_new_question[len(output1) + need_change_acl_plc[0] - 1:])
                                    else:
                                        final.extend(
                                            str_tokens_new_question[
                                            len(output1) + 1:len(output1) + need_change_acl_plc[0]])
                                        final.extend([str_tokens_new_question[len(output1)]])
                                        final.extend(str_tokens_new_question[len(output1) + need_change_acl_plc[0]:])
                                    final.pop()
                                    if IN != []:
                                        IN[0] = IN[0][0].lower() + IN[0][1:]
                                    final.extend(IN)
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                            else:
                                tag = nltk.pos_tag(str_tokens_output2)
                                nltk_tag = [this_tag[1] for this_tag in tag]
                                have_root = False
                                num = 0
                                for this_tag in nltk_tag[1:]:
                                    num += 1
                                    if "VB" in this_tag:
                                        root_plc = num
                                        root = str_tokens_output2[num]
                                        have_root = True
                                if have_root:
                                    final = []
                                    before_what = str_tokens_new_question[:what_plc[0]]
                                    before_what[0] = before_what[0][0].lower() + before_what[0][1:]
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    if pos_tokens_new_question[first_vb_plc + root_plc - 1] in ["ADJ", "ADV", "ADJP"]:
                                        final.extend(
                                            str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc - 1])
                                        final.extend([str_tokens_new_question[first_vb_plc]])
                                        final.extend([str_tokens_new_question[first_vb_plc + root_plc - 1]])
                                    else:
                                        final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                                        final.extend([str_tokens_new_question[first_vb_plc]])
                                        final.extend([str_tokens_new_question[first_vb_plc + root_plc]])
                                    final.extend(before_what)
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final.extend(str_tokens_new_question[first_vb_plc + root_plc + 1:])
                                    final.pop()
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                                final = []
                                after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                    in_plc = tag_after_what.index("IN")
                                    after_what = after_what[in_plc:]
                                else:
                                    if "type" in after_what:
                                        type_plc = after_what.index("type")
                                        after_what = after_what[type_plc:]
                                    else:
                                        after_what = []
                                for this_word in after_what:
                                    if this_word in answer.lower():
                                        after_what = []
                                final.extend([answer])
                                final.extend(after_what)
                                final.extend(str_tokens_output2[root_plc:])
                                final.pop()
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                        else:
                            output3 = str_tokens_new_question[first_vb_plc + 1:]
                            doc_output3 = nlp(list_to_str(output3))
                            tokens_output3 = [token for token in doc_output3 if token.text != ""]
                            str_tokens_output3 = [token.text for token in doc_output3 if
                                                  token.text != ""]
                            dep_tokens_output3 = [token.dep_ for token in doc_output3 if token.text != ""]
                            dep_tokens_output3 = [token.dep_ for token in doc_output3 if token.text != ""]
                            pos_tokens_output3 = [token.pos_ for token in doc_output3 if token.text != ""]
                            root = str_tokens_output3[dep_tokens_output3.index("ROOT")]
                            root_plc = dep_tokens_output3.index("ROOT")
                            if pos_tokens_output3[root_plc] in ["ADJ", "ADV", "ADJP"]:
                                final = []
                                after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                    in_plc = tag_after_what.index("IN")
                                    after_what = after_what[in_plc:]
                                else:
                                    if "type" in after_what:
                                        type_plc = after_what.index("type")
                                        after_what = after_what[type_plc:]
                                    else:
                                        after_what = []
                                for this_word in after_what:
                                    if this_word in answer.lower():
                                        after_what = []
                                if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                                    after_what = [str_tokens_new_question[what_plc[0] + 1]]
                                if pos_tokens_new_question[root_plc + first_vb_plc] in ["ADJ", "ADV", "ADJP"]:
                                    final.extend(str_tokens_new_question[len(output1) + 1:root_plc + first_vb_plc])
                                    final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                    final.extend(str_tokens_new_question[root_plc + first_vb_plc:])
                                else:
                                    final.extend(str_tokens_new_question[len(output1) + 1:root_plc + first_vb_plc + 1])
                                    final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                    final.extend(str_tokens_new_question[root_plc + first_vb_plc + 1:])
                                final.pop()
                                if IN != []:
                                    IN[0] = IN[0][0].lower() + IN[0][1:]
                                final.extend(IN)
                                final.extend([answer])
                                final.extend(after_what)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            if pos_tokens_output3[root_plc] in ["NOUN", "PROPN", "PRON"]:
                                if "DET" in pos_tokens_output3[root_plc + 1:]:
                                    final = []
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                                        after_what = [str_tokens_new_question[what_plc[0] + 1]]
                                    if pos_tokens_new_question[root_plc + first_vb_plc + 1] in ["ADJ", "ADV", "ADJP"]:
                                        final.extend(
                                            str_tokens_new_question[len(output1) + 1:root_plc + first_vb_plc + 1])
                                        final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                        final.extend(str_tokens_new_question[root_plc + first_vb_plc + 1:])
                                    else:
                                        final.extend(
                                            str_tokens_new_question[len(output1) + 1:root_plc + first_vb_plc + 2])
                                        final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                        final.extend(str_tokens_new_question[root_plc + first_vb_plc + 2:])
                                    final.pop()
                                    IN[0] = IN[0][0].lower() + IN[0][1:]
                                    final.extend(IN)
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                                else:
                                    final = []
                                    after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                    if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                        in_plc = tag_after_what.index("IN")
                                        after_what = after_what[in_plc:]
                                    else:
                                        if "type" in after_what:
                                            type_plc = after_what.index("type")
                                            after_what = after_what[type_plc:]
                                        else:
                                            after_what = []
                                    for this_word in after_what:
                                        if this_word in answer.lower():
                                            after_what = []
                                    if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                                        after_what = [str_tokens_new_question[what_plc[0] + 1]]
                                    final.extend(str_tokens_new_question[len(output1) + 1:])
                                    final.pop()
                                    final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                    IN[0] = IN[0][0].lower() + IN[0][1:]
                                    final.extend(IN)
                                    final.extend([answer])
                                    final.extend(after_what)
                                    final_out = list_to_str(final)
                                    if have_comma_do:
                                        final_out = final_add + ", " + final_out + "."
                                    else:
                                        final_out = final_out[0].upper() + final_out[1:] + "."
                                    return final_out
                            if pos_tokens_output3[root_plc] in ["VERB"]:
                                final = []
                                after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                                    in_plc = tag_after_what.index("IN")
                                    after_what = after_what[in_plc:]
                                else:
                                    if "type" in after_what:
                                        type_plc = after_what.index("type")
                                        after_what = after_what[type_plc:]
                                    else:
                                        after_what = []
                                for this_word in after_what:
                                    if this_word in answer.lower():
                                        after_what = []
                                if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                                    after_what = [str_tokens_new_question[what_plc[0] + 1]]
                                if pos_tokens_new_question[root_plc + first_vb_plc] in ["ADJ", "ADV", "ADJP"]:
                                    final.extend(str_tokens_new_question[len(output1) + 1:root_plc + first_vb_plc])
                                    final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                    final.extend(str_tokens_new_question[root_plc + first_vb_plc:])
                                else:
                                    final.extend(str_tokens_new_question[len(output1) + 1:root_plc + first_vb_plc + 1])
                                    final.extend(str_tokens_new_question[len(output1):len(output1) + 1])
                                    final.extend(str_tokens_new_question[root_plc + first_vb_plc + 1:])
                                final.pop()
                                IN[0] = IN[0][0].lower() + IN[0][1:]
                                final.extend(IN)
                                final.extend([answer])
                                final.extend(after_what)
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            final = []
                            final.extend(str_tokens_new_question[:what_plc[0]])
                            final.extend([answer])
                            if str_tokens_new_question[what_plc[0] + 1] in answer:
                                final.extend(str_tokens_new_question[what_plc[0] + 2:])
                            else:
                                final.extend(str_tokens_new_question[what_plc[0] + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                    else:
                        if tokens_output2[root_plc - 1].lemma_ == "be":
                            if tag_tokens_new_question[0] == "IN" and str_tokens_new_question[
                                1] == "what" and "VERB" in pos_tokens_output2[2:]:
                                final = []
                                root_plc = pos_tokens_output2[2:].index("VERB") + 2
                                final.extend(str_tokens_new_question[first_vb_plc + 1:first_vb_plc + root_plc])
                                final.extend([str_tokens_new_question[first_vb_plc]])
                                final.extend(str_tokens_new_question[first_vb_plc + root_plc:])
                                final.pop()
                                before = str_tokens_new_question[0]
                                before = before[0].lower() + before[1:]
                                final.extend([before])
                                final.extend([answer])
                                if str_tokens_new_question[2] in ["century"]:
                                    final.extend([str_tokens_new_question[2]])
                                final_out = list_to_str(final)
                                if have_comma_do:
                                    final_out = final_add + ", " + final_out + "."
                                else:
                                    final_out = final_out[0].upper() + final_out[1:] + "."
                                return final_out
                            final = []
                            final.extend(str_tokens_new_question[:what_tree_plc])
                            final.extend([answer])
                            final.extend(str_tokens_new_question[what_tree_plc + len(WHAT):])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "."
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "."
                            return final_out
                        final = []
                        after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
                        if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                            in_plc = tag_after_what.index("IN")
                            after_what = after_what[in_plc:]
                        else:
                            if "type" in after_what:
                                type_plc = after_what.index("type")
                                after_what = after_what[type_plc:]
                            else:
                                after_what = []
                        for this_word in after_what:
                            if this_word in answer.lower():
                                after_what = []
                        if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                            after_what = [str_tokens_new_question[what_plc[0] + 1]]
                        if pos_tokens_new_question[root_plc + len(output1) - 1] in ["ADJ", "ADV", "ADJP"]:
                            final.extend(str_tokens_new_question[first_vb_plc + 1:root_plc + len(output1) - 1])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[root_plc + len(output1) - 1:])
                        else:
                            final.extend(str_tokens_new_question[first_vb_plc + 1:root_plc + len(output1)])
                            final.extend([str_tokens_new_question[first_vb_plc]])
                            final.extend(str_tokens_new_question[root_plc + len(output1):])
                        final.pop()
                        IN[0] = IN[0][0].lower() + IN[0][1:]
                        final.extend(IN)
                        final.extend([answer])
                        final.extend(after_what)
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
        final = []
        if what_plc[0] != len(str_tokens_new_question) - 2:
            if str_tokens_new_question[what_plc[0] + 1] in be or str_tokens_new_question[what_plc[0] + 1] in do:
                final.extend(str_tokens_new_question[:what_plc[0]])
                final.extend([answer])
                final.extend(str_tokens_new_question[what_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        if what_plc[0] < first_vb_plc:
            after_what = str_tokens_new_question[what_plc[0] + 1:first_vb_plc]
            tag_after_what = tag_tokens_new_question[what_plc[0] + 1:first_vb_plc]
            if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                in_plc = tag_after_what.index("IN")
                after_what = after_what[in_plc:]
            if "TO" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                in_plc = tag_after_what.index("TO")
                after_what = after_what[in_plc:]
            else:
                if "type" in after_what:
                    type_plc = after_what.index("type")
                    after_what = after_what[type_plc:]
                else:
                    after_what = []
            for this_word in after_what:
                if this_word in answer.lower():
                    after_what = []
            final.extend(str_tokens_new_question[:what_plc[0]])
            final.extend([answer])
            final.extend(after_what)
            if pos_tokens_new_question[first_vb_plc - 1] == "ADV" and pos_tokens_new_question[
                first_vb_plc - 2] == "ADV":
                final.extend(str_tokens_new_question[first_vb_plc - 2:])
            elif pos_tokens_new_question[first_vb_plc - 1] == "ADV":
                final.extend(str_tokens_new_question[first_vb_plc - 1:])
            else:
                final.extend(str_tokens_new_question[first_vb_plc:])
        elif what_plc[0] + 1 == first_vb_plc:
            final.extend(str_tokens_new_question[:what_plc[0]])
            final.extend([answer])
            final.extend(str_tokens_new_question[what_plc[0] + 1:])
        else:
            parent = []
            for word in tokens_new_question:
                tree = []
                child_to_list_node(word, tree)
                for child in tree:
                    if child.lemma_ == "what":
                        parent.append(word)
            if parent == []:
                final.extend(str_tokens_new_question[:what_plc[0]])
                final.extend([answer])
                final.extend(str_tokens_new_question[what_plc[0] + 1:])
            else:
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
                    if word in ["what", "What"]:
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
                WHAT = []
                WHAT.extend(str_tokens_new_question[what_tree_plc:what_tree_plc + len(what_tree)])
                after_what = str_tokens_new_question[what_tree_plc + 1:what_tree_plc + len(what_tree)]
                if what_tree != []:
                    tag_after_what = tag_tokens_new_question[what_tree_plc: + 1:what_tree_plc + len(what_tree)]
                else:
                    tag_after_what = []
                if "IN" in tag_after_what and "kind" not in after_what and "type" not in after_what:
                    in_plc = tag_after_what.index("IN")
                    after_what = after_what[in_plc:]
                else:
                    if "type" in after_what:
                        type_plc = after_what.index("type")
                        after_what = after_what[type_plc:]
                    else:
                        after_what = []
                for this_word in after_what:
                    if this_word in answer.lower():
                        after_what = []
                if str_tokens_new_question[what_plc[0] + 1] in ["century"]:
                    after_what = [str_tokens_new_question[what_plc[0] + 1]]
                final.extend(str_tokens_new_question[:what_tree_plc])
                final.extend([answer])
                final.extend(after_what)
                final.extend(str_tokens_new_question[what_tree_plc + len(what_tree):])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "."
        else:
            final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out
