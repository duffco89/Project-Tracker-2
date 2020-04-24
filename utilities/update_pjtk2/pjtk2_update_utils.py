"""=============================================================
~/pjtk2/utils/update_pjtk2/pjtk2_update_utils.py
 Created: 13 Mar 2020 10:49:34

 DESCRIPTION:

Utilities to get objects out of a Project Tracker database with unique
identifiers so they can be moved from one version of Project tracker
to the next.

 A. Cottrill
=============================================================

"""


import psycopg2


def run_select_sql(sql, pgpars):
    """connect to our postgres database, run the query and return the
    results

    """

    pg_constring = (
        "host='{HOST}' dbname='{DBNAME}' user='{USER}'" + " password='{PASSWORD}'"
    )
    pg_constring = pg_constring.format(**pgpars)

    pgconn = psycopg2.connect(pg_constring)
    pgcur = pgconn.cursor()
    pgcur.execute(sql)
    rs = pgcur.fetchall()
    colnames = [x[0].lower() for x in pgcur.description]

    data = []
    for record in rs:
        item_dict = {k: v for k, v in zip(colnames, record)}
        data.append(item_dict)

    pgcur.close()
    pgconn.close()

    return data


def get_users(pgpars):
    """
    """

    sql = """SELECT username,
               first_name,
               last_name,
               email,
               date_joined,
               last_login,
               is_superuser,
               is_staff,
               is_active
        FROM auth_user;
        """

    return run_select_sql(sql, pgpars)


def get_employees(pgpars):
    """
    """

    sql = """SELECT boss.username AS supervisor,
    myuser.username AS employee,
           employee.position,
           employee.role
    FROM pjtk2_employee AS employee
      Left JOIN auth_user AS myuser ON myuser.id = employee.user_id
      left JOIN pjtk2_employee AS supervisor ON employee.supervisor_id = supervisor.id
      left JOIN auth_user AS boss ON boss.id = supervisor.user_id
      order by boss.username, myuser.username;
    """

    return run_select_sql(sql, pgpars)


def get_milestones(pgpars):
    """
    """

    sql = """SELECT  label, label_abbrev, category, report, protected,
    pjtk2_milestone.order, shared
    FROM pjtk2_milestone;
    """

    return run_select_sql(sql, pgpars)


def get_databases(pgpars):
    """
    """

    sql = "SELECT * FROM pjtk2_database;"

    return run_select_sql(sql, pgpars)


def get_projects(pgpars):
    """
    """

    sql = """SELECT prj_cd,
               active,
               year,
               prj_date0,
               prj_date1,
               prj_nm,
        			 COMMENT,
               risk,
               prj_ldr.username AS prj_ldr,
               field_ldr.username AS field_ldr,
               cancelled_by.username AS cancelled_by,
               --projtype.project_type AS project_type,
               proj_owner.username AS owner,
               dba.username AS dba,
               lake.lake AS lake,
               db.master_database as database,
               slug,
               cancelled
        FROM pjtk2_project AS project
          JOIN auth_user AS prj_ldr ON prj_ldr.id = project.prj_ldr_id
          LEFT JOIN auth_user AS field_ldr ON field_ldr.id = project.field_ldr_id
          LEFT JOIN auth_user AS cancelled_by ON cancelled_by.id = project.cancelled_by_id
          LEFT JOIN auth_user AS proj_owner ON proj_owner.id = project.owner_id
          LEFT JOIN auth_user AS dba ON dba.id = project.dba_id
          LEFT JOIN pjtk2_lake AS lake ON lake.id = project.lake_id
          LEFT JOIN pjtk2_database AS db ON db.id = project.master_database_id
          LEFT JOIN pjtk2_projecttype AS projtype ON projtype.id = project.project_type_id;
        """

    return run_select_sql(sql, pgpars)


def get_funding_sources(pgpars):
    """
    """

    sql = "select distinct funding from pjtk2_project;"

    return run_select_sql(sql, pgpars)


