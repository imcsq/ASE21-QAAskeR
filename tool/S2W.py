import spacy
import json
import numpy as np
import random
import nltk
import argparse
from tqdm import tqdm
from nltk import Tree
from benepar.spacy_plugin import BeneparComponent
from nltk.tokenize.treebank import TreebankWordDetokenizer
from transformers import BertTokenizer, BertForTokenClassification

tokenizer = BertTokenizer.from_pretrained('bert-large-cased')

list_list_that = [["that"], ["which"], ["who"], ["where"], ["whose"]]
list_that_set = {"that", "which", "who", "where", "whose"}
abc_set = {"b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w",
           "x", "y", "z"}
noun_set = {"NOUN", "PROPN", "PRON", "ADJ", "ADJP"}
noun_set_ = {"'s", "'", "s", "a", "an", "A", "-", "I", "IV", "VI", "well"}
real_noun_set = {"NOUN", "PROPN", "PRON"}
adj2_set = {"ADJ", "ADJP", "DET", "NOUN", "PROPN", "PRON", "NUM", "CCONJ"}
adj_set_ = {"'s", "'", "s", "a", "an", "A", "-", "I", "IV", "VI", "well", "most"}
IN_set = {"with", "of", "without", "and", "over"}
tag_set = {"CD", "FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS"}
ilegal_words_set = {("the", "range"), ("a", "concern"), ("a", "desire"), ("a", "person"), ("a", "term"),
                    ("an", "event"), ("one", "of", "the"), ("All", "other"), ("efforts"), ("D.C", ".."),
                    ("not", "only"), ("the", "term"), ("the", "world"), ("the", "name"), ("the", "most", "times"),
                    ("the", "last", "time"), ("last", "time"), ("a", "time"), ("some", "people"), ("a", "living"),
                    ("the", "first", "time"), ("the", "public"), ("that", "person"), ("most", "often"),
                    ("dependent", "on"), ("the", "time"), ("one", "individual"), ("more", "so"), ("most", "often"),
                    ("a", "product"), ("the", "most"), ("the", "term"), ("the", "area"), ("the", "last"),
                    ("the", "range"), ("each", "other"), ("the", "efforts"), ("last", "year")}
single_ilegal_word_set = {("not"), ("also"), ("place"), ("key"), ("other"), ("Other"), ("lack"), ("effect"),
                          ("addition"), ("responsible"), ("pace"), ("most"), ("total"), ("one"), ("many"), ("action"),
                          ("many"), ("most"), ("relation"), ("due"), ("people"), ("total"), ("part"), ("city"),
                          ("someone"), ("regard"), ("data"), ("people"), ("life"), ("total"), ("kind"), ("history"),
                          ("work"), ("mom"), ("dad")}
it_set_0 = {"this", "it", "other"}
it_set = {"this", "it", "other", "me", "him", "her", "them", "they", "you", "he", "she", "I"}


def if_have_ileage_word(list1):
    for i in list1:
        if "-" in i and i != "-":
            return True
    return False


def order(child_list, sent_list, this_one):
    order_list = []
    start_plc = 0
    this_one_plc = 0
    for part in sent_list:
        if part in list_that_set:
            start_plc = sent_list.index(part)
    for part in this_one:
        if part in list_list_that:
            this_one_plc = this_one.index(part)
    if start_plc == 0 or this_one_plc == 0:
        return [], 0, 0
    num = 0
    for part in sent_list[start_plc:]:
        if len(order_list) == len(child_list):
            return order_list, this_one_plc, num
        if len(child_list) > len(sent_list) - start_plc:
            return [], 0, 0
        order_list.append(part)
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


def list_to_str(a_list):
    if_start = True
    str_out = ""
    for i in a_list:
        if if_start:
            str_out = str_out + i
            if_start = False
        else:
            str_out = str_out + " " + i
    return str_out


def intersection(part, answer):
    this_part = []
    this_answer = []
    for i in part:
        this_part.append(i.lower())
    for i in answer:
        this_answer.append(i.lower())
    if set(this_part) <= set(this_answer):
        return True
    if set(this_answer) <= set(this_part):
        return True
    return False


