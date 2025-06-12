from mvlocscript.xmltools import xpath

CUSTOM_FONT = {
    'fuel': '{',
    'droneparts': '|',
    'drones': '|',
    'missiles': '}',
    'scrap': '~',
    'repair': '$',
    'elite': '€',
    'fire': '‰',
    'power': '†',
    'cooldown': '‡',
    #'upgraded': '™'# Not supported in MV font?
}

class EventBaseClass():
    def __init__(self, element, priority) -> None:
        self._element = element
        self._priority = priority
        self._infoText = None
    
    @property
    def priority(self):
        return self._priority
    
    def setInfo(self):
        raise NotImplementedError
    
    def getInfo(self):
        self.setInfo()
        return self._infoText

def ajustText(text, use_custom_font = True):
    assert text is not None
    
    if use_custom_font:
        text = text.lower()
        for key, custom_font in CUSTOM_FONT.items():
            text = text.replace(key, custom_font)
    return text.replace('_', ' ').title()


#----------------------Evnets----------------------

class NameReturn():
    '''Contain fixed event'''
    def __init__(self, name, priority=1) -> None:
        self._priority = priority
        self._infoText = name
    
    @property
    def priority(self):
        return self._priority
    
    def getInfo(self):
        return '[NAME]storageCheck[/NAME]' + self._infoText
    
class TextReturn(EventBaseClass):
    '''A proxy of loadEvent and this deals with \<textReturn>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        self._infoText = self._element.text or None

class UnlockCustomShip(EventBaseClass):
    '''Deal with \<unlockCustomShip>.'''
    def __init__(self, element, priority=999) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        text = ajustText(self._element.text.replace('PLAYER_SHIP_', ''), False)
        self._infoText = f'[NAME]unlockCustomShip[/NAME][style[color:00FFFF]]<#>Unlock Ship({text})[[/style]]'

class RemoveCrew(EventBaseClass):
    '''Deal with \<removeCrew>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        clonetags = xpath(self._element, './clone')
        assert len(clonetags) == 1
        
        if clonetags[0].text == 'true':
            self._infoText = '[NAME]removeCrew[/NAME][style[color:E00000]]<!>Lose your crew([[/style]][style[color:700000]]clonable[[/style]][style[color:E00000]])[[/style]]'
        elif clonetags[0].text == 'false':
            self._infoText = '[NAME]removeCrew[/NAME][style[color:E00000]]<!>Lose your crew([[/style]][style[color:FF0000]]UNCLONABLE[[/style]][style[color:E00000]])[[/style]]'
        else:
            raise ValueError

class CrewMember(EventBaseClass):
    '''Deal with \<crewMember>. This shows crew gain info if "amount" is plus, otherwise crew loss(unclonable) info if "amount" is minus.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        amount = int(self._element.attrib['amount'])        
        if amount > 0:
            race = ajustText(self._element.get('class', 'Random').replace('LIST_CREW_', ''), False)
            self._infoText = f'[NAME]crewMember[/NAME][style[color:00E000]]Gain a crew({race})[[/style]]'
        elif amount < 0:
            self._infoText = '[NAME]removeCrew[/NAME][style[color:E00000]]<!>Lose your crew([[/style]][style[color:FF0000]]UNCLONABLE[[/style]][style[color:E00000]])[[/style]]'

class RevealMap(EventBaseClass):
    '''Deal with \<revealMap>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        self._infoText = '[NAME]revealMap[/NAME][style[color:00E000]]Map Reveal[[/style]]'

class AutoReward(EventBaseClass):
    '''Deal with \<autoReward>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        level = self._element.attrib['level'][0]
        stuff_type = ajustText(self._element.text)
        self._infoText = f'[NAME]autoReward[/NAME][style[color:00E000]]Reward {stuff_type}({level})[[/style]]'

class ItemModify(EventBaseClass):
    '''Deal with \<itemModify>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        itemtags = xpath(self._element, './item')
        assert len(itemtags) > 0
        
        itemlist = []
        for itemtag in itemtags:
            item = ajustText(itemtag.attrib['type'])
            amount_min = int(itemtag.attrib['min'])
            amount_max = int(itemtag.attrib['max'])
            
            if amount_min == amount_max:
                color = 'E00000' if amount_min < 0 else '00E000'
                itemlist.append(f'[style[color:{color}]]{item}{amount_min}[[/style]]')
            elif amount_max > amount_min:
                color = 'E00000' if amount_max < 0 else '00E000'
                itemlist.append(f'[style[color:{color}]]{amount_min}≤{item}≤{amount_max}[[/style]]')
            elif amount_max < amount_min and amount_max < 0 and amount_min < 0:
                itemlist.append(f'[style[color:E00000]]<!>{amount_max}≤{item}≤{amount_min}[[/style]]')
            else:
                raise ValueError
        self._infoText = '[NAME]itemModify[/NAME]' + ' '.join(itemlist)

