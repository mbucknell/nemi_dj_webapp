-- do this last

CREATE OR REPLACE PACKAGE BODY MERGE_STG_TO_PROD AS
/******************************************************************************
   NAME:       MergeMethods
   PURPOSE:

   REVISIONS:
   Ver        Date        Author           Description
   ---------  ----------  ---------------  ------------------------------------
   1.0        3/31/2008             1. Created this package body.
******************************************************************************/
  PROCEDURE RefreshMethods is
  begin
    MergeMethods;
    MergeAnalytes;
    MergeRevisions;
    ReloadMethodFact;
    RebuildIndexes;
    end;

  PROCEDURE MergeMethods IS
  BEGIN
  execute immediate 'ALTER TRIGGER CG$AIS_METHOD DISABLE';
  execute immediate 'ALTER TRIGGER CG$AUS_METHOD DISABLE';
    MERGE INTO method B
USING (
  SELECT *
  FROM method_stg where approved = 'Y' AND METHOD_ID IN ('11355','11356','11353','11358','9928','9926','11362','9931','9927','9932','11351','9929','9930','9933','11352','11365')) E ON (B.method_id = E.method_id)
WHEN MATCHED THEN
  UPDATE SET
  b.METHOD_SUBCATEGORY_ID = e.METHOD_SUBCATEGORY_ID,
