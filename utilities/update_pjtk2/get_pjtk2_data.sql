--- exporting and merging data from project tracker 
-- rows in tables will be exported with id's replaced by unique labels of foreign key objects so we can 'get or create them'
-- queries will be run on both lake Huron and Lake Superior databases so they can be merged into a single entity.
-- USERS   
SELECT username,
       first_name,
       last_name,
       email,
       date_joined,       
       last_login,
       is_superuser,
       is_staff,
       is_active
FROM auth_user;



-- EMPLOYESS
-- note - this table should have two time stampt fields - activate and deactivated
select count(*) from pjtk2_employee;

SELECT boss.username AS supervisor,
myuser.username AS employee,
       employee.position,
       employee.role
FROM pjtk2_employee AS employee
  Left JOIN auth_user AS myuser ON myuser.id = employee.user_id
  left JOIN pjtk2_employee AS supervisor ON employee.supervisor_id = supervisor.id
  left JOIN auth_user AS boss ON boss.id = supervisor.user_id
  order by boss.username, myuser.username;
  

-- LAKE (this is now obsolete)
SELECT *
FROM pjtk2_lake;

-- MILESTONES
SELECT  label, label_abbrev, category, report, protected, pjtk2_milestone.order, shared
FROM pjtk2_milestone;

--update pjtk2_milestone set label_abbrev='Submitted' where label='Submitted';
--commit;


-- PROJECT TYPES
SELECT *
FROM pjtk2_projecttype;

-- PROJECT Protocols  NOT IMPLEMENTED YET
--select * from pjtk2_milestone;
-- PROJECT TYPES
SELECT *
FROM pjtk2_database;x

-- distinct funding sources:
select * from pjtk2_project limit 10;
select distinct funding from pjtk2_project;


-- PROJECTS
select * from pjtk2_project limit 4;

SELECT prj_cd,
       active,
       year,
       prj_date0,
       prj_date1,
       prj_nm,       
			 COMMENT,
       risk,
       prj_ldr.username AS prj_ldr,
       fld_ldr.username AS fld_ldr,
       cancelled_by.username AS cancelled_by,
       projtype.project_type AS project_type,
       proj_owner.username AS owner,
       dba.username AS dba,
       lake.lake AS lake,
       db.master_database as database,	     
       slug,
       cancelled
FROM pjtk2_project AS project
  JOIN auth_user AS prj_ldr ON prj_ldr.id = project.prj_ldr_id
  LEFT JOIN auth_user AS fld_ldr ON fld_ldr.id = project.field_ldr_id
  LEFT JOIN auth_user AS cancelled_by ON cancelled_by.id = project.cancelled_by_id
  LEFT JOIN auth_user AS proj_owner ON proj_owner.id = project.owner_id
  LEFT JOIN auth_user AS dba ON dba.id = project.dba_id
  LEFT JOIN pjtk2_lake AS lake ON lake.id = project.lake_id
  LEFT JOIN pjtk2_database AS db ON db.id = project.master_database_id
  LEFT JOIN pjtk2_projecttype AS projtype ON projtype.id = project.project_type_id;

-- PROJECT FIELD STAFF
-- project key words
-- select * from taggit_tag limit 10;
-- select * from taggit_taggeditem limit 10;
-- select id from django_content_type where app_label='pjtk2' and model='project';
SELECT prj_cd,
       tag.name
FROM taggit_tag AS tag
  JOIN taggit_taggeditem AS taggeditem ON taggeditem.tag_id = tag.id
  JOIN pjtk2_project AS project ON project.id = taggeditem.object_id
WHERE taggeditem.content_type_id = (SELECT id
                                    FROM django_content_type
                                    WHERE app_label = 'pjtk2'
                                    AND   model = 'project');

-- FUNDING SOURCES - does not actuall exist in current application
--select * from pjtk2_fundingsource;
SELECT prj_cd,
       funding,
       odoe,
       salary
FROM pjtk2_project;

-- SAMPLE POINTS
-- update with annual report work arrounds
SELECT prj_cd,
       sam,
       st_astext(geom)
FROM pjtk2_samplepoint AS pt
  JOIN pjtk2_project AS project ON project.id = pt.project_id LIMIT 10;

-- Project Images
-- get project images from from Annual Report directory
-- PROJECT MILESTONES
--select * from pjtk2_projectmilestones;
SELECT prj_cd,
       ms.label_abbrev,
       required,
       completed
FROM pjtk2_projectmilestones AS pjms
  JOIN pjtk2_project AS project ON project.id = pjms.project_id
  JOIN pjtk2_milestone AS ms ON ms.id = pjms.milestone_id
ORDER BY prj_cd,
         ms.order
-- REPORTS
-- check for orphan reports
-- check for reports that been replaced by newer versions
SELECT *FROM pjtk2_report LIMIT 10;



-- report2Milestones
-- these are the distinct reports, their projects and their associated milestone
SELECT DISTINCT prj_cd,
       ms.order AS milestone_order,
       label_abbrev,
       CURRENT,
       report_path,
       REPLACE(report_path,'milestone_reports','milestone_reports/' || prj_cd) AS report_path_shouldbe,
       uploaded_on,
       myuser.username AS uploaded_by,
       report_hash