def get_project_funding(pgpars):
    """
    """

    sql = """SELECT prj_cd,
       funding,
       odoe,
       salary
    FROM pjtk2_project;
    """

    return run_select_sql(sql, pgpars)


def get_project_tags(pgpars):
    """
    """

    sql = """SELECT prj_cd,
       tag.name
        FROM taggit_tag AS tag
          JOIN taggit_taggeditem AS taggeditem ON taggeditem.tag_id = tag.id
          JOIN pjtk2_project AS project ON project.id = taggeditem.object_id
        WHERE taggeditem.content_type_id = (SELECT id
                                            FROM django_content_type
                                            WHERE app_label = 'pjtk2'
                                            AND   model = 'project');
    """

    return run_select_sql(sql, pgpars)


def get_project_sample_points(pgpars):
    """
    """

    sql = """-- SAMPLE POINTS
    SELECT prj_cd,
       sam,
       st_astext(geom)
    FROM pjtk2_samplepoint AS pt
    JOIN pjtk2_project AS project ON project.id = pt.project_id;
    """

    return run_select_sql(sql, pgpars)


def get_project_milestones(pgpars):
    """
    """

    sql = """SELECT prj_cd,
               ms.label_abbrev,
               required,
               completed
        FROM pjtk2_projectmilestones AS pjms
          JOIN pjtk2_project AS project ON project.id = pjms.project_id
          JOIN pjtk2_milestone AS ms ON ms.id = pjms.milestone_id
        ORDER BY prj_cd,
         ms.order"""

    return run_select_sql(sql, pgpars)


def get_reports_and_milestones(pgpars):
    """
    """

    sql = """
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
        """

    return run_select_sql(sql, pgpars)


def get_associated_files(pgpars):
    """
    """

    sql = """SELECT prj_cd,
               file_path,
               CURRENT,
               uploaded_on,
               hash,
               myuser.username AS uploaded_by
        FROM pjtk2_associatedfile AS associatedfile
          JOIN pjtk2_project AS project ON project.id = associatedfile.project_id
          JOIN auth_user AS myuser ON myuser.id = associatedfile.uploaded_by_id;
        """

    return run_select_sql(sql, pgpars)


def get_bookmarks(pgpars):
    """
    """

    sql = """SELECT project.prj_cd,
               myuser.username,
               bookmark.date
        FROM pjtk2_bookmark AS bookmark
          JOIN auth_user AS myuser ON myuser.id = bookmark.user_id
          JOIN pjtk2_project AS project ON project.id = bookmark.project_id;
        """

    return run_select_sql(sql, pgpars)


def get_sisters(pgpars):
    """
    """

    sql = """SELECT prj_cd,
               family_id
        FROM pjtk2_projectsisters AS sisters
          JOIN pjtk2_project AS project ON project.id = sisters.project_id
    where family_id is not null
        ORDER BY family_id,
                 prj_cd;
        """

    return run_select_sql(sql, pgpars)


def get_messages(pgpars):
    """
    """

    sql = """-- MESSAGES
        SELECT message.id as msg_id, prj_cd,
               ms.label_abbrev,
               msgtxt,
               level
        FROM pjtk2_message AS message
          JOIN pjtk2_projectmilestones AS projectmilestones ON projectmilestones.id = message.project_milestone_id
          JOIN pjtk2_project AS project ON project.id = projectmilestones.project_id
          JOIN pjtk2_milestone AS ms ON ms.id = projectmilestones.milestone_id
        ORDER BY prj_cd,
                 ms.order;
        """

    return run_select_sql(sql, pgpars)


def get_messages2users(msg_id, pgpars):
    """
    """

    sql = """SELECT prj_cd,
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
          where message.id={}
        ORDER BY prj_cd,
                 ms.order,
                 myuser.username;
        """

    return run_select_sql(sql.format(msg_id), pgpars)