b.METHOD_SOURCE_ID = e.METHOD_SOURCE_ID,
b.SOURCE_CITATION_ID = e.SOURCE_CITATION_ID,
b.SOURCE_METHOD_IDENTIFIER = e.SOURCE_METHOD_IDENTIFIER,
b.METHOD_DESCRIPTIVE_NAME = e.METHOD_DESCRIPTIVE_NAME,
b.METHOD_OFFICIAL_NAME = e.METHOD_OFFICIAL_NAME,
b.MEDIA_NAME = e.MEDIA_NAME,
b.BRIEF_METHOD_SUMMARY = e.BRIEF_METHOD_SUMMARY,
b.SCOPE_AND_APPLICATION = e.SCOPE_AND_APPLICATION,
b.DL_TYPE_ID = e.DL_TYPE_ID,
b.DL_NOTE = e.DL_NOTE,
b.APPLICABLE_CONC_RANGE = e.APPLICABLE_CONC_RANGE,
b.CONC_RANGE_UNITS = e.CONC_RANGE_UNITS,
b.INTERFERENCES = e.INTERFERENCES,
b.QC_REQUIREMENTS = e.QC_REQUIREMENTS,
b.SAMPLE_HANDLING = e.SAMPLE_HANDLING,
b.MAX_HOLDING_TIME = e.MAX_HOLDING_TIME,
b.SAMPLE_PREP_METHODS = e.SAMPLE_PREP_METHODS,
b.RELATIVE_COST_ID = e.RELATIVE_COST_ID,
b.LINK_TO_FULL_METHOD = e.LINK_TO_FULL_METHOD,
b.INSERT_DATE = e.INSERT_DATE,
b.INSERT_PERSON_NAME = e.INSERT_PERSON_NAME,
b.LAST_UPDATE_DATE = e.LAST_UPDATE_DATE,
b.LAST_UPDATE_PERSON_NAME = e.LAST_UPDATE_PERSON_NAME,
b.APPROVED = e.APPROVED,
b.APPROVED_DATE = e.APPROVED_DATE,
b.INSTRUMENTATION_ID = e.INSTRUMENTATION_ID,
b.PRECISION_DESCRIPTOR_NOTES = e.PRECISION_DESCRIPTOR_NOTES,
b.RAPIDITY = e.RAPIDITY,
b.CBR_ONLY = e.CBR_ONLY,
b.WATERBODY_TYPE = e.WATERBODY_TYPE,
b.MATRIX = e.MATRIX,
b.TECHNIQUE = e.TECHNIQUE,
b.SCREENING = e.SCREENING,
b.ETV_LINK = e.ETV_LINK,
b.DATE_LOADED = sysdate,
b.REVIEWER_NAME = e.REVIEWER_NAME,
b.REGS_ONLY = e.REGS_ONLY,
b.METHOD_TYPE_ID = e.METHOD_TYPE_ID,
b.COLLECTED_SAMPLE_AMT_ML = e.COLLECTED_SAMPLE_AMT_ML,
b.COLLECTED_SAMPLE_AMT_G = e.COLLECTED_SAMPLE_AMT_G,
b.LIQUID_SAMPLE_FLAG = e.LIQUID_SAMPLE_FLAG,
b.ANALYSIS_AMT_ML = e.ANALYSIS_AMT_ML,
b.ANALYSIS_AMT_G = e.ANALYSIS_AMT_G,
b.PH_OF_ANALYTICAL_SAMPLE = e.PH_OF_ANALYTICAL_SAMPLE,
b.CALC_WASTE_AMT = e.CALC_WASTE_AMT,
b.QUALITY_REVIEW_ID = e.QUALITY_REVIEW_ID,
b.PBT = e.PBT,
b.TOXIC  = e.TOXIC ,
b.CORROSIVE = e.CORROSIVE,
b.WASTE = e.WASTE,
b.ASSUMPTIONS_COMMENTS = e.ASSUMPTIONS_COMMENTS
WHEN NOT MATCHED THEN
  INSERT (b.METHOD_ID,
b.METHOD_SUBCATEGORY_ID,
b.METHOD_SOURCE_ID,
b.SOURCE_CITATION_ID,
b.SOURCE_METHOD_IDENTIFIER,
b.METHOD_DESCRIPTIVE_NAME,
b.METHOD_OFFICIAL_NAME,
b.MEDIA_NAME,
b.BRIEF_METHOD_SUMMARY,
b.SCOPE_AND_APPLICATION,
b.DL_TYPE_ID,
b.DL_NOTE,
b.APPLICABLE_CONC_RANGE,
b.CONC_RANGE_UNITS,
b.INTERFERENCES,
b.QC_REQUIREMENTS,
b.SAMPLE_HANDLING,
b.MAX_HOLDING_TIME,
b.SAMPLE_PREP_METHODS,
b.RELATIVE_COST_ID,
b.LINK_TO_FULL_METHOD,
b.INSERT_DATE,
b.INSERT_PERSON_NAME,
b.LAST_UPDATE_DATE,
b.LAST_UPDATE_PERSON_NAME,
b.APPROVED,
b.APPROVED_DATE,
b.INSTRUMENTATION_ID,
b.PRECISION_DESCRIPTOR_NOTES,
b.RAPIDITY,
b.CBR_ONLY,
b.WATERBODY_TYPE,
b.MATRIX,
b.TECHNIQUE,
b.SCREENING,
b.ETV_LINK,
b.DATE_LOADED,
b.REVIEWER_NAME,
b.REGS_ONLY,
b.METHOD_TYPE_ID,
b.COLLECTED_SAMPLE_AMT_ML,
b.COLLECTED_SAMPLE_AMT_G,
b.LIQUID_SAMPLE_FLAG,
b.ANALYSIS_AMT_ML,
b.ANALYSIS_AMT_G,
b.PH_OF_ANALYTICAL_SAMPLE,
b.CALC_WASTE_AMT,
b.QUALITY_REVIEW_ID ,
b.PBT,
b.TOXIC ,
b.CORROSIVE,
b.WASTE ,
b.ASSUMPTIONS_COMMENTS  )
  VALUES (E.METHOD_ID,
E.METHOD_SUBCATEGORY_ID,
E.METHOD_SOURCE_ID,
E.SOURCE_CITATION_ID,
E.SOURCE_METHOD_IDENTIFIER,
E.METHOD_DESCRIPTIVE_NAME,
E.METHOD_OFFICIAL_NAME,
E.MEDIA_NAME,
E.BRIEF_METHOD_SUMMARY,
E.SCOPE_AND_APPLICATION,
E.DL_TYPE_ID,
E.DL_NOTE,
E.APPLICABLE_CONC_RANGE,
E.CONC_RANGE_UNITS,
E.INTERFERENCES,
E.QC_REQUIREMENTS,
E.SAMPLE_HANDLING,
E.MAX_HOLDING_TIME,
E.SAMPLE_PREP_METHODS,
E.RELATIVE_COST_ID,
E.LINK_TO_FULL_METHOD,
E.INSERT_DATE,
E.INSERT_PERSON_NAME,
E.LAST_UPDATE_DATE,
E.LAST_UPDATE_PERSON_NAME,
E.APPROVED,
E.APPROVED_DATE,
E.INSTRUMENTATION_ID,
E.PRECISION_DESCRIPTOR_NOTES,
E.RAPIDITY,
E.CBR_ONLY,
E.WATERBODY_TYPE,
E.MATRIX,
E.TECHNIQUE,
E.SCREENING,
E.ETV_LINK,
E.DATE_LOADED,
E.REVIEWER_NAME,
E.REGS_ONLY,
E.METHOD_TYPE_ID,
e.COLLECTED_SAMPLE_AMT_ML,
e.COLLECTED_SAMPLE_AMT_G,
e.LIQUID_SAMPLE_FLAG,
e.ANALYSIS_AMT_ML,
e.ANALYSIS_AMT_G,
e.PH_OF_ANALYTICAL_SAMPLE,
e.CALC_WASTE_AMT,
e.QUALITY_REVIEW_ID,
e.PBT,
e.TOXIC ,
e.CORROSIVE,
e.WASTE,
e.ASSUMPTIONS_COMMENTS
  );
  commit;
    execute immediate 'ALTER TRIGGER CG$AIS_METHOD ENABLE';
  execute immediate 'ALTER TRIGGER CG$AUS_METHOD ENABLE';
  END;

