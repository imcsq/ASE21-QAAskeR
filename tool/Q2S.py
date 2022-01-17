import json
import spacy
import string
import nltk
import argparse
import numpy as np
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from pattern.text.en import conjugate, lemma, lexeme, PRESENT, INFINITIVE, PAST, FUTURE, SG, PLURAL, PROGRESSIVE
from wh_rules.howmany import howmany
from wh_rules.what import what
from wh_rules.how import how
from wh_rules.why import why
from wh_rules.who import who
from wh_rules.whose import whose
from wh_rules.where import where
from wh_rules.when import when
from wh_rules.which import which


nlp = spacy.load('en_core_web_sm')


this_what = what()
this_how = how()
this_howmany = howmany()
this_why = why()
this_who = who()
this_whose = whose()
this_where = where()
this_when = when()
this_which = which()


def change(question, answer):
    if "can't " in question:
        question = question.replace("can't ", "can not ")
    elif "won't " in question:
        question = question.replace("won't ", "will not ")
    elif "couldn't " in question:
        question = question.replace("couldn't ", "could not ")
    elif "shouldn't " in question:
        question = question.replace("shouldn't ", "should not ")
    elif "haven't " in question:
        question = question.replace("haven't ", "have not ")
    elif "hasn't " in question:
        question = question.replace("hasn't ", "has not ")
    elif "mustn't " in question:
        question = question.replace("mustn't ", "must not ")
    elif "aren't " in question:
        question = question.replace("aren't ", "are not ")
    elif "isn't " in question:
        question = question.replace("isn't ", "is not ")
    elif "weren't " in question:
        question = question.replace("weren't ", "were not ")
    elif "wasn't " in question:
        question = question.replace("wasn't ", "was not ")
    elif "don't " in question:
        question = question.replace("don't ", "do not ")
    elif "doesn't " in question:
        question = question.replace("doesn't ", "does not ")
    elif "didn't " in question:
        question = question.replace("didn't ", "did not ")
    if "dont " in question:
        question = question.replace("dont ", "do not ")
    if "How man " in question:
        question = question.replace("How man ", "How many ")
    if "How maney " in question:
        question = question.replace("How maney ", "How many ")
    doc_question = nlp(question)
    tokens_question = [token for token in doc_question]
    tokens_question_lemma = [token.lemma_ for token in doc_question]
    tokens_question_pos = [token.pos_ for token in doc_question]
    str_tokens_question = [token.text for token in doc_question]
    boolean_start = ["be", "do", "will", "can", "should", "may", "have", "must", "would", "am", "could", "shell", "might"]
    if tokens_question[0].lemma_ in ["how", "what", "who", "why", "whose", "where", "when", "which"]:
        if tokens_question_lemma[0] == 'how' and tokens_question_pos[1] in ['ADJ', 'ADV']:
            statement = this_howmany.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "what" or ("what" in str_tokens_question and tokens_question[0].lemma_ != "who"):
            statement = this_what.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "who":
            statement = this_who.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "why" or ", why " in question:
            statement = this_why.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "whose":
            statement = this_whose.generate(question, answer)
            return statement
        elif "When and where" in question or "Where and when" in question:
            new_question = question
            if "When and where" in question:
                new_question = question.replace("When and where", "Where")
            if "Where and when" in question:
                new_question = question.replace("Where and when", "Where")
            statement = this_where.generate(new_question, answer)
            return statement
        elif tokens_question[0].lemma_ == "where":
            statement = this_where.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "when":
            statement = this_when.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "how":
            statement = this_how.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "which":
            statement = this_which.generate(question, answer)
            return statement
    if tokens_question[0].lemma_ in boolean_start:
        return
    elif 'how' in tokens_question_lemma:
        how_index = tokens_question_lemma.index('how')
        if how_index != len(tokens_question_lemma)-1:
            if tokens_question_lemma[how_index+1] in ['ADJ', 'ADV']:
                statement = this_howmany.generate(question, answer)
                return statement
        statement = this_how.generate(question, answer)
        return statement
    elif "what" in tokens_question_lemma:
        statement = this_what.generate(question, answer)
        return statement
    elif "who" in tokens_question_lemma or "whom" in tokens_question_lemma:
        statement = this_who.generate(question, answer)
        return statement
    elif "why" in tokens_question_lemma:
        statement = this_why.generate(question, answer)
        return statement
    elif "whose" in tokens_question_lemma:
        statement = this_whose.generate(question, answer)
        return statement
    elif "where" in tokens_question_lemma or "in which" in str_tokens_question or "In which" in str_tokens_question:
        statement = this_where.generate(question, answer)
        return statement
    elif "when" in tokens_question_lemma:
        statement = this_when.generate(question, answer)
        return statement
    elif "which" in tokens_question_lemma:
        statement = this_which.generate(question, answer)
        return statement


