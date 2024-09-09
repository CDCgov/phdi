BEGIN;


INSERT INTO conditions VALUES('1','DIBBs Local Code System','Newborn Screening','20240909');
INSERT INTO conditions VALUES('2','DIBBs Local Code System','Cancer (Leukemia)','20240909');
INSERT INTO conditions VALUES('3','DIBBs Local Code System','Social Determinants of Health','20240909'); -- has no valuesets

-- Newborn Screening valueset(s)
INSERT INTO valuesets VALUES('1_20240909','1','20240909','Newborn Screening','DIBBs','lotc');

-- Cancer (Leukemia) valueset(s)
INSERT INTO valuesets VALUES('2_20240909','2','20240909','Cancer (Leukemia)','DIBBs','dxtc');
INSERT INTO valuesets VALUES('3_20240909','3','20240909','Cancer Leukemia','DIBBs','mrtc');


-- Newborn Screening concepts
INSERT INTO concepts VALUES('1_73700-7','73700-7','http://loinc.org','CCHD newborn screening interpretation','737007','2024-09');
INSERT INTO concepts VALUES('1_73698-3','73698-3','http://loinc.org','Reason CCHD oxygen saturation screening not performed','736983','2024-09');
INSERT INTO concepts VALUES('1_54108-6','54108-6','http://loinc.org','Newborn hearing screen of Ear - left','541086','2024-09');
INSERT INTO concepts VALUES('1_54109-4','54109-4','http://loinc.org','Newborn hearing screen of Ear - right','541094','2024-09');
INSERT INTO concepts VALUES('1_58232-0','58232-0','http://loinc.org','Hearing loss risk indicators','582320','2024-09');
INSERT INTO concepts VALUES('1_57700-7','57700-7','http://loinc.org','Hearing loss newborn screening comment-discussion','577007','2024-09');
INSERT INTO concepts VALUES('1_73739-5','73739-5','http://loinc.org','Newborn hearing screen reason not performed of Ear - left','737395','2024-09');
INSERT INTO concepts VALUES('1_73742-9','73742-9','http://loinc.org','Newborn hearing screen reason not performed of Ear - right','737429','2024-09');
INSERT INTO concepts VALUES('1_2708-6','2708-6','http://loinc.org','Cannabinoids [Presence] in Vitreous fluid','27086','2024-09');
INSERT INTO concepts VALUES('1_8336-0','8336-0','http://loinc.org','Body weight [Percentile] Per age','83360','2024-09');

-- Cancer (Leukemia) concepts
INSERT into concepts VALUES('1_92814006','92814006','http://www.nlm.nih.gov/research/umls/rxnorm','Chronic lymphoid leukemia, disease (disorder)','92814006','2024-09');
INSERT into concepts VALUES('1_828265','828265','http://www.nlm.nih.gov/research/umls/rxnorm','1 ML alemtuzumab 30 MG/ML Injection','828265','2024-09');


--  
INSERT INTO condition_to_valueset VALUES('1514','1','1_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1515','2','1_92814006','DIBBs');


-- Newborn Screening valueset to concept mappings
INSERT INTO valueset_to_concept VALUES('45274','1_20240909','1_73700-7');
INSERT INTO valueset_to_concept VALUES('45275','1_20240909','1_73698-3');
INSERT INTO valueset_to_concept VALUES('45276','1_20240909','1_54108-6');
INSERT INTO valueset_to_concept VALUES('45277','1_20240909','1_54109-4');
INSERT INTO valueset_to_concept VALUES('45278','1_20240909','1_58232-0');
INSERT INTO valueset_to_concept VALUES('45279','1_20240909','1_57700-7');
INSERT INTO valueset_to_concept VALUES('45280','1_20240909','1_73739-5');
INSERT INTO valueset_to_concept VALUES('45281','1_20240909','1_73742-9');
INSERT INTO valueset_to_concept VALUES('45282','1_20240909','1_2708-6');
INSERT INTO valueset_to_concept VALUES('45283','1_20240909','1_8336-0');
INSERT INTO valueset_to_concept VALUES('45284','1_92814006','1_92814006');


COMMIT;