PROCEDURE MergeAnalytes IS
  BEGIN
  execute immediate 'ALTER TRIGGER CG$AIS_ANALYTE_METHOD_JN DISABLE';
  execute immediate 'ALTER TRIGGER CG$AUS_ANALYTE_METHOD_JN DISABLE';
    MERGE INTO analyte_method_jn B
USING (
  SELECT *
 FROM analyte_method_jn_stg amj where exists(select 1 from method_stg m where m.method_id = amj.method_id and m.approved = 'Y') AND METHOD_ID IN ('11355','11356','11353','11358','9928','9926','11362','9931','9927','9932','11351','9929','9930','9933','11352','11365')) E
ON (B.analyte_method_id = E.analyte_method_id)
WHEN MATCHED THEN
  UPDATE SET
b.DATE_LOADED = sysdate,
b.METHOD_ID = e.METHOD_ID,
b.ANALYTE_ID = e.ANALYTE_ID,
b.DL_VALUE = e.DL_VALUE,
b.DL_UNITS = e.DL_UNITS,
b.ACCURACY = e.ACCURACY,
b.ACCURACY_UNITS = e.ACCURACY_UNITS,
b.FALSE_POSITIVE_VALUE = e.FALSE_POSITIVE_VALUE,
b.FALSE_NEGATIVE_VALUE = e.FALSE_NEGATIVE_VALUE,
b.PRECISION = e.PRECISION,
b.PRECISION_UNITS = e.PRECISION_UNITS,
b.PREC_ACC_CONC_USED = e.PREC_ACC_CONC_USED,
b.INSERT_DATE = e.INSERT_DATE,
b.INSERT_PERSON_NAME = e.INSERT_PERSON_NAME,
b.LAST_UPDATE_DATE = e.LAST_UPDATE_DATE,
b.LAST_UPDATE_PERSON_NAME = e.LAST_UPDATE_PERSON_NAME,
b.GREEN_FLAG = e.GREEN_FLAG,
b.YELLOW_FLAG = e.YELLOW_FLAG,
b.CONFIRMATORY = e.CONFIRMATORY
WHEN NOT MATCHED THEN
  INSERT (b.DATE_LOADED,
b.ANALYTE_METHOD_ID,
b.METHOD_ID,
b.ANALYTE_ID,
b.DL_VALUE,
b.DL_UNITS,
b.ACCURACY,
b.ACCURACY_UNITS,
b.FALSE_POSITIVE_VALUE,
b.FALSE_NEGATIVE_VALUE,
b.PRECISION,
b.PRECISION_UNITS,
b.PREC_ACC_CONC_USED,
b.INSERT_DATE,
b.INSERT_PERSON_NAME,
b.LAST_UPDATE_DATE,
b.LAST_UPDATE_PERSON_NAME,
b.GREEN_FLAG,
b.YELLOW_FLAG,
b.CONFIRMATORY)
values (sysdate,
e.ANALYTE_METHOD_ID,
e.METHOD_ID,
e.ANALYTE_ID,
e.DL_VALUE,
e.DL_UNITS,
e.ACCURACY,
e.ACCURACY_UNITS,
e.FALSE_POSITIVE_VALUE,
e.FALSE_NEGATIVE_VALUE,
e.PRECISION,
e.PRECISION_UNITS,
e.PREC_ACC_CONC_USED,
e.INSERT_DATE,
e.INSERT_PERSON_NAME,
e.LAST_UPDATE_DATE,
e.LAST_UPDATE_PERSON_NAME,
e.GREEN_FLAG,
e.YELLOW_FLAG,
e.CONFIRMATORY);
commit;
  execute immediate 'ALTER TRIGGER CG$AIS_ANALYTE_METHOD_JN ENABLE';
  execute immediate 'ALTER TRIGGER CG$AUS_ANALYTE_METHOD_JN ENABLE';
