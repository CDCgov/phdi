BEGIN;

INSERT INTO conditions VALUES('1','DIBBs Local Code System','Newborn Screening','20240909');
INSERT INTO conditions VALUES('2','DIBBs Local Code System','Cancer (Leukemia)','20240909');
INSERT INTO conditions VALUES('3','DIBBs Local Code System','Social Determinants of Health','20240909'); -- has no valuesets

-- Newborn Screening valueset(s)
INSERT INTO valuesets VALUES('1_20240909','1','20240909','Newborn Screening','DIBBs','lotc');

-- Cancer (Leukemia) valueset(s)
INSERT INTO valuesets VALUES('2_20240909','2','20240909','Cancer (Leukemia)','DIBBs','dxtc');
INSERT INTO valuesets VALUES('3_20240909','3','20240909','Cancer Leukemia','DIBBs','mrtc');

-- Missing Syphilis valueset(s)
INSERT INTO valuesets VALUES('4_20240909','4','20240909','Missing Syphilis mrtc','DIBBs','mrtc');
INSERT INTO valuesets VALUES('5_20240909','5','20240909','Missing Syphilis dxtc','DIBBs','dxtc');
INSERT INTO valuesets VALUES('6_20240909','6','20240909','Missing Syphilis sdtc','DIBBs','sdtc');

-- Missing Gonorhea valueset(s)
INSERT INTO valuesets VALUES('7_20240909','7','20240909','Missing Gonorhea mrtc','DIBBs','mrtc');
INSERT INTO valuesets VALUES('8_20240909','8','20240909','Missing Gonorhea dxtc','DIBBs','dxtc');
INSERT INTO valuesets VALUES('9_20240909','9','20240909','Missing Gonorhea lotc','DIBBs','lotc');
INSERT INTO valuesets VALUES('10_20240909','10','20240909','Missing Gonorhea lrtc','DIBBs','lrtc');

-- Missing Chlamydia valueset(s)
INSERT INTO valuesets VALUES('11_20240910','11','20240910','Missing Chlamydia mrtc','DIBBs','mrtc');
INSERT INTO valuesets VALUES('12_20240910','12','20240910','Missing Chlamydia lrtc','DIBBs','lrtc');
INSERT INTO valuesets VALUES('13_20240910','13','20240910','Missing Chlamydia sdtc','DIBBs','sdtc');


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
INSERT INTO concepts VALUES('1_828265','828265','http://www.nlm.nih.gov/research/umls/rxnorm','1 ML alemtuzumab 30 MG/ML Injection','828265','2024-09');

-- Missing Syphilis concepts
INSERT INTO concepts VALUES('1_2671695','2671695','http://www.nlm.nih.gov/research/umls/rxnorm','penicillin G benzathine 2400000 UNT Injection','2671695','2024-09');
INSERT INTO concepts VALUES('1_186647001','186647001','http://snomed.info/sct','Primary genital syphilis','186647001','2024-09');

-- Missing Gonorrhea & Chlamydia concepts
INSERT INTO concepts VALUES('1_434692','434692','http://www.nlm.nih.gov/research/umls/rxnorm','azithromycin 1000 MG','434692','2024-09');
INSERT INTO concepts VALUES('1_1665005','1665005','http://www.nlm.nih.gov/research/umls/rxnorm','ceftriaxone 500 MG Injection','1665005','2024-09');
 
INSERT INTO concepts VALUES('1_72531000052105','72531000052105 ','http://snomed.info/sct','Counseling for contraception','72531000052105','2024-09');
INSERT INTO concepts VALUES('1_11350-6','11350-6','http://loinc.org','History of Sexual behavior Narrative','113506','2024-09');
INSERT INTO concepts VALUES('1_82810-3','82810-3','http://loinc.org','Pregnancy status','828103','2024-09');
INSERT INTO concepts VALUES('1_83317-8','83317-8','http://loinc.org','Sexual activity with anonymous partner in the past year','833178','2024-09');

