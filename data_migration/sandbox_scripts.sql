SELECT *
FROM pjtk2_employee;

SELECT *
FROM pjtk2_milestone;

SELECT *
FROM auth_user;

INSERT INTO pjtk2_employee
(
  user_id,
  POSITION,
  role,
  supervisor_id
)
VALUES
(
  23,
  'TBD',
  3,
  NULL
);

INSERT INTO pjtk2_employee
(
  user_id,
  POSITION,
  role,
  supervisor_id
)
VALUES
(
  1,
  'TBD',
  3,
  63
);

INSERT INTO pjtk2_employee
(
  user_id,
  POSITION,
  role,
  supervisor_id
)
VALUES
(
  8,
  'TBD',
  3,
  63
);

COMMIT;

SELECT e.id
FROM pjtk2_employee AS e
  JOIN auth_user AS u ON u.id = e.user_id
WHERE u.username = 'mcleishda';

INSERT INTO pjtk2_lake
(
  lake
)
VALUES
(
  'foobar'
);

UPDATE pjtk2_employee
   SET supervisor_id = 82
WHERE supervisor_id = 80;

COMMIT;

SELECT *
FROM pjtk2_project
WHERE year::int4 = 2012;

UPDATE pjtk2_project
   SET slug = 'lha_ia03_spa'
WHERE prj_cd = 'LHA_IA03_SPA';

COMMIT;

-- an example query selecting proejct based on milestones
SELECT *
FROM pjtk2_projectmilestones AS pms,
     pjtk2_project AS p,
     pjtk2_milestone AS ms
WHERE p.id = pms.project_id
AND   ms.id = pms.milestone_id
AND   ms.label = 'Sign off'
AND   p.year::int4> 2010 LIMIT 40;

-- update old projects by default - we'll assume that they are done.
UPDATE pjtk2_projectmilestones pms
   SET completed = NOW()
FROM pjtk2_project AS p,
     pjtk2_milestone AS ms
WHERE p.id = pms.project_id
AND   ms.id = pms.milestone_id
AND   p.year::int4< 2010
AND   ms.label IN ('Approved','Aging Complete','Sign off','Data Scrubbed','Data Merged')
AND   completed IS NULL;

COMMIT;

-- if a new project has a completion report, we will assume that the field work, aging, 
-- and data scrubbing must also be done;
UPDATE pjtk2_projectmilestones pms
   SET completed = NOW()
FROM pjtk2_project AS p,
     pjtk2_milestone AS ms
WHERE p.id = pms.project_id
AND   ms.id = pms.milestone_id
AND   completed IS NULL
AND   ms.label IN ('Approved','Aging Complete','Field Work Conducted','Data Scrubbed','Data Merged')
AND   pms.project_id IN (
-- get all of project ID that have a project completion report:
SELECT pms.project_id
FROM pjtk2_projectmilestones AS pms,
     pjtk2_project AS p,
     pjtk2_milestone AS ms
WHERE p.id = pms.project_id
AND   ms.id = pms.milestone_id
AND   ms.label = 'Project Completion Report'
AND   pms.completed IS NOT NULL);

COMMIT;

-- get project codes that have appear in spatial data but do not appear in project master list
-- these are projects that have obviously been run, but not reported on:
SELECT *
FROM pjtk2_samplepoint LIMIT 10;

SELECT DISTINCT prj_cd
FROM spatial_tmp LIMIT 7;

SELECT *
FROM pjtk2_projectmilestones LIMIT 3;

SELECT *
FROM pjtk2_milestone
WHERE report = TRUE;

-- projects with some form of 'completion' report but without any data in our master datasets:
-- where is the data?
SELECT DISTINCT p.year,
       p.prj_cd,
       p.prj_nm,
       u.first_name || ' ' || u.last_name AS project_lead,
       p.field_project
FROM pjtk2_project p
  JOIN auth_user AS u ON u.id = p.prj_ldr_id
  JOIN pjtk2_projectmilestones pms ON p.id = pms.project_id
  JOIN pjtk2_milestone ms ON ms.id = pms.milestone_id
WHERE ms.label IN ('Summary Report','Project Completion Report','Project Completion Pres.')
AND   pms.completed IS NOT NULL
AND   p.prj_cd NOT IN (
-- projects with spatial data
SELECT DISTINCT prj_cd FROM spatial_tmp)
ORDER BY year DESC;

-- projects with spatial data missing from project tracker:
SELECT DISTINCT sp.dbase,
       sp.prj_cd
FROM spatial_tmp sp
WHERE sp.prj_cd NOT IN (SELECT DISTINCT p.prj_cd FROM pjtk2_project p)
ORDER BY dbase,
         prj_cd;

COMMIT;

SELECT u.*,
       first_name || ' ' || last_name AS project_lead