def this_main(npy_file_path, out_file_path):
    print_out_data = []
    output = np.load(npy_file_path, allow_pickle=True)
    output = output.tolist()
    for a_num in tqdm(range(len(output))):
        i = output[a_num]
        question = i[0]
        if "can't " in question:
            question = question.replace("can't ", "can not ")
        elif "won't " in question:
            question = question.replace("won't ", "will not ")
        elif "couldn't " in question:
            question = question.replace("couldn't ", "could not ")
        elif "shouldn't " in question:
            question = question.replace("shouldn't ", "should not ")
        elif "haven't " in question:
            question = question.replace("haven't ", "have not ")
        elif "hasn't " in question:
            question = question.replace("hasn't ", "has not ")
        elif "mustn't " in question:
            question = question.replace("mustn't ", "must not ")
        elif "aren't " in question:
            question = question.replace("aren't ", "are not ")
        elif "isn't " in question:
            question = question.replace("isn't ", "is not ")
        elif "weren't " in question:
            question = question.replace("weren't ", "were not ")
        elif "wasn't " in question:
            question = question.replace("wasn't ", "was not ")
        elif "don't " in question:
            question = question.replace("don't ", "do not ")
        elif "doesn't " in question:
            question = question.replace("doesn't ", "does not ")
        elif "didn't " in question:
            question = question.replace("didn't ", "did not ")
        if "dont " in question:
            question = question.replace("dont ", "do not ")
        if "How man " in question:
            question = question.replace("How man ", "How many ")
        if "How maney " in question:
            question = question.replace("How maney ", "How many ")
        doc_question = nlp(question)
        tokens_question = [token for token in doc_question]
        tokens_question_lemma = [token.lemma_ for token in doc_question]
        tokens_question_pos = [token.pos_ for token in doc_question]
        str_tokens_question = [token.text for token in doc_question]
        boolean_start = ["be", "do", "will", "can", "should", "may", "have", "must", "would", "am", "could", "shell", "might"]
        if tokens_question[0].lemma_ in ["how", "what", "who", "why", "whose", "where", "when", "which"]:
            if tokens_question_lemma[0] == 'how' and tokens_question_pos[1] in ['ADJ', 'ADV']:
                statement = this_howmany.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "what" or ("what" in str_tokens_question and tokens_question[0].lemma_ != "who"):
                statement = this_what.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "who":
                statement = this_who.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "why" or ", why " in question:
                statement = this_why.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "whose":
                statement = this_whose.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif "When and where" in question or "Where and when" in question:
                new_question = question
                if "When and where" in question:
                    new_question = question.replace("When and where", "Where")
                if "Where and when" in question:
                    new_question = question.replace("Where and when", "Where")
                if new_question != question:
                    statement = this_where.generate(new_question, i[1])
                    if statement is None:
                        continue
                    print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                    continue
                continue
            elif tokens_question[0].lemma_ == "where":
                statement = this_where.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "when":
                statement = this_when.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "how":
                statement = this_how.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
            elif tokens_question[0].lemma_ == "which":
                statement = this_which.generate(question, i[1])
                if statement is None:
                    continue
                print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                continue
        if tokens_question[0].lemma_ in boolean_start:
            continue
        elif 'how' in tokens_question_lemma:
            how_index = tokens_question_lemma.index('how')
            if how_index != len(tokens_question_lemma)-1:
                if tokens_question_lemma[how_index+1] in ['ADJ', 'ADV']:
                    statement = this_howmany.generate(question, i[1])
                    if statement is None:
                        continue
                    print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
                    continue
            statement = this_how.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "what" in tokens_question_lemma:
            statement = this_what.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "who" in tokens_question_lemma or "whom" in tokens_question_lemma:
            statement = this_who.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "why" in tokens_question_lemma:
            statement = this_why.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "whose" in tokens_question_lemma:
            statement = this_whose.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "where" in tokens_question_lemma or "in which" in str_tokens_question or "In which" in str_tokens_question:
            statement = this_where.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "when" in tokens_question_lemma:
            statement = this_when.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
        elif "which" in tokens_question_lemma:
            statement = this_which.generate(question, i[1])
            if statement is None:
                continue
            print_out_data.append({'statement': str(statement), 'answer': i[1], 'article': i[2], 'question': question, 'GT': i[5], 'index': i[3], 'dataset': i[4]})
            continue
    np.save(out_file_path, print_out_data)


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
    this_main(args.npy_file_path, args.out_file_path)


if __name__ == "__main__":
    main()