def is_noun(list_1, pos_list, str_list, str_tokens_answer):
    if_noun = True
    num = -1
    if list_1 == []:
        return False
    if list_1 == ["the"] or list_1 == ["The"]:
        return True
    if list_1[0] == "the" or list_1[0] == "The":
        return True
    if len(list_1) == 1 and len(list_1[0]) == 1 and list_1[0].lower() in abc_set:
        return True
    for i in list_1:
        num += 1
        if "-" in i and i != "-":
            continue
        plc = str_list.index(i)
        pos = pos_list[plc]
        if num == len(list_1) - 1:
            if i not in [".", ","] and pos == "PUNCT":
                continue
        if pos not in noun_set and i not in noun_set_ and i[-3:] != "ing":
            if_noun = False
    if "-" in list_1:
        if_noun = True
    return if_noun


def is_adj(list_1, pos_list, str_list, str_tokens_answer):
    if_adj = True
    if list_1 == []:
        return False
    if list_1 == ["by"]:
        return False
    if "-" not in list_1[-1] or list_1[-1] == "-":
        plc = str_list.index(list_1[-1])
        pos = pos_list[plc]
        if pos in ["NUM"]:
            return True
    if len(list_1) == 2:
        if ("-" not in list_1[0] or list_1[0] == "-") and ("-" not in list_1[1] or list_1[1] == "-"):
            plc0 = str_list.index(list_1[0])
            pos0 = pos_list[plc0]
            plc1 = str_list.index(list_1[1])
            pos1 = pos_list[plc1]
            if pos0 == "ADV" and pos1 == "VERB":
                return True
    if list_1[0] == "the" or list_1[0] == "The":
        num = 0
        for i in list_1[1:]:
            num += 1
            if '-' in i and i != "-":
                continue
            plc = str_list.index(i)
            pos = pos_list[plc]
            if pos in real_noun_set:
                return False
        return True
    num = -1
    if list_1 == ["much", "more"]:
        return True
    for i in list_1:
        num += 1
        if '-' in i and i != "-":
            continue
        plc = str_list.index(i)
        pos = pos_list[plc]
        if pos not in adj2_set and i not in adj_set_ and i[-3:] != "ing":
            if_adj = False
    return if_adj


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--information_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--answers_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--for_unilm_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('benepar', config={'model': 'benepar_en3'})
    nlp2 = spacy.load('en_core_web_sm')

    source_statements = np.load(args.input_file_path, allow_pickle=True)
    source_statements = source_statements.tolist()

    statements = []
    for i in source_statements:
        statement = i["statement"]
        answer = i["answer"]
        article = i["article"]
        question = i["question"]
        GT = i["GT"]
        index = i["index"]
        this_dataset = i["dataset"]
        statements.append([statement, answer, article, question, GT, index, this_dataset])

    first_num = -1
    print_out_data = []
    print_out_data_jiancha = []
    print_out_data_jilu = []
    pass_num = 0
    for a_num in tqdm(range(len(statements))):
        one = statements[a_num]
        one[0] = one[0][0].lower() + one[0][1:]
        one[0] = one[0].replace("?", "")
        first_num += 1
        doc = nlp(one[0])
        sent = list(doc.sents)[0]
        doc2 = nlp2(one[0])
        tokens_sent = [token for token in doc2 if token.text != ""]
        str_tokens = [token.text for token in doc2 if token.text != ""]
        pos_tokens = [token.pos_ for token in doc2 if token.text != ""]
        doc_answer = nlp(one[1])
        str_tokens_answer = [token.text for token in doc_answer if token.text != ""]
        parse_str = sent._.parse_string
        t = Tree.fromstring(parse_str)
        this_one = []
        shuchu(t, this_one)
        if [] in this_one:
            this_one.remove([])
        have_that = False
        that = ""
        for i in this_one:
            for j in i:
                if j in list_that_set:
                    if '-' not in this_one[this_one.index(i) - 1][-1] or this_one[this_one.index(i) - 1][-1] == "-":
                        if pos_tokens[str_tokens.index(this_one[this_one.index(i) - 1][-1])] in real_noun_set:
                            have_that = True
                            that = j
                            break
        if have_that:
            parent = []
            for word in tokens_sent:
                tree = []
                child_to_list_node(word, tree)
                for child in tree:
                    if child.lemma_ in list_that_set:
                        parent.append(word)
            parent_tree = []
            tree_to_list_str(parent[0], parent_tree)
            order_list, order_plc, num = order(parent_tree, str_tokens, this_one)
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
            if this_one[num] == ["-"] and len(this_one) > num + 1:
                this_one[num].extend(this_one[num + 1])
                this_one[num + 1] = []
                this_one[num - 1].extend(this_one[num])
                this_one[num] = []
                this_one.remove([])
                this_one.remove([])
                num -= 1
            if num == len(this_one) - 1:
                if_ctn = False
        all_noun = []
        all_adj = []
        for num in range(len(this_one)):
            if is_noun(this_one[num], pos_tokens, str_tokens, str_tokens_answer):
                all_noun.append(num)
        for num in range(len(this_one)):
            if is_adj(this_one[num], pos_tokens, str_tokens, str_tokens_answer):
                all_adj.append(num)
        comb = []
        num = -1
        for i in all_noun[:]:
            num += 1
            if num == len(all_noun) - 1:
                break
            if all_noun[num] + 1 == all_noun[num + 1] and "the" not in this_one[all_noun[num + 1]] and \
                    this_one[all_noun[num]][-1] != "time":
                comb.append(all_noun[num])
        num = -1
        for i in all_adj[:]:
            num += 1
            if all_adj[num] not in comb:
                if num != len(all_adj) - 1:
                    if all_adj[num] + 1 == all_adj[num + 1] and "the" not in this_one[all_adj[num + 1]]:
                        if comb == []:
                            comb.append(all_adj[num])
                            continue
                        have_insert = False
                        for plc in comb:
                            if plc > all_adj[num]:
                                have_insert = True
                                comb.insert(comb.index(plc), all_adj[num])
                                break
                        if have_insert:
                            continue
                        else:
                            comb.append(all_adj[num])
                            continue
                if all_adj[num] + 1 in all_noun and "the" not in this_one[all_adj[num] + 1]:
                    if comb == []:
                        comb.append(all_adj[num])
                    else:
                        have_insert = False
                        for plc in comb:
                            if plc > all_adj[num]:
                                have_insert = True
                                comb.insert(comb.index(plc), all_adj[num])
                                break
                        if have_insert:
                            continue
                        else:
                            comb.append(all_adj[num])
                            continue
        all_nn_adj = all_noun
        for i in all_adj:
            if i not in all_nn_adj:
                all_nn_adj.append(i)
        num = -1
        for i in this_one:
            num += 1
            if this_one[num] == []:
                continue
            if num != 0 and this_one[num - 1] != []:
                if '-' in this_one[num - 1][-1] and this_one[num - 1][-1] != "-":
                    continue
            if this_one[num][0] in IN_set and num - 1 in all_nn_adj and pos_tokens[
                str_tokens.index(this_one[num - 1][-1])] in real_noun_set:
                first_plc = num - 1
                second_plc = num
                if first_plc not in comb:
                    if comb != []:
                        have_insert = False
                        for plc in comb:
                            if plc > first_plc:
                                have_insert = True
                                comb.insert(comb.index(plc), first_plc)
                                break
                        if not have_insert:
                            comb.append(first_plc)
                    else:
                        comb.append(first_plc)
                if second_plc not in comb:
                    if comb != []:
                        have_insert = False
                        for plc in comb:
                            if plc > second_plc:
                                have_insert = True
                                comb.insert(comb.index(plc), second_plc)
                                break
                        if not have_insert:
                            comb.append(second_plc)
                    else:
                        comb.append(second_plc)
            if this_one[num][0] in list_that_set and num - 1 in all_nn_adj:
                first_plc = num - 1
                second_plc = num
                if first_plc not in comb:
                    if comb != []:
                        have_insert = False
                        for plc in comb:
                            if plc > first_plc:
                                have_insert = True
                                comb.insert(comb.index(plc), first_plc)
                                break
                        if not have_insert:
                            comb.append(first_plc)
                    else:
                        comb.append(first_plc)
        new_comb = []
        for i in range(len(comb)):
            new_comb.append(comb[len(comb) - i - 1])
        if new_comb != []:
            for i in new_comb:
                if len(this_one) < i + 2:
                    break
                this_one[i].extend(this_one[i + 1])
                this_one[i + 1] = []
        legal = []
        num = -1
        doc_answer = nlp(one[1])
        str_tokens_answer = [token.text for token in doc_answer if token.text != ""]
        doc_statement = nlp(one[0])
        str_tokens_statement = [token.text for token in doc_statement if token.text != ""]
        tag_tokens_statement = [token.tag_ for token in doc_statement if token.text != ""]
        ctn = True
        while (ctn):
            if [] in this_one:
                this_one.remove([])
            else:
                ctn = False
        for this_part in this_one:
            num += 1
            if len(this_part) / len(str_tokens_statement) > 0.7:
                continue
            if not intersection(this_part, str_tokens_answer) and this_part not in list_list_that:
                legal.append(num)
        rm_legal = []
        left_plc = []
        for i in legal:
            if this_one[i] == [] or if_have_ileage_word(this_one[i]):
                rm_legal.append(i)
                continue
            if len(this_one[i]) == 2 and this_one[i][0] in ["the"]:
                this_a_sent = "the public service is " + str(this_one[i][1])
                sen = nltk.word_tokenize(this_a_sent)
                tagged_sent = nltk.pos_tag(sen)
                if tagged_sent[-1][1] in ['NN', "NNS"]:
                    rm_legal.append(i)
                    continue
            if this_one[i][0] in it_set_0:
                rm_legal.append(i)
                continue
            if len(this_one[i]) == 1 and this_one[i][0] in it_set:
                rm_legal.append(i)
                continue
            if len(this_one[i]) == 1 and this_one[i][0] in single_ilegal_word_set:
                rm_legal.append(i)
                continue
            if tuple(this_one[i]) in ilegal_words_set or "way" in this_one[i] or this_one[i][0] == "that":
                rm_legal.append(i)
                continue
            if this_one[i] == [] or this_one[i] == ['as', 'well', 'as'] or this_one[i] == ["."]:
                rm_legal.append(i)
                continue
            this_i_plc = str_tokens_statement.index(this_one[i][0])
            this_i_tag_plc = tag_tokens_statement[this_i_plc]
            if len(this_one[i]) == 1 and this_i_tag_plc not in tag_set:
                left_plc.append(i)
                rm_legal.append(i)
        for i in rm_legal:
            legal.remove(i)
        if len(legal) == 0:
            continue
        a = []
        for i in range(len(legal)):
            a.append(i)

        final_out = []

        the_first = True
        for rdm in range(len(legal)):
            fina_article = statements[a_num][0]
            final_answer = list_to_str(this_one[legal[rdm]])
            tokens_article = tokenizer.tokenize(fina_article)
            tokens_answer = tokenizer.tokenize(final_answer)

            final_out.append([one[0], final_answer])

            print_out_data.append(list_to_str(tokens_article) + " [SEP] " + list_to_str(tokens_answer))
        print_out_data_jiancha.append(final_out)
        print_out_data_jilu.append({'source_answer': one[1],
                                    'source_question': one[3],
                                    'article': one[2],
                                    'GT': one[4],
                                    'index': one[5],
                                    'dataset': one[6]})

    data = open(args.for_unilm_file_path, 'w', encoding='utf-8')
    for i in print_out_data:
        print(i, file=data)
    data.close()

    np.save(args.information_file_path, print_out_data_jilu)
    np.save(args.answers_file_path, print_out_data_jiancha)


if __name__ == "__main__":
    main()
