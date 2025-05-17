import uuid
from django.forms.models import model_to_dict
from django.db import models
from django.utils import timezone


class SoftDeletionManager(models.Manager):
    def get_queryset(self):
        """
        Return a queryset that filters out any deleted items.

        :param self: The instance of the class.
        :return: A queryset that filters out any deleted items.
        """
        return super().get_queryset().filter(is_deleted=False)

    def all_objects(self):
        """
        Returns all objects in the queryset.

        :param self: The instance of the class.
        :return: The queryset containing all objects.
        """
        return super().get_queryset()


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models.

    Fields:
    - id: Unique identifier for the model (UUIDField).
    - created_at: Date and time when the model was created (DateTimeField).
    - modified_at: Date and time when the model was last modified (DateTimeField).
    - is_deleted: Boolean indicating whether the model is deleted or not (BooleanField).
    """

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeletionManager()

    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class ModelDiffMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        """
        Calculates the differences between the initial state of the object and its current state.

        Returns:
            dict: A dictionary containing the differences between the initial state and the current state.
                The keys are the attributes that have changed, and the values are tuples containing
                the old and new values of each attribute.
        """
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        """
        Returns a boolean value indicating whether the object has changed or not.
        """
        return bool(self.diff)

    @property
    def changed_fields(self):
        """
        Returns a list of the keys of the dictionary `diff`, which represents the fields that have been changed in the object.

        :returns: A list of the keys of the changed fields.
        :rtype: list
        """
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        """
        Returns a dictionary representation of the object.

        :return: A dictionary containing the object's attributes.
        """
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])
