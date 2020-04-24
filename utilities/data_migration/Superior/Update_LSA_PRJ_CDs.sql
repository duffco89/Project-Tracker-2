-- sql commands to replace/update all of the 000_ prefixes on the lake superior projects with LSA_

-- append the old proejct code onto the existing comment so that we don't loose them:
update pjtk2_project set comment =  comment || '

Original Project code:' || prj_cd where prj_cd ~ '^[0-9]{3}';

commit;

-- there is one duplicate project (or there willbe if we replce all of the numbers with names.)
select * from pjtk2_project where prj_cd ilike '%DD97_LSM';
-- append the project code to the comment of the other
update pjtk2_project set comment =  comment || '
and 099_DD97_LSM' where prj_cd= '006_DD97_LSM';
-- and then delete the one we're not keeping
delete from pjtk2_project where prj_cd = '099_DD97_LSM';

-- if the project code starts with three digits, replace them with LSA
update pjtk2_project set prj_cd = 'LSA' || substr(prj_cd, 4) where prj_cd ~ '^[0-9]{3}';
-- don't forget to update our slugs:
update pjtk2_project set slug = lower(prj_cd);


commit;




select 'LSA' || substr(prj_cd, 4) from pjtk2_project limit 10;

select substr(prj_cd, 4) from pjtk2_project group by substr(prj_cd, 0,4) limit 20;

select prj_cd from pjtk2_project where prj_cd ~ '^[0-9]{3}' limit 10;

select regexp_matches('^\d{3}', prj_cd) from pjtk2_project limit 10;
