## Detailed Introduction about the Involved Heuristic Rules

We have designed several heuristic rules to realize **the synthesis of the declarative sentence from wh-question and corresponding answer** and **the selection of potential target answers**. But due to the limited space in the paper, we only list some typical rules in the paper as examples. 

In this file, **we introduce all these heuristic rules in detail**.

---

### Detailed Rules for the Synthesis of Declarative Sentence from Wh-question and Corresponding Answer

#### Some Notions:
* [be] ---> ["be", "am", "is", "are", "was", "were"]
* [do] ---> ["do", "does", "did"]
* [aux] ---> ["will", "can", "must", "should", "would", "could", "may", "might", "has", "have", "had"]
* [answer] ---> answer
* [adj] ---> adjective, such as far, long, many, etc.
* prep ---> preposition.
* A ---> a subject.
* doing ---> a verb in the present continuous tense
* done ---> a passive verb.
* () ---> exist or not.

#### Rules for synthesis from Wh-question starting with `What`
* For declarative question containing "what", just replace "what" with answer.
* For "what" guided question:
  * what (noun) [be] A ---> A [be] [answer] (noun).
  * what (noun) [be] A doing (prep) ---> A [be] doing (prep) [answer] (noun).
  * what (noun) [be] A done prep ---> A [be] done prep [answer] (noun).
  * prep what (noun) [be] A doing ---> A [be] doing prep [answer] (noun).
  * prep what (noun) [be] A done ---> A [be] done prep [answer] (noun).
  * what (noun) [do] A do (prep) ---> A do (prep) [answer] (noun).
  * prep what (noun) [do] A do ---> A do prep [answer] (noun).
  * what (noun) [aux] A do/be (prep) ---> A [aux] do/be (prep) [answer] (noun).
  * prep what (noun) [aux] A do/be ---> A [aux] do/be prep [answer] (noun).

#### Rules for synthesis from Wh-question starting with `How`
* For declarative question containing "how", just replace "how" with answer.
* For "how" guided question:
  * how [be] A ---> A [be] [answer].
  * (by) how [be] A doing ---> A [be] doing by [answer].
  * (by) how [be] A done ---> A [be] done by [answer].
  * (by) how [do] A do ---> A do by [answer].
  * (by) how [aux] A do/be ---> A [aux] do/be by [answer].

#### Rules for synthesis from Wh-question starting with `How [adj]`
* For declarative question containing "how [adj]", just replace "how [adj]" with answer.
* For "how [adj]" guided question:
  * how [adj] (noun) [be] A ---> A [be] [answer] (noun).
  * how [adj] (noun) [be] A doing (prep) ---> A [be] doing (prep) [answer] (noun).
  * how [adj] (noun) [be] A done prep ---> A [be] done prep [answer] (noun).
  * prep how [adj] (noun) [be] A doing ---> A [be] doing prep [answer] (noun).
  * prep how [adj] (noun) [be] A done ---> A [be] done prep [answer] (noun).
  * how [adj] (noun) [do] A do (prep) ---> A do (prep) [answer] (noun).
  * prep how [adj] (noun) [do] A do ---> A do prep [answer] (noun).
  * how [adj] (noun) [aux] A do (prep) ---> A [aux] do (prep) [answer] (noun).
  * prep how [adj] (noun) [aux] A do/be ---> A [aux] do/be prep [answer] (noun).

#### Rules for synthesis from Wh-question starting with `Why`
* For declarative question containing "why", just replace "why" with answer.
* For "why" guided question:
  * why [be] A ... ---> A [be] ... because [answer].
  * why [be] A doing ---> A [be] doing because [answer].
  * why [be] A done ---> A [be] done because [answer].
  * why [do] A do ---> A do because [answer].
  * why [aux] A do/be ---> A [aux] do/be because [answer].

#### Rules for synthesis from Wh-question starting with `Who(Whom)`
* For declarative question containing "who(m)", just replace "who(m)" with answer.
* For "who(m)" guided question:
  * who [be] ---> [answer] [be]
  * who [be] A ---> A [be] [answer].
  * who [be] doing ---> [answer] [be] doing.
  * who [be] A doing (prep) ---> A [be] doing (prep) [answer].
  * who [be] done ---> [answer] [be] done.
  * who [be] A done prep ---> A [be] done prep [answer].
  * prep whom [be] A done ---> A [be] done prep [answer].
  * who do ---> [answer] do.
  * who [do] A do (prep) ---> A do (prep) [answer].
  * prep whom [do] A do ---> A do (prep) [answer].
  * who [aux] do/be ---> [answer] [aux] do/be.
  * who [aux] A do/be (prep) ---> A [aux] do/be (prep) [answer].
  * prep whom [aux] A do/be ---> A [aux] do/be (prep) [answer].