INSERT INTO concepts VALUES('1_82122','82122','https://www.nlm.nih.gov/research/umls/rxnorm','levofloxacin','82122','2024-09');
INSERT INTO concepts VALUES('1_1649987','1649987','https://www.nlm.nih.gov/research/umls/rxnorm','doxycycline hyclate 100 MG','1649987','2024-09');
INSERT INTO concepts VALUES('1_72828-7','72828-7','http://loinc.org','Chlamydia trachomatis and Neisseria gonorrhoeae DNA panel - Specimen','728287','2024-09');
INSERT INTO concepts VALUES('1_2339001','2339001','http://snomed.info/sct','Sexual overexposure','2339001','2024-09');

-- Newborn Screening condition to valueset mappings
INSERT INTO condition_to_valueset VALUES('1514','1','1_20240909','DIBBs');

-- Cancer (Leukemia) condition to valueset mappings
INSERT INTO condition_to_valueset VALUES('1515','2','2_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1516','3','3_20240909','DIBBs');

-- Missing Syphilis condition to valueset mappings
INSERT INTO condition_to_valueset VALUES('1517','35742006','4_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1518','35742006','5_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1519','35742006','6_20240909','DIBBs');

-- Missing Gonorhea condition to valueset mappings
INSERT INTO condition_to_valueset VALUES('1520','15628003','7_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1521','15628003','8_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1522','15628003','9_20240909','DIBBs');
INSERT INTO condition_to_valueset VALUES('1523','15628003','10_20240909','DIBBs');

-- Missing Chlamydia condition to valueset mappings
INSERT INTO condition_to_valueset VALUES('1524','240589008','11_20240910','DIBBs');
INSERT INTO condition_to_valueset VALUES('1525','240589008','12_20240910','DIBBs');
INSERT INTO condition_to_valueset VALUES('1526','240589008','13_20240910','DIBBs');

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


-- Cancer (Leukemia) valueset to concept mappings
INSERT INTO valueset_to_concept VALUES('45284','2_20240909','2.16.840.1.113762.1.4.1146.1407_92814006');
INSERT INTO valueset_to_concept VALUES('45285','3_20240909','1_828265');

-- Missing Syphilis valueset to concept mappings
INSERT INTO valueset_to_concept VALUES('45286','4_20240909','1_2671695');
INSERT INTO valueset_to_concept VALUES('45287','5_20240909','2.16.840.1.113762.1.4.1146.395_76272004');
INSERT INTO valueset_to_concept VALUES('45288','6_20240909','1_186647001');

-- Missing Gonorrhea valueset to concept mappings
INSERT INTO valueset_to_concept VALUES('45289','7_20240909','1_434692');
INSERT INTO valueset_to_concept VALUES('45290','7_20240909','1_1665005');
INSERT INTO valueset_to_concept VALUES('45292','8_20240909','1_2339001');
INSERT INTO valueset_to_concept VALUES('45293','8_20240909','1_72531000052105');
INSERT INTO valueset_to_concept VALUES('45294','9_20240909','1_11350-6');
INSERT INTO valueset_to_concept VALUES('45295','10_20240909','2.16.840.1.113762.1.4.1146.239_21613-5');
INSERT INTO valueset_to_concept VALUES('45296','10_20240909','1_82810-3');
INSERT INTO valueset_to_concept VALUES('45297','10_20240909','1_83317-8');

-- Missing Chlamydia valueset to concept mappings
INSERT INTO valueset_to_concept VALUES('45298','11_20240910','1_434692');
INSERT INTO valueset_to_concept VALUES('45299','11_20240910','1_82122');
INSERT INTO valueset_to_concept VALUES('45300','11_20240910','1_1649987');
INSERT INTO valueset_to_concept VALUES('45301','11_20240910','1_1665005');
INSERT INTO valueset_to_concept VALUES('45302','12_20240910','2.16.840.1.113762.1.4.1146.244_24111-7');
INSERT INTO valueset_to_concept VALUES('45303','12_20240910','2.16.840.1.113762.1.4.1146.239_21613-5');
INSERT INTO valueset_to_concept VALUES('45304','12_20240910','1_82810-3');
INSERT INTO valueset_to_concept VALUES('45305','12_20240910','1_83317-8');
INSERT INTO valueset_to_concept VALUES('45306','12_20240910','1_11350-6');
INSERT INTO valueset_to_concept VALUES('45307','12_20240910','1_72828-7');
INSERT INTO valueset_to_concept VALUES('45308','13_20240910','1_72531000052105');
INSERT INTO valueset_to_concept VALUES('45309','13_20240910','1_2339001');




COMMIT;