FROM auth_user u LIMIT 10;

SELECT *
FROM pjtk2_project LIMIT 5;

UPDATE pjtk2_projectmilestones pms2
   SET completed = NOW()
WHERE pms2.id IN (SELECT pms.id
                  FROM pjtk2_projectmilestones pms
                    JOIN pjtk2_project p ON pms.project_id = p.id
                    JOIN pjtk2_milestone ms ON ms.id = pms.milestone_id
                    JOIN spatial_tmp AS sp ON sp.prj_cd = p.prj_cd
                  WHERE pms.completed IS NULL
                  AND   p.year::INT4< 2012
                  AND   ms.report = FALSE);

COMMIT;

-- we don't want to sign off on recent projects though - rest the signoff project milestone for those projects;
UPDATE pjtk2_projectmilestones pms2
   SET completed = NULL
WHERE pms2.id IN (SELECT DISTINCT pms.id
                  FROM pjtk2_projectmilestones pms
                    JOIN pjtk2_project p ON pms.project_id = p.id
                    JOIN pjtk2_milestone ms ON ms.id = pms.milestone_id
                    JOIN spatial_tmp AS sp ON sp.prj_cd = p.prj_cd
                  WHERE pms.completed IS NOT NULL
                  AND   p.year::INT4>= 2012
                  AND   ms.label = 'Sign off');

COMMIT;

SELECT *
FROM pjtk2_milestone;

-- clips applied to lake trout in past 18 years (or so).
SELECT DISTINCT spawn_year,
       spawn_year +1 AS yc,
       clipa
FROM fsis2_event event
  JOIN fsis2_lot lot ON event.lot_id = lot.id
  JOIN fsis2_species spc ON spc.id = lot.species_id
WHERE species_code = 81
AND   spawn_year >= 1995
AND   clipa NOT IN ('0','5')
ORDER BY yc;

-- calculate catch, effort, cpue per 24-hour, cpue per km, and cpue-per-km-per-24hr
SELECT year,
       quota_zone,
       grtp,
       effdst5,
       effdur9,
       effduru,
       (effdst5*0.9144 / 1000) AS effort_km,
       catch_kg,
       CASE
         WHEN effduru = 'D' THEN catch_kg / effdur9
         ELSE catch_kg /(effdur9 / 24)
       END AS cpe_24hr,
       catch_kg /(effdst5*0.9144 / 1000) AS cpe_km,
       CASE
         WHEN effduru = 'D' THEN catch_kg /(effdst5*0.9144 / 1000) /(effdur9)
         ELSE catch_kg /(effdst5*0.9144 / 1000) /(effdur9 / 24)
       END AS cpe_km_24hr
FROM ch132
  JOIN location_with_latlong AS lwll ON lwll.grid = ch132.grid
  JOIN (SELECT id132,
               SUM(hvswta) AS catch_kg
        FROM ch133
        GROUP BY id132,
                 spc
        HAVING spc = '091') AS catch_kg ON ch132.id132 = catch_kg.id132
WHERE quota_zone = 'Zone1'
AND   ch132.effdst5 IS NOT NULL
AND   ch132.effdst5 > 0
AND   ch132.effdur9 IS NOT NULL
AND   ch132.effdur9 > 0
AND   spctrg = '091'
ORDER BY year;

-- mean net length over time:
SELECT quota_zone,
       year,
       AVG((effdst5*0.9144) / 1000) AS AvgEffort_km
FROM ch132
  JOIN location_with_latlong AS lwll ON lwll.grid = ch132.grid
WHERE effdst5 IS NOT NULL
AND   effdst5 > 0
AND   grtp = 'GL'
AND   spctrg = '091'
GROUP BY year,
         quota_zone
ORDER BY quota_zone,
         year;

-- mean effort duration over time:
-- calculate effort duration in hours:
SELECT year,
       quota_zone,
       AVG(effdurD)
FROM (SELECT YEAR,
             quota_zone,
             effdur9,
             effduru,
             CASE
               WHEN effduru = 'D' THEN effdur9
               ELSE effdur9 / 24
             END AS effdurD
      FROM ch132
        JOIN location_with_latlong AS lwll ON lwll.grid = ch132.grid) AS effDays
WHERE quota_zone = '4-5'
GROUP BY year,
         quota_zone
ORDER BY quota_zone,
         year LIMIT 35;

SELECT year,
       prj_cd,
       chsam,
       eff,
       quota_zone,
       grtp,
       effdst5,
       effdur9,
       effduru,
       (effdst5*0.9144 / 1000) AS effort_km,
       CASE
         WHEN effduru = 'D' THEN effdur9
         ELSE effdur9 / 24
       END AS effdurD,
       catch_kg