#### Rules for synthesis from Wh-question starting with `Whose`
* For declarative question containing "whose", just replace "whose" with answer.
* For "whose" guided question:
  * whose noun [be] A ---> A [be] [answer] ['s] noun.
  * whose noun [be] A doing (prep) ---> A [be] doing (prep) [answer] ['s] noun.
  * whose noun [be] A done prep ---> A [be] done prep [answer] ['s] noun.
  * prep whose noun [be] A doing ---> A [be] doing prep [answer] ['s] noun.
  * prep whose noun [be] A done ---> A [be] done prep [answer] ['s] noun.
  * whose noun [do] A do (prep) ---> A do (prep) [answer] ['s] noun.
  * prep whose noun [do] A do ---> A do prep [answer] ['s] noun.
  * whose noun [aux] A do/be (prep) ---> A [aux] do/be (prep) [answer] ['s] noun.
  * prep whose noun [aux] A do/be ---> A [aux] do/be prep [answer] ['s] noun.

#### Rules for synthesis from Wh-question starting with `Where`
* For declarative question containing "where", just replace "where" with answer.
* For "where" guided question:
  * (prep) where [be] A ---> A [be] prep [answer].
  * (prep) where [be] A doing ---> A [be] doing prep [answer].
  * (prep) where [be] A done ---> A [be] done prep [answer].
  * (prep) where [do] A do ---> A do prep [answer].
  * (prep) where [aux] A do/be ---> A [aux] do/be prep [answer].

#### Rules for synthesis from Wh-question starting with `When`
* For declarative question containing "when", just replace "when" with answer.
* For "when" guided question:
  * when [be] A ---> A [be] prep [answer].
  * when [be] A doing ---> A [be] doing prep [answer].
  * when [be] A done ---> A [be] done prep [answer].
  * when [do] A do ---> A do prep [answer].
  * when [aux] A do/be ---> A [aux] do/be prep [answer].

#### Rules for synthesis from Wh-question starting with `Which`
* For declarative question containing "which", just replace "which" with answer.
* For "which" guided question:
  * which noun [be] A ---> A [be] [answer] noun.
  * which noun [be] A doing (prep) ---> A [be] doing (prep) [answer] noun.
  * which noun [be] A done prep ---> A [be] done prep [answer] noun.
  * prep which  noun [be] A doing ---> A [be] doing prep [answer] noun.
  * prep which noun [be] A done ---> A [be] done prep [answer] noun.
  * which noun [do] A do (prep) ---> A do (prep) [answer] noun.
  * prep which noun [do] A do ---> A do prep [answer] noun.
  * which noun [aux] A do/be (prep) ---> A [aux] do/be (prep) [answer] noun.
  * prep which noun [aux] A do/be ---> A [aux] do/be prep [answer] noun.

---

### Detailed Rules for the Selection of Potential Target Answers

#### Some Notions:
* ADJ: adjective
* ADP: adjective phrase
* NOUN: noun
* PROPN: proper noun
* NUM: number
* CCONJ: coordinating conjunction
* [attributive clause]: attributive clause
* [possessive pronoun]: my, his, her, its, their

#### Rules for Adjective/Noun Phrase Selection
1. ADJ/ADJP                                                 
  *Expected question format: `How be A ?`, `What kind of A be/[aux]/do ...`*
2. ADJ/ADJP + CCONJ + ADJ/ADJP + CCONJ + ...              
  *Expected question format: `How be A ?`, `What kind of A be/[aux]/do ...`*
3. (NUM) + (1/2) + NOUN/PROPN + ([attributive clause])  
  *Expected question format: `What [aux]/do A do ... ?`, `What ([aux]) be A ... ?`, `Who ([aux]) do ... ?`, `Who ([aux]) be ... ?`, `Which noun [aux]/do A do ...?`, `Which noun be A ...?`, `Which noun be/[aux]/do ...?`*
4. (NUM) + (1/2) + PROPN + [attributive clause]       
  *Expected question format: `What [aux]/do A do ... ?`, `What ([aux]) be A ... ?`, `Who ([aux]) do ... ?`, `Who ([aux]) be ... ?`, `Which noun [aux]/do A do ...`, `Which noun be A ...?`, `Which noun be/[aux]/do ...?`*
5. 3/4 + CCONJ + 3/4 + CCONJ + ...                        
  *Expected question format: `What [aux]/do A do ... ?`, `What ([aux]) be A ... ?`, `Who ([aux]) do ... ?`, `Who ([aux]) be ... ?`, `Which noun [aux]/do A do ...`, `Which noun be A ...?`, `Which noun be/[aux]/do ...?`*

#### Rules for Unsuitable Answer Exclusion
* *original answer (source output)*
* PRON
* PRON + CCONJ + PRON + CCONJ + ...
* [possessive pronoun] + (ADJ/ADJP (+ CCONJ + ...)) + NOUN

---

*Return to [README](README.md)*