class ModifyPursuit(EventBaseClass):
    '''Deal with \<modifyPursuit>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        amount = int(self._element.attrib['amount'])
        
        if amount < 0:
            self._infoText = f'[NAME]modifyPursuit[/NAME][style[color:00E000]]Fleet Delay({amount * -1})[[/style]]'
        elif amount > 0:
            self._infoText = f'[NAME]modifyPursuit[/NAME][style[color:E00000]]<!>Fleet Advance({amount})[[/style]]'
        else:
            raise ValueError

class Reward(EventBaseClass):
    '''Deal with \<weapon>, \<drone>, and \<augment>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        name = ajustText(self._element.attrib['name'], False)
        if self._element.tag[0] in ('a', 'e', 'i', 'o', 'u'):
            self._infoText = f'[NAME]{self._element.tag}[/NAME][style[color:00E000]]Gain an {self._element.tag}({name})[[/style]]'
        else:
            self._infoText = f'[NAME]{self._element.tag}[/NAME][style[color:00E000]]Gain a {self._element.tag}({name})[[/style]]'

class Damage(EventBaseClass):
    '''Deal with \<damage>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        amount = int(self._element.attrib['amount'])
        
        if amount < 0:
            self._infoText = f'[NAME]damage[/NAME][style[color:00E000]]Repair Hull({amount * -1}$)[[/style]]'
        elif amount > 0:
            self._infoText = f'[NAME]damage[/NAME][style[color:E00000]]<!>Damage Hull({amount})[[/style]]'
        else:
            # NOTE: there is a case where amount is 0 - example attrib of such tag: {'amount': '0', 'system': 'room', 'effect': 'breach'}
            pass

class Upgrade(EventBaseClass):
    '''Deal with \<upgrade>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        system = ajustText(self._element.attrib['system'])
        amount = self._element.attrib['amount']
        
        self._infoText = f'[NAME]upgrade[/NAME][style[color:00E000]]System Upgrade({system} x{amount})[[/style]]'

class Boarders(EventBaseClass):
    '''Deal with \<boarders>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        race = ajustText(self._element.get('class', '?').replace('LIST_CREW_', ''), False)
        amount = self._element.get('amount')
        if amount is not None:
            amount_min, amount_max = int(amount), int(amount)
        else:
            amount_min = int(self._element.attrib['min'])
            amount_max = int(self._element.attrib['max'])
        
        if amount_min == amount_max:
            self._infoText = f'[NAME]boarders[/NAME][style[color:E00000]]<!>Enemy Boarding(x{amount_min} {race})[[/style]]'
        elif amount_max > amount_min:
            self._infoText = f'[NAME]boarders[/NAME][style[color:E00000]]<!>Enemy Boarding(x{amount_min}-x{amount_max} {race})[[/style]]'
        else:
            raise ValueError

class Test(EventBaseClass):
    def __init__(self, element, priority) -> None:
        super().__init__(element, priority)


#not done(or not planned to implement): 'environment', 'recallBoarders', 'achievement', 'choiceRequiresCrew', 'instantEscape', 'win', 'lose', 'store'
EVENTCLASSMAP = {
    "textReturn": TextReturn,
    "unlockCustomShip": UnlockCustomShip,
    "removeCrew": RemoveCrew,
    "crewMember": CrewMember,
    "reveal_map": RevealMap,
    "autoReward": AutoReward,
    "item_modify": ItemModify,
    "modifyPursuit": ModifyPursuit,
    "weapon": Reward,
    "drone": Reward,
    "augment": Reward,
    "damage": Damage,
    "upgrade": Upgrade,
    "boarders": Boarders,
}