FROM pjtk2_report_projectreport AS msreport
  JOIN pjtk2_projectmilestones AS projectmilestones ON projectmilestones.id = msreport.projectmilestones_id
  JOIN pjtk2_project AS project ON project.id = projectmilestones.project_id
  JOIN pjtk2_milestone AS ms ON ms.id = projectmilestones.milestone_id
  JOIN pjtk2_report AS report ON report.id = msreport.report_id
  JOIN auth_user AS myuser ON myuser.id = report.uploaded_by_id
ORDER BY prj_cd,
         ms.order;

-- Associated files
SELECT prj_cd,
       file_path,
       CURRENT,
       uploaded_on,
       hash,
       myuser.username AS uploaded_by
FROM pjtk2_associatedfile AS associatedfile
  JOIN pjtk2_project AS project ON project.id = associatedfile.project_id
  JOIN auth_user AS myuser ON myuser.id = associatedfile.uploaded_by_id;



--  BOOKMARKS
SELECT project.prj_cd,
       myuser.username,
       bookmark.date
FROM pjtk2_bookmark AS bookmark
  JOIN auth_user AS myuser ON myuser.id = bookmark.user_id
  JOIN pjtk2_project AS project ON project.id = bookmark.project_id;

-- PROJECT SISTERS
-- create get or create each family id
SELECT prj_cd,
       family_id
FROM pjtk2_projectsisters AS sisters
  JOIN pjtk2_project AS project ON project.id = sisters.project_id
ORDER BY family_id,
         prj_cd;

commit;
-- MESSAGESx
SELECT prj_cd,
       ms.label_abbrev,
       msgtxt,
       level
FROM pjtk2_message AS message
  JOIN pjtk2_projectmilestones AS projectmilestones ON projectmilestones.id = message.project_milestone_id
  JOIN pjtk2_project AS project ON project.id = projectmilestones.project_id
  JOIN pjtk2_milestone AS ms ON ms.id = projectmilestones.milestone_id
ORDER BY prj_cd,
         ms.order;

-- MESSAGES2USER
SELECT prj_cd,
       ms.label_abbrev,
       myuser.username,
       msgtxt,
       level,
       created,
       read
FROM pjtk2_messages2users AS message2user
  JOIN pjtk2_message AS message ON message.id = message2user.message_id
  JOIN pjtk2_projectmilestones AS projectmilestones ON projectmilestones.id = message.project_milestone_id
  JOIN pjtk2_project AS project ON project.id = projectmilestones.project_id
  JOIN pjtk2_milestone AS ms ON ms.id = projectmilestones.milestone_id
  JOIN auth_user AS myuser ON myuser.id = message2user.user_id
ORDER BY prj_cd,
         ms.order,
         myuser.username;



select * from pjtk2_project where year='2019';

-- project types that are still null
select substr(prj_cd,5,2) as prj_type, count(id) as N from pjtk2_project 
group by substr(prj_cd,5,2), project_type_id
having project_type_id is null
order by count(id) desc;


SELECT year, substr(prj_cd, 5,2) as prj_type,
       prj_cd,
       prj_nm
FROM pjtk2_project
WHERE protocol_id IS NULL
order by prj_type, year


SELECT prj_cd,
       prj_nm,
       abbrev
FROM pjtk2_project project
  JOIN pjtk2_projectprotocol AS protocol ON protocol.id = project.protocol_id
where abbrev='SF'
and prj_nm ilike '%volunteer%'



-- database size in this cluster
-- from: https://wiki.postgresql.org/wiki/Disk_Usage
SELECT d.datname AS Name,  pg_catalog.pg_get_userbyid(d.datdba) AS Owner,
    CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT')
        THEN pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname))
        ELSE 'No Access'
    END AS SIZE
FROM pg_catalog.pg_database d
    ORDER BY
    CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT')
        THEN pg_catalog.pg_database_size(d.datname)
        ELSE NULL
    END DESC -- nulls firstx
    LIMIT 20


SELECT nspname || '.' || relname AS "relation",
    pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
  FROM pg_class C
  LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
  WHERE nspname NOT IN ('pg_catalog', 'information_schema')
    AND C.relkind <> 'i'
    AND nspname !~ '^pg_toast'
  ORDER BY pg_total_relation_size(C.oid) DESC
  LIMIT 20;

select * from fn121('LHA_IA09_005');

select * from pjtk2_projecttype;

SELECT project_type,
       protocol,
       abbrev
FROM pjtk2_projectprotocol AS protocol
  right JOIN pjtk2_projecttype AS project_type ON project_type.id = protocol.project_type_id
  order by project_type, protocol;


--update pjtk2_projectprotocol set abbrev = 'UTA' where abbrev='UTS'
commit;


SELECT prj_cd, image_path as shouldbe
FROM pjtk2_projectimage AS img
  JOIN pjtk2_project project ON project.id = img.project_id;


