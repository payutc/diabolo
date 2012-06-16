# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('diabolo_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('badge_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal('diabolo', ['UserProfile'])

        # Adding model 'Famille'
        db.create_table('diabolo_famille', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('alcool', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('diabolo', ['Famille'])

        # Adding model 'Asso'
        db.create_table('diabolo_asso', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('diabolo', ['Asso'])

        # Adding M2M table for field sellers on 'Asso'
        db.create_table('diabolo_asso_sellers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('asso', models.ForeignKey(orm['diabolo.asso'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('diabolo_asso_sellers', ['asso_id', 'user_id'])

        # Adding model 'Article'
        db.create_table('diabolo_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('famille', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Famille', to=orm['diabolo.Famille'])),
            ('asso', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Association', to=orm['diabolo.Asso'])),
            ('stockinitial', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('stock', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('enVente', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('diabolo', ['Article'])

        # Adding model 'PointOfSale'
        db.create_table('diabolo_pointofsale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('MustCheckSeller', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('diabolo', ['PointOfSale'])

        # Adding model 'ArticlePos'
        db.create_table('diabolo_articlepos', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Article', to=orm['diabolo.Article'])),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('pos', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Point de vente', to=orm['diabolo.PointOfSale'])),
            ('debut', self.gf('django.db.models.fields.TimeField')()),
            ('fin', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('diabolo', ['ArticlePos'])

        # Adding model 'Groupe'
        db.create_table('diabolo_groupe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('diabolo', ['Groupe'])

        # Adding model 'Reversement'
        db.create_table('diabolo_reversement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('montant', self.gf('django.db.models.fields.IntegerField')()),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('diabolo', ['Reversement'])

        # Adding model 'Transaction'
        db.create_table('diabolo_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diabolo.Article'])),
            ('seller', self.gf('django.db.models.fields.related.ForeignKey')(related_name='seller', to=orm['auth.User'])),
            ('buyer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='buyer', to=orm['auth.User'])),
            ('pos', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pos', to=orm['diabolo.PointOfSale'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('diabolo', ['Transaction'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table('diabolo_userprofile')

        # Deleting model 'Famille'
        db.delete_table('diabolo_famille')

        # Deleting model 'Asso'
        db.delete_table('diabolo_asso')

        # Removing M2M table for field sellers on 'Asso'
        db.delete_table('diabolo_asso_sellers')

        # Deleting model 'Article'
        db.delete_table('diabolo_article')

        # Deleting model 'PointOfSale'
        db.delete_table('diabolo_pointofsale')

        # Deleting model 'ArticlePos'
        db.delete_table('diabolo_articlepos')

        # Deleting model 'Groupe'
        db.delete_table('diabolo_groupe')

        # Deleting model 'Reversement'
        db.delete_table('diabolo_reversement')

        # Deleting model 'Transaction'
        db.delete_table('diabolo_transaction')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'diabolo.article': {
            'Meta': {'object_name': 'Article'},
            'asso': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Association'", 'to': "orm['diabolo.Asso']"}),
            'enVente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'famille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Famille'", 'to': "orm['diabolo.Famille']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'stock': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'stockinitial': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'diabolo.articlepos': {
            'Meta': {'object_name': 'ArticlePos'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Article'", 'to': "orm['diabolo.Article']"}),
            'debut': ('django.db.models.fields.TimeField', [], {}),
            'fin': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Point de vente'", 'to': "orm['diabolo.PointOfSale']"}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        'diabolo.asso': {
            'Meta': {'object_name': 'Asso'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sellers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'diabolo.famille': {
            'Meta': {'object_name': 'Famille'},
            'alcool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'diabolo.groupe': {
            'Meta': {'object_name': 'Groupe'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'diabolo.pointofsale': {
            'Meta': {'object_name': 'PointOfSale'},
            'MustCheckSeller': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'diabolo.reversement': {
            'Meta': {'object_name': 'Reversement'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': ('django.db.models.fields.IntegerField', [], {}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'diabolo.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['diabolo.Article']"}),
            'buyer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'buyer'", 'to': "orm['auth.User']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pos'", 'to': "orm['diabolo.PointOfSale']"}),
            'seller': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'seller'", 'to': "orm['auth.User']"})
        },
        'diabolo.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'badge_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['diabolo']