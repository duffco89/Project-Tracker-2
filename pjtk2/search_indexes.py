import datetime
from haystack import indexes
from pjtk2.models import Project


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    #author = indexes.CharField(model_attr='user')
    #pub_date = indexes.DateTimeField(model_attr='EFFDT1')
    year = indexes.CharField(model_attr='year')
    code = indexes.CharField(model_attr='prj_cd')
    name = indexes.CharField(model_attr='prj_nm')
    description = indexes.CharField(model_attr='comment')

    ##Database = indexes.CharField(model_attr='master_database')
    project_type = indexes.CharField(model_attr='project_type', faceted=True)
    ##
    #Approved = indexes.BooleanField(model_attr='Approved', faceted=True)
    #Completed = indexes.BooleanField(model_attr='SignOff', faceted=True)
    ##
    lake = indexes.CharField(model_attr='lake', faceted=True)
    funding = indexes.CharField(model_attr='funding', faceted=True)

    tags = indexes.MultiValueField()

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_model(self):
        return Project

    #def index_queryset(self, using=None):
    #    """Used when the entire index for model is updated."""
    #    return self.get_model().objects.all()