end;

PROCEDURE MergeRevisions IS
  BEGIN
    execute immediate 'ALTER TRIGGER CG$AIS_REVISION_JOIN DISABLE';
  execute immediate 'ALTER TRIGGER CG$AUS_REVISION_JOIN DISABLE';
    execute immediate 'DROP INDEX method_pdf_ctx_idx';
    MERGE INTO revision_join B
USING (
  SELECT *
  FROM revision_join_stg amj where exists(select 1 from method_stg m where m.method_id = amj.method_id and approved = 'Y' ) AND METHOD_ID IN ('11355','11356','11353','11358','9928','9926','11362','9931','9927','9932','11351','9929','9930','9933','11352','11365')) E
ON (B.revision_id = E.revision_id)
WHEN MATCHED THEN
  UPDATE SET
b.METHOD_ID = e.METHOD_ID,
b.REVISION_INFORMATION = e.REVISION_INFORMATION,
b.METHOD_PDF = e.METHOD_PDF,
b.INSERT_DATE = e.INSERT_DATE,
b.INSERT_PERSON_NAME = e.INSERT_PERSON_NAME,
b.LAST_UPDATE_DATE = e.LAST_UPDATE_DATE,
b.LAST_UPDATE_PERSON_NAME = e.LAST_UPDATE_PERSON_NAME,
b.MIMETYPE = e.MIMETYPE,
b.PDF_INSERT_PERSON = e.PDF_INSERT_PERSON,
b.PDF_INSERT_DATE = e.PDF_INSERT_DATE,
b.REVISION_FLAG = e.REVISION_FLAG,
b.DATE_LOADED = sysdate
WHEN NOT MATCHED THEN
  INSERT (b.REVISION_ID,
b.METHOD_ID,
b.REVISION_INFORMATION,
b.METHOD_PDF,
b.INSERT_DATE,
b.INSERT_PERSON_NAME,
b.LAST_UPDATE_DATE,
b.LAST_UPDATE_PERSON_NAME,
b.MIMETYPE,
b.PDF_INSERT_PERSON,
b.PDF_INSERT_DATE,
b.REVISION_FLAG,
b.DATE_LOADED)
values (e.REVISION_ID,
e.METHOD_ID,
e.REVISION_INFORMATION,
e.METHOD_PDF,
e.INSERT_DATE,
e.INSERT_PERSON_NAME,
e.LAST_UPDATE_DATE,
e.LAST_UPDATE_PERSON_NAME,
e.MIMETYPE,
e.PDF_INSERT_PERSON,
e.PDF_INSERT_DATE,
e.REVISION_FLAG,
sysdate);
COMMIT;
    execute immediate 'ALTER TRIGGER CG$AIS_REVISION_JOIN ENABLE';
  execute immediate 'ALTER TRIGGER CG$AUS_REVISION_JOIN ENABLE';
execute immediate 'CREATE INDEX method_pdf_ctx_idx ON revision_join(method_pdf) INDEXTYPE IS ctxsys.context
  PARAMETERS(''DATASTORE multi_method_pdf LEXER mylex filter ctxsys.auto_filter WORDLIST STEM_FUZZY_PREF'')';
    end;

PROCEDURE ReloadMethodFact IS
  BEGIN
  execute immediate 'TRUNCATE TABLE method_fact DROP STORAGE';
  insert into method_fact
