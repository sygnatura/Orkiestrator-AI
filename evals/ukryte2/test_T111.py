from _wspolne import TestCli


class T111(TestCli):
    def test_tylko_dostepne(self):
        self.assertEqual([linia.split(']')[0] for linia in self.linie('lista', '--tylko-dostepne')],
                         ['[1', '[3', '[5', '[7', '[8'])
        self.assertNotIn('[wypożyczona]', '\n'.join(self.linie('lista', '--tylko-dostepne')))
