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


class who(object):

    def generate(self, question, answer):
        try:
            return self.generate_statement(question, answer)
        except IndexError as e:
            return None

    def generate_statement(self, question, answer):
        if "WHo " in question:
            question = question.replace("WHo ", "who ")
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
        str_tokens_question = [token.text for token in doc_question if token.text != ""]
        have_comma = False
        all_comma = []
        all_who = []
        num = 0
        for token in tokens_question:
            if token.text == ",":
                all_comma.append(num)
                have_comma = True
            if token.text == "Who" or token.text == "who" or token.text == "whom":
                all_who.append(num)
            num += 1
        small_question_start = 0
        have_comma_do = False
        if have_comma:
            for comma in all_comma:
                if all_who[0] > comma:
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
        real_root = str_tokens_new_question[dep_tokens_new_question.index("ROOT")]
        real_root_plc = dep_tokens_new_question.index("ROOT")
        who = []
        who_plc = []
        num = 0
        for word in tokens_new_question:
            if word.lemma_ == "who" or word.lemma_ == "whom":
                who.append(word)
                who_plc.append(num)
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
        num = -1
        all_del = []
        for vb in vbs:
            num += 1
            if vb.lower() == conjugate(tokens_new_question[vbs_plc[num]].lemma_, tense=PRESENT, aspect=PROGRESSIVE):
                all_del.append(num)
        for this_del in range(len(all_del)):
            all_del[this_del] = all_del[this_del] - this_del
        for this_del in all_del:
            vbs.pop(this_del)
            vbs_plc.pop(this_del)
        if vbs == []:
            if "whom" in new_question:
                final = []
                final.extend(str_tokens_new_question[:who_plc[0]])
                final.extend([answer])
                final.extend(str_tokens_new_question[who_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
            if "who " in new_question:
                new_question = new_question.replace("who ", "who is ")
            else:
                new_question = new_question.replace("Who ", "Who is ")
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
                if pos == "VERB" and tokens_new_question[num].text != conjugate(
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
            final.extend(str_tokens_new_question[:who_plc[0]])
            final.extend([answer])
            final.extend(str_tokens_new_question[who_plc[0] + 1:])
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
            if str_tokens_new_question[0] in ["Who", "who", "whom"]:
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
                    final = []
                    final.extend(str_tokens_new_question[first_vb_plc + 1:])
                    final.pop()
                    final.extend([first_vb])
                    final.extend([answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
            else:
                final = []
                final.extend(str_tokens_new_question[:who_plc[0]])
                final.extend([answer])
                final.extend(str_tokens_new_question[who_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        if first_vb in do:
            if str_tokens_new_question[0] in ["Who", "who", "whom"]:
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
                root_token = tokens_output2[root_plc]
                IN = ["with", "to", "for", "from", "at"]
                if len(str_tokens_output2) > 1 and str_tokens_output2[-2] in IN:
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
                    final = []
                    final.extend(str_tokens_new_question[who_plc[0] + 2:len(output1) + root_plc + 1])
                    final.extend([this_verb])
                    final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                    final.pop()
                    final.extend([answer])
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "."
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "."
                    return final_out
                IN_plc = []
                for this_IN in IN:
                    if this_IN in str_tokens_output2:
                        if pos_tokens_output2[str_tokens_output2.index(this_IN)] not in ["ADJ", "ADV", "ADJP", "NOUN",
                                                                                         "PROPN"]:
                            IN_plc.append(str_tokens_output2.index(this_IN))
                            break
                if root_token.lemma_ in ["send", "give", "bring"]:
                    IN_plc = []
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
                    if pos_tokens_new_question[who_plc[0] + 1] in ["ADJ", "ADV", "ADJP"]:
                        final.extend([str_tokens_new_question[who_plc[0] + 1]])
                    final.extend([this_verb])
                    if str_tokens_new_question[-2] in ["of", "on", "in", "to", "with", "for"]:
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:])
                        final.pop()
                        final.extend([answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    if len(IN_plc):
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 2:len(output1) + IN_plc[0] + 2])
                        final.extend([answer])
                        final.extend(str_tokens_new_question[len(output1) + IN_plc[0] + 2:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                    else:
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
                if who[0].text == "whom":
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
                        before_answer = str_tokens_new_question[:who_plc[0]]
                        before_answer[0] = before_answer[0][0].lower() + before_answer[0][1:]
                        final.extend(before_answer)
                        final.extend([answer])
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
                        final.extend(str_tokens_new_question[len(output1) + root_plc + 1:])
                        final.pop()
                        before_answer = str_tokens_new_question[:who_plc[0]]
                        before_answer[0] = before_answer[0][0].lower() + before_answer[0][1:]
                        final.extend(before_answer)
                        final.extend([answer])
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "."
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "."
                        return final_out
                final = []
                final.extend(str_tokens_new_question[:who_plc[0]])
                final.extend([answer])
                final.extend(str_tokens_new_question[who_plc[0] + 1:])
                final.pop()
                final_out = list_to_str(final)
                if have_comma_do:
                    final_out = final_add + ", " + final_out + "."
                else:
                    final_out = final_out[0].upper() + final_out[1:] + "."
                return final_out
        final = []
        final.extend(str_tokens_new_question[:who_plc[0]])
        final.extend([answer])
        final.extend(str_tokens_new_question[who_plc[0] + 1:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "."
        else:
            final_out = final_out[0].upper() + final_out[1:] + "."
        return final_out