FROM ch132
  JOIN location_with_latlong AS lwll ON lwll.grid = ch132.grid
  JOIN (SELECT id132,
               SUM(hvswta) AS catch_kg
        FROM ch133
        GROUP BY id132,
                 spc
        HAVING spc = '091') AS catch_kg ON ch132.id132 = catch_kg.id132
WHERE quota_zone = '4-5'
AND   grtp = 'GL'
AND   spctrg = '091'
AND   year = '2012'
ORDER BY quota_zone,
         year LIMIT 35;

SELECT ch132.*
FROM ch132
  JOIN location_with_latlong AS lwll ON lwll.grid = ch132.grid
WHERE quota_zone = 'Zone1'
-- H, X, D, NULL
-- X - look like buyers records, grid_flag should be updated to 0
AND   effdst5 = 0
AND   spctrg = '091' LIMIT 100;

SELECT id132,
       SUM(hvswta)
FROM ch133
GROUP BY id132,
         spc
HAVING spc = '091' LIMIT 10;

SELECT *
FROM information_schema.tables
WHERE table_schema = 'shapefiles';

SELECT *
FROM information_schema.tables
WHERE table_schema = 'public';

SELECT *
FROM pjtk2_samplepoint AS sam,
     shapefiles.grids AS grids
WHERE st_intersects (grids.geom,st_transform (sam.geom,26917))
AND   grids.on_grid_no IN (2043,2143) LIMIT 10;

SELECT *
FROM (SELECT *,
             st_transform(geom,26917) AS utm
      FROM pjtk2_samplepoint AS sam LIMIT 10) AS wtf
  JOIN shapefiles.grids grids ON st_intersects (grids.geom,wtf.utm);

SELECT *,
       st_astext(st_transform (geom,26917))
FROM pjtk2_samplepoint LIMIT 10;

SELECT *
FROM shapefiles.grids LIMIT 5;

SELECT *
FROM pjtk2_samplepoint LIMIT 5;

--select distinct cwt from cwts_cwt_recovery as r
SELECT *
FROM cwts_cwt_recovery AS r
  JOIN shapefiles.grids AS g ON g.on_grid_no = r.recovery_grid::int4
WHERE g.on_manarea = '5-1'
-- to merge qma
-- 
CREATE OR REPLACE VIEW shapefiles.QMAs AS
-- return polygons representing each of the qmas.  The polygons have been simplified 
--(to make the file size smaller) and then buffered twice to remove any dangling artefacts.
SELECT ROW_NUMBER() OVER (
ORDER BY on_manarea ASC) AS gid,
         on_manarea,
         st_simplify(st_buffer (st_union (st_buffer (geom,1)),-1),100) AS geom FROM shapefiles.grids AS grids WHERE on_manarea != 'NA' GROUP BY grids.on_manarea;

COMMIT;

-- cwts stocked in a specific qma and year
SELECT DISTINCT cwt,
       year,
       qma
FROM fsis2_event AS event
  JOIN fsis2_taggingevent AS tevent ON tevent.stocking_event_id = event.id
  JOIN fsis2_cwts_applied AS applied ON applied.tagging_event_id = tevent.id
  JOIN fsis2_qma AS qma ON st_intersects (qma.geom,event.geom)
WHERE event.year = '2011'
AND   qma.qma = 'Zone3'
ORDER BY cwt;

SELECT *
FROM cwts_cwt_recovery rec
WHERE rec.composite_key NOT LIKE '%-081-%'
AND   rec.composite_key NOT LIKE '%-082-%'
AND   rec.composite_key NOT LIKE '%-086-%'
AND   rec.composite_key NOT LIKE '%-087-%';

SELECT *
FROM fsis2_taggingevent LIMIT 2;

SELECT *
FROM fsis2_cwts_applied LIMIT 2;

-- cwts that have been recovered but do not appear in cwt master or cwts_applied.
SELECT *
FROM cwts_cwt_recovery
WHERE cwt NOT IN (SELECT DISTINCT cwt
                  FROM cwts_cwt
                  UNION
                  SELECT DISTINCT cwt
                  FROM fsis2_cwts_applied)
ORDER BY recovery_year DESC;

SELECT *
FROM cwts_cwt_recovery
WHERE cwt !~ '(05|43|59|60|63|64)\d{4}'
ORDER BY recovery_year DESC;

DELETE
FROM cwts_cwt_recovery
WHERE cwt !~ '\d{6}';

COMMIT;

SELECT *
FROM cwts_cwt LIMIT 1;

SELECT prj_cd,
       prj_nm,
       COMMENT
FROM pjtk2_project
WHERE COMMENT ilike '%contaminant%';

SELECT st_astext(st_transform (geom,4326)) AS grid
FROM shapefiles.grids
WHERE on_grid_no = '2826';

