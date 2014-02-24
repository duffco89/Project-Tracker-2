python manage.py loaddata --settings=main.settings.local auth > fixtures/users.json

python manage.py loaddata --settings=main.settings.local pjtk2.Employee > fixtures/employee.json

python manage.py loaddata --settings=main.settings.local pjtk2.Milestone > fixtures/milestones.json

python manage.py loaddata --settings=main.settings.local pjtk2.ProjectType > fixtures/projecttype.json

python manage.py loaddata --settings=main.settings.local pjtk2.Database > fixtures/database.json

python manage.py loaddata --settings=main.settings.local pjtk2.Lake > fixtures/lake.json

python manage.py loaddata --settings=main.settings.local pjtk2.Project > fixtures/project.json

python manage.py loaddata --settings=main.settings.local pjtk2.ProjectMilestones > fixtures/projectmilestones.json

