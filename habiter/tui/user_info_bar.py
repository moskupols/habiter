import urwid


class UserInfoBar(urwid.Text):
    PARTS = (
        ('name',  '{u.name}'),
        ('level', '{s.level} level'),
        ('hp',    '{s.hp}/{s.max_hp} hp'),
        ('exp',   '{s.exp}/{s.max_exp} exp'),
        ('mp',    '{s.mp}/{s.max_mp} mp'),
        ('gold',  '{s.gold:.2f} gold'),
    )

    @classmethod
    def info_markup_for(cls, user):
        if not user.stats:
            return ''

        def intersperse(lst, sep):
            seps = [sep] * (len(lst) * 2 - 1)
            seps[0::2] = lst
            return seps

        markup = [(part, form.format(u=user, s=user.stats)) for part, form in cls.PARTS]
        markup = intersperse(markup, ', ')
        markup = ('info_bar', markup)
        return markup

    def __init__(self, user):
        super().__init__(self.info_markup_for(user), align=urwid.CENTER)
        self.user = user
        urwid.connect_signal(user, 'reset', self.on_user_reset)

    def on_user_reset(self):
        self.set_text(self.info_markup_for(self.user))