SELECT st_astext(st_transform (st_centroid (geom),4326)) AS grid
FROM shapefiles.grids
WHERE on_grid_no = '2826';

SELECT st_astext(randompointsinpolygon (geom,4)) AS grid
FROM shapefiles.grids
WHERE on_grid_no = '2826';

SELECT on_grid_no,
       st_astext(st_transform (st_centroid (geom),4326)) AS grid
FROM shapefiles.grids
WHERE on_grid_no IN ('2825','2827');

-- add columns for odoe and salary and remove total_cost
BEGIN;
ALTER TABLE pjtk2_project ADD COLUMN salary numeric(8,2);
ALTER TABLE pjtk2_project ADD COLUMN odoe numeric(8,2);
ALTER TABLE pjtk2_project DROP COLUMN total_cost;
COMMIT;

-- Add field component to project type:
BEGIN;
ALTER TABLE pjtk2_project DROP COLUMN field_project;
ALTER TABLE pjtk2_projecttype ADD COLUMN field_component Bool;
UPDATE pjtk2_projecttype set field_component=TRUE;
UPDATE pjtk2_projecttype
   SET field_component = FALSE
WHERE project_type IN ('Lamprey Monitoring and Reporting','CWT Recovery and Analysis','Diet Analysis','Aging QAQC','Commerical Harvest and Stock Status Reporting');
COMMIT;



--find projects with field_component=False but with lat-long data (might be project type mis-speficication)
SELECT DISTINCT project.*
FROM pjtk2_project AS project
  JOIN pjtk2_samplepoint AS pt ON pt.project_id = project.id 
join pjtk2_projecttype as pjtype on pjtype.id=project.project_type_id  
where field_component=False
LIMIT 10;


select report_path from pjtk2_report where uploaded_on > timestamp '2014-05-30';

select report_path from pjtk2_report limit 10;

select * from auth_user;

select * from pjtk2_project limit 10;

select * from pjtk2_employee;

commit;


select prj_cd, project_type, prj_nm from pjtk2_project as proj 
join pjtk2_projecttype as ptype on ptype.id=proj.project_type_id
where proj.year='2013';

select project_type, count(prj_cd) as N from pjtk2_project as proj 
join pjtk2_projecttype as ptype on ptype.id=proj.project_type_id
group by project_type, proj.year
having proj.year='2013';

select replace(prj_nm, 'Swin', 'SWIN') from pjtk2_project where prj_nm ilike '%swin%';

select replace(comment, 'Swin', 'SWIN') from pjtk2_project where comment ilike '%swin%';

UPDATE pjtk2_project set prj_nm = replace(prj_nm, 'Swin', 'SWIN') where prj_nm ilike '%swin%';
UPDATE pjtk2_project set prj_nm = replace(prj_nm, 'Fwin', 'FWIN') where prj_nm ilike '%fwin%';
UPDATE pjtk2_project set prj_nm = replace(prj_nm, 'Estn', 'ESTN') where prj_nm ilike '%estn%';

UPDATE pjtk2_project set comment = replace(comment, 'Swin', 'SWIN') where comment ilike '%swin%';
UPDATE pjtk2_project set comment = replace(comment, 'Fwin', 'FWIN') where comment ilike '%fwin%';
UPDATE pjtk2_project set comment = replace(comment, 'Estn', 'ESTN') where comment ilike '%estn%';

UPDATE pjtk2_project set prj_nm = replace(prj_nm, 'Smin', 'SMIN') where prj_nm ilike '%smin%';
UPDATE pjtk2_project set comment = replace(comment, 'Smin', 'SMIN') where comment ilike '%smin%';

UPDATE pjtk2_project set prj_nm = replace(prj_nm, 'Flin', 'FLIN') where prj_nm ilike '%flin%';
UPDATE pjtk2_project set comment = replace(comment, 'Flin', 'FLIN') where comment ilike '%flin%';


commit;


select comment from pjtk2_project where comment like '%ommerical%';

UPDATE pjtk2_project set comment = replace(comment, 'commerical', 'commercial') where comment like '%commerical%';
UPDATE pjtk2_project set prj_nm = replace(prj_nm, 'Commerical', 'Commercial') where prj_nm like '%Commerical%';


select * from pjtk2_project limit 3;


select * FROM fsis2_event AS event limit 2;
select * FROM fsis2_stockingsite as site limit 2;

SELECT *
FROM fsis2_event AS event
  JOIN fsis2_stockingsite AS site ON site.id = event.site_id
WHERE site.site_name='Black Rock';


select * from fsis2_event as event 
join fsis2_lot as lot on lot.id=event.lot_id
join fsis2_species as spc on spc.id = lot.species_id
where fish_wt > 15 and fish_wt <= 20 and spc.common_name='Walleye';

select * from fsis2_lot limit 10;
select * from fsis2_species limit 10;
