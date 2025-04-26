from mongoengine import Document, fields

class BaseDocument(Document):
    """Base class for all documents"""
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)

    meta = {
        'abstract': True,
        'ordering': ['-created_at']
    } 