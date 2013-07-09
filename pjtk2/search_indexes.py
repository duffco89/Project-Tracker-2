import datetime
from haystack import indexes
from pjtk2.models import Project


class ProejctIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    #author = indexes.CharField(model_attr='user')
    #pub_date = indexes.DateTimeField(model_attr='EFFDT1')
    YEAR = indexes.CharField(model_attr='YEAR')
    code = indexes.CharField(model_attr='PRJ_CD')
    name = indexes.CharField(model_attr='PRJ_NM')
    description = indexes.CharField(model_attr='COMMENT')

    ##Database = indexes.CharField(model_attr='master_database')
    ProjectType = indexes.CharField(model_attr='ProjectType', faceted=True)
    ##
    #Approved = indexes.BooleanField(model_attr='Approved', faceted=True)
    #Completed = indexes.BooleanField(model_attr='SignOff', faceted=True)
    ##
    Lake = indexes.CharField(model_attr='Lake', faceted=True)
    Funding = indexes.CharField(model_attr='Funding', faceted=True)

    tags = indexes.MultiValueField()

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_model(self):
        return Project

    #def index_queryset(self, using=None):
    #    """Used when the entire index for model is updated."""
    #    return self.get_model().objects.all()


