#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S      // указываем корневой нетерминал грамматики


S -> adj_mod_of interp (Relation.adj_mod_of::norm="m,sg") |
     adv_of interp (Relation.adv_of::norm="inf") |
     adv interp (Relation.adv::norm="inf") |
     subj_of interp (Relation.subj_of::norm="inf,sg");

adj_mod_of -> Adj<gnc-agr[1]> Noun<gnc-agr[1]>;
adv_of -> Adv Verb;
adv -> Verb Adv;
subj_of -> Noun<sp-agr[1]> Verb<sp-agr[1]>;
subj -> Verb<sp-agr[1]> Noun<sp-agr[1]>;
