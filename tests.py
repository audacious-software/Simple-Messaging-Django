# pylint: disable=line-too-long

import six

from django.test import TestCase

from .utils import split_into_bundles, byte_len

if six.PY2:
    from io import open # pylint: disable=redefined-builtin

class LineSplittingTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None # pylint: disable=invalid-name

    def test_line_splitting(self):
        with open('simple_messaging/testing/test_line_splitting/long_message.txt', encoding='utf-8') as long_message:
            long_message_txt = long_message.read()

            normalized_text = six.ensure_str(long_message_txt, encoding='utf-8')

            self.assertEqual(byte_len(long_message_txt), byte_len(normalized_text))

            bundles = split_into_bundles(long_message_txt, bundle_size=1000)

            self.assertEqual(bundles, [
                "Safety Plan:\nWarning Signs: \n#1: Feeling like I don't want to talk to anyone\n#2: Feeling overwhelmingly angry\n#3: Thinking about ways to die\n#4: Being irritated with everything and everyone\n#5: Doomscrolling\n#6: Not responding to texts",
                "Coping Skills: \n#1: Listening to calm music\n#2: Cooking a complex meal\n#3: Til\n#4: Listening to music. Calm piano music\n#5: Visit the Live Through This website: https://livethroughthis.org/filter-stories/\n#6: Visit The Mighty: https://themighty.com/topic/suicide/collections/\n#7: YouTube\n#8: Folding laundry\n#9: Play cards",
                "People I Can Call for a Distraction: \n1. Aaron - 999-999-9999\n2. Josh - \"Hey, could use some help now. Got a minute?\"\n3. Nate -999-999-9999\n4. Elan -- 999-999-9999 - \"Hey Elan, got a sec -- I could use a bit of help when you have the time.\"\n5. Zev -222-222-2222 - \"Hey Zev, can you help me out with a distraction right now? Just need to take my mind off things for a bit.\"\n\nA message you can send to any of them: \"Hey, mind talking for a few? I just need a distraction.\"",
                "People I Can Call for Help: \n1. Nate -- 999-999-9999 - \"Hey, I'm going through a tough time right now, and it would help to just talk to someone I trust. Could you give me a call?\"\n2. Josh\n3. Aaron -- 999-999-9999 - \"Hey -- can you give me a call --I need a little help.\"",
                "Health Providers I Can Call: \n1. Goodenow - not sure the number - \"\"I sometimes have suicidal thoughts or feelings that I want to die. I've been thinking about getting some professional help. Just so you know, I'm okay right now and not in crisis. I haven\u2019t tried any kind of treatment yet, but I was thinking about seeing a therapist. Is that something you can help me with?\"\"",
                "Crisis Resources: \n#1: Warmline (Non-Crisis Support) - NoneFor non-crisis support, warmlines are available. Find your local warmline, or a warmline that accepts out of state calls: https://warmline.org/warmdir.html ",
                "Ways I Can Make My Environment Safer: \n#1: Places to make safer: Home and my car\n#2: The park\n#3: Ways of creating time/space: Asking my wife to hold my meds\n#4: Places I can go: The mall\n#5: Give stuff to my neighbors\n#6: Places to make safer: My room\n#7: Ways of creating time/space: Get rid of my meds\n#8: Places I can go: Starbies\n#9: Other ways to make my environment safer: Ask Nataly to take meds and store them in a locked box she controls.\n\n"
              ])
