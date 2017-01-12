# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import six
from collections import defaultdict
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.constants import NAMESPACES, Mimetypes


class TestMetadata(unittest.TestCase):
    def test_init(self):
        a = Metadata()
        self.assertTrue(hasattr(a, "metadata"), True)
        self.assertTrue(isinstance(a.metadata, defaultdict))

        a = Metadata(keys=["title"])
        self.assertEqual(
            a.keys(), ["title"], "Keys should be set"
        )

    def test_set(self):
        a = Metadata()
        a["title"] = [("eng", "Epigrams")]
        self.assertEqual(a["title"]["eng"], "Epigrams")
        self.assertEqual(
            a.keys(), ["title"], "Keys should be set"
        )
        a[("desc", "label")] = ([("eng", "desc")], [("eng", "lbl"), ("fre", "label")])
        self.assertEqual(a["desc"]["eng"], "desc")
        self.assertEqual(a["label"][("eng", "fre")], ("lbl", "label"))

    def test_get(self):
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a[("desc", "label")] = (m1, m2)
        self.assertEqual(a[("desc", "label")], (m1, m2))

        self.assertEqual(a[0], m1)
        with self.assertRaises(KeyError):
            z = a[2]
        with self.assertRaises(KeyError):
            z = a["textgroup"]

        with six.assertRaisesRegex(self, TypeError, "Only text_type or tuple instances are accepted as key"):
            a[3.5] = "test"
        with six.assertRaisesRegex(self, ValueError, "Less values than keys detected"):
            a[("lat", "grc")] = ["Epigrammata"]

    def test_iter(self):
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a["desc"] = m1
        a["label"] = m2

        i = 0
        d=[]
        d2=[]
        for k, v in a:
            d.append(k)
            d2.append(v)
            if i == 1:
                break
            i += 1
        self.assertEqual(d, ["desc", "label"])
        self.assertEqual(d2, [m1, m2])

        i = 0
        d=[]
        d2=[]
        for k, v in a:
            d.append(k)
            d2.append(v)
            break
        self.assertEqual(d, ["desc"])
        self.assertEqual(d2, [m1])

        self.assertEqual(list(a), [("desc", m1), ("label", m2)])

    def test_len(self):
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a["desc"] = m1
        self.assertEqual(len(a), 1)
        a["label"] = m2
        self.assertEqual(len(a), 2)
        a["z"] = 1.5
        self.assertEqual(len(a), 2)

    def test_add(self):
        """ Test sum of two Metadata objects  """
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a["desc"] = m1
        a["label"] = m2

        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Omelette")])
        m4 = Metadatum("title", [("eng", "ttl"), ("fre", "titre")])
        b[("desc", "title")] = (m3, m4)

        c = a + b
        self.assertEqual(len(c), 3)
        self.assertEqual(len(c["desc"]), 2)

    def test_export_json(self):
        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Omelette")])
        m4 = Metadatum("title", [("eng", "ttl"), ("fre", "titre")])
        m5 = Metadatum("dc:editor", [("eng", "Captain Hook"), ("fre", "Capitaine Crochet")])
        b[("desc", "title", "dc:editor")] = (m3, m4, m5)

        six.assertCountEqual(
            self,
            b.export(Mimetypes.JSON.Std),
            {'dc:editor': {'default': 'eng', 'langs': [('eng', 'Captain Hook'), ('fre', 'Capitaine Crochet')],
                           'name': 'dc:editor'},
             'title': {'default': 'eng', 'langs': [('eng', 'ttl'), ('fre', 'titre')], 'name': 'title'},
             'desc': {'default': 'fre', 'langs': [('fre', 'Omelette')], 'name': 'desc'}},
            "JSON LD Expression should take into account prefixes"
        )

    def test_export_jsonld_nons(self):
        """ With no namespace """
        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Un bon livre")])
        m4 = Metadatum("title", [("eng", "A title"), ("fre", "Un titre")])
        m5 = Metadatum("dc:editor", [("eng", "An Editor"), ("fre", "Un Editeur")])
        b[("desc", "title", "dc:editor")] = (m3, m4, m5)

        six.assertCountEqual(
            self,
            b.export(Mimetypes.JSON.DTS.Std),
            [
                {
                    'desc': 'Un bon livre',
                    'title': 'Un titre',
                    'http://purl.org/dc/elements/1.1/editor': "Un Editeur",
                    '@language': 'fre'
                },
                {
                    'title': 'A title',
                    'http://purl.org/dc/elements/1.1/editor': "An Editor",
                    '@language': 'eng'
                }
            ],
            "JSON LD Expression should take into account prefixes"
        )

    def test_export_jsonld_withns(self):
        """ With no namespace """
        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Un bon livre")], namespace=NAMESPACES.CTS)
        m4 = Metadatum("title", [("eng", "A title"), ("fre", "Un titre")], namespace=NAMESPACES.CTS)
        m5 = Metadatum("dc:editor", [("eng", "An Editor"), ("fre", "Un Editeur")])
        b[("desc", "title", "dc:editor")] = (m3, m4, m5)

        six.assertCountEqual(
            self,
            b.export(Mimetypes.JSON.DTS.Std),
            [
                {
                    'http://chs.harvard.edu/xmlns/cts/desc': 'Un bon livre',
                    'http://chs.harvard.edu/xmlns/cts/title': 'Un titre',
                    'http://purl.org/dc/elements/1.1/editor': "Un Editeur",
                    '@language': 'fre'
                },
                {
                    'http://chs.harvard.edu/xmlns/cts/title': 'A title',
                    'http://purl.org/dc/elements/1.1/editor': "An Editor",
                    '@language': 'eng'
                }
            ],
            "JSON LD Expression should take into account prefixes"
        )

    def test_export_xmlRDF_noNS(self):
        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Omelette")])
        m4 = Metadatum("title", [("eng", "ttl"), ("fre", "titre")])
        m5 = Metadatum("dc:editor", [("eng", "Captain Hook"), ("fre", "Capitaine Crochet")])
        b[("desc", "title", "dc:editor")] = (m3, m4, m5)
        self.assertEqual(
            b.export(Mimetypes.XML.RDF),
            """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description>
    <editor xmlns="http://purl.org/dc/elements/1.1/" xml:lang="eng">Captain Hook</editor><editor xmlns="http://purl.org/dc/elements/1.1/" xml:lang="fre">Capitaine Crochet</editor><desc xml:lang="fre">Omelette</desc><title xml:lang="eng">ttl</title><title xml:lang="fre">titre</title>
  </rdf:Description>
</rdf:RDF>""",
            "XML/RDF Expression should take into account prefixes"
        )

    def test_export_xmlRDF_withNs(self):
        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Omelette")], namespace=NAMESPACES.CTS)
        m4 = Metadatum("title", [("eng", "ttl"), ("fre", "titre")], namespace=NAMESPACES.CTS)
        m5 = Metadatum("dc:editor", [("eng", "Captain Hook"), ("fre", "Capitaine Crochet")])
        b[("desc", "title", "dc:editor")] = (m3, m4, m5)
        self.assertEqual(
            b.export(Mimetypes.XML.RDF),
            """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description>
    <editor xmlns="http://purl.org/dc/elements/1.1/" xml:lang="eng">Captain Hook</editor><editor xmlns="http://purl.org/dc/elements/1.1/" xml:lang="fre">Capitaine Crochet</editor><desc xmlns="http://chs.harvard.edu/xmlns/cts/" xml:lang="fre">Omelette</desc><title xmlns="http://chs.harvard.edu/xmlns/cts/" xml:lang="eng">ttl</title><title xmlns="http://chs.harvard.edu/xmlns/cts/" xml:lang="fre">titre</title>
  </rdf:Description>
</rdf:RDF>""",
            "XML/RDF Expression should take into account prefixes"
        )