SELECT
j.dl_units,
j.dl_value,
j.analyte_id,
j.accuracy,
j.accuracy_units,
j.PRECISION,
j.precision_units,
j.prec_acc_conc_used,
j.false_positive_value,
j.false_negative_value,
m_vw.instrumentation_description,
j.analyte_code,
j.analyte_name,
m_vw.method_id,
m_vw.source_method_identifier,
       m_vw.method_descriptive_name,
       m_vw.method_official_name,
       m_vw.method_source_id,
       m_vw.source_citation_id,
       m_vw.brief_method_summary,
       m_vw.scope_and_application,
       m_vw.media_name,
       m_vw.dl_type_id,
       m_vw.cbr_only,
       m_vw.method_source,
       m_vw.method_source_name,
       m_vw.precision_descriptor_notes,
       m_vw.method_category,
       m_vw.method_subcategory,
       m_vw.dl_type_description,
       m_vw.source_citation_name,
       m_vw.relative_cost_symbol,
       m_vw.relative_cost,
       rj.revision_information,
       rj.revision_id,
       rj.revision_flag,
       m_vw.regs_only,
       m_vw.method_type_desc,
       sysdate date_loaded,
       rj.MIMETYPE,
       m_vw.LINK_TO_FULL_METHOD,
       m_vw.LEVEL_OF_TRAINING,
       m_vw.MEDIA_SUBCATEGORY ,
       m_vw.MEDIA_EMPHASIZED_NOTE,
       m_vw.SAM_COMPLEXITY
  FROM method_vw m_vw,
       method_analyte_all_vw j,
       revision_join rj
 WHERE j.method_id(+) = m_vw.method_id
   AND m_vw.cbr_only = 'N'
   and m_vw.regs_only = 'N'
   AND m_vw.method_id = rj.method_id(+)
    and rj.revision_information is not null;
  commit;
    END;

 PROCEDURE RebuildIndexes IS
 BEGIN
 execute immediate 'drop INDEX method_ctx_index';
execute immediate 'CREATE INDEX method_ctx_index ON method_fact(source_method_identifier) INDEXTYPE IS ctxsys.context
  PARAMETERS(''DATASTORE multi_method_a LEXER mylex filter ctxsys.auto_filter WORDLIST STEM_FUZZY_PREF'')';

 execute immediate 'DROP INDEX method_pdf_ctx_idx';
 execute immediate 'CREATE INDEX method_pdf_ctx_idx ON revision_join(method_pdf) INDEXTYPE IS ctxsys.context
  PARAMETERS(''DATASTORE multi_method_pdf LEXER mylex filter ctxsys.auto_filter WORDLIST STEM_FUZZY_PREF'')';

execute immediate 'DROP INDEX IDX_METHOD_FACT';
execute immediate 'CREATE BITMAP INDEX IDX_METHOD_FACT ON METHOD_FACT
(SOURCE_METHOD_IDENTIFIER, ANALYTE_NAME, REVISION_INFORMATION)
LOGGING
NOPARALLEL';

execute immediate 'dROP INDEX IDX_METHOD_FACT_MEDIA';

execute immediate 'CREATE BITMAP INDEX IDX_METHOD_FACT_MEDIA ON METHOD_FACT
(MEDIA_NAME)
LOGGING
NOPARALLEL';

execute immediate 'drop INDEX IDX_METHOD_FACT_INSTRU';

execute immediate 'CREATE BITMAP INDEX IDX_METHOD_FACT_INSTRU ON METHOD_FACT
(INSTRUMENTATION_DESCRIPTION)
LOGGING
NOPARALLEL';

execute immediate 'drop INDEX IDX_METHOD_FACT_SOURCE';
execute immediate 'CREATE BITMAP INDEX IDX_METHOD_FACT_SOURCE ON METHOD_FACT
(METHOD_SOURCE)
LOGGING
NOPARALLEL';

execute immediate 'DROP INDEX IDX_METHOD_FACT_SUBCAT';
execute immediate 'CREATE BITMAP INDEX IDX_METHOD_FACT_SUBCAT ON METHOD_FACT
(METHOD_SUBCATEGORY)
LOGGING
NOPARALLEL';
SYS.DBMS_STATS.GATHER_TABLE_STATS (
      OwnName        => 'NEMI_DATA'
     ,TabName        => 'METHOD_FACT'
    ,Estimate_Percent  => 0
    ,Degree            => 4
    ,Cascade           => TRUE
    ,No_Invalidate     => FALSE);
END;

END MERGE_STG_TO_PROD;
/
