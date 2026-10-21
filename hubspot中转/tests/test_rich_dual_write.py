"""Local contract tests; no model, database, or HubSpot calls."""

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gen_email as bridge
from upload_data import _validated_inputs


EVENT_TYPES = (
    'viewed_promotion_abandonment',
    'viewed_product_abandonment',
    'started_design_abandonment',
    'upload_artwork_abandonment',
)


class RichDualWriteTests(unittest.TestCase):
    def test_four_events_both_rounds_write_both_fields(self):
        for event_type in EVENT_TYPES:
            for round_number in (1, 2):
                with self.subTest(event_type=event_type, round_number=round_number):
                    body = ('Hi Li,\n\xa0\nSee <a href="https://example.com">the product</a>.\n'
                            'Best regards,\nMegan H\nCustomer Success Manager'
                            if event_type.startswith('viewed_') else
                            'Hi Li,\n\xa0\nA & B < C.\n\xa0\nBest regards,\nMegan H\nCustomer Success Manager')
                    contact = {'id': f'{event_type}-{round_number}',
                               'properties': {'last_behavioral_email_type': event_type,
                                              'n1v1_email_round': f'round_{round_number}'}}
                    response = {'code': 1, 'model_response': {
                        'email_subject': 'Subject', 'email_body': body}}
                    with patch.object(bridge.requests, 'post', return_value=Mock(json=lambda: response)):
                        result = bridge.gen_email([contact], max_workers=1)[0]

                    self.assertEqual(result['email_send'], 'Ready')
                    self.assertEqual(result['email_body'], body)
                    self.assertTrue(result['email_body_rich'].strip())
                    if event_type.startswith('viewed_'):
                        self.assertIn('<a href="https://example.com">', result['email_body_rich'])
                    else:
                        self.assertIn('A &amp; B &lt; C.', result['email_body_rich'])
                        self.assertIn('Best regards,<br>Megan H<br>Customer Success Manager',
                                      result['email_body_rich'])
                        self.assertIn('Hi Li,<br><br>A', result['email_body_rich'])

                    properties = _validated_inputs([result])[0]['properties']
                    self.assertEqual(properties['email_body'], body)
                    self.assertEqual(properties['email_body_rich'], result['email_body_rich'])

    def test_empty_body_cannot_be_ready(self):
        response = {'code': 1, 'model_response': {'email_subject': 'Subject', 'email_body': '  '}}
        contact = {'id': '1', 'properties': {'last_behavioral_email_type':
                                             'started_design_abandonment'}}
        with patch.object(bridge.requests, 'post', return_value=Mock(json=lambda: response)):
            result = bridge.gen_email([contact], max_workers=1)[0]
        self.assertEqual(result['email_send'], 'Pending')

    def test_missing_event_type_uses_product_fallback(self):
        body = 'Hi Li,\nSee <a href="https://example.com">the product</a>.'
        response = {'code': 1, 'model_response': {'email_subject': 'Subject',
                                                   'email_body': body}}
        contact = {'id': '1', 'properties': {'last_behavioral_email_type': None}}
        with patch.object(bridge.requests, 'post', return_value=Mock(json=lambda: response)):
            result = bridge.gen_email([contact], max_workers=1)[0]
        self.assertEqual(result['email_send'], 'Ready')
        self.assertIn('<a href="https://example.com">', result['email_body_rich'])

    def test_app_skips_only_records_missing_rich(self):
        save_module = types.ModuleType('save_to_db')
        save_module.save_to_db = lambda _: None
        tqdm_module = types.ModuleType('tqdm')
        tqdm_module.tqdm = lambda iterable, **_: iterable
        with patch.dict(sys.modules, {'save_to_db': save_module, 'tqdm': tqdm_module}):
            import app

        contacts = [
            {'id': '1', 'properties': {'last_behavioral_email_type': 'upload_artwork_abandonment'}},
            {'id': '2', 'properties': {'last_behavioral_email_type': 'viewed_product_abandonment'}},
        ]
        generated = [
            {'id': '1', 'email_send': 'Ready', 'email_subject': 'Subject', 'email_body': 'Body'},
            {'id': '2', 'email_send': 'Ready', 'email_subject': 'Subject', 'email_body': 'Body',
             'email_body_rich': '<p>OK</p>'},
        ]
        upload = Mock(return_value=[{'id': '2'}])
        with (patch.object(app, 'get_contacts_needing_email', return_value=contacts),
              patch.object(app, 'set_more_params', side_effect=lambda contacts: contacts),
              patch.object(app, 'gen_email', return_value=generated),
              patch.object(app, 'save_to_db'),
              patch.object(app, 'upload_contact_emails', upload)):
            result = app.run_email_generation(max_workers=1)

        self.assertTrue(result['success'])
        self.assertEqual(result['updated_count'], 1)
        upload.assert_called_once_with([generated[1]])


if __name__ == '__main__':
    unittest.main